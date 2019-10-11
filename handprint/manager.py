'''
manager.py: main loop for Handprint

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018-2019 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from   collections import namedtuple
from   concurrent.futures import ThreadPoolExecutor
import humanize
import io
from   itertools import repeat
import json
import math
import os
from   os import path
import shutil
from   stringdist import levenshtein
import sys
from   threading import Thread
import time
from   timeit import default_timer as timer
import urllib

import handprint
from handprint import _OUTPUT_EXT, _OUTPUT_FORMAT
from handprint.annotate import annotated_image
from handprint.debug import log
from handprint.exceptions import *
from handprint.files import converted_image, image_size, image_dimensions
from handprint.files import reduced_image_size, reduced_image_dimensions
from handprint.files import filename_basename, filename_extension, relative
from handprint.files import files_in_directory, alt_extension, handprint_path
from handprint.files import readable, writable, is_url, create_image_grid
from handprint.files import delete_existing
from handprint.messages import styled
from handprint.network import network_available, download_file, disable_ssl_cert_check
from handprint.services import KNOWN_SERVICES


# Helper data types.
# -----------------------------------------------------------------------------

Input = namedtuple('Input', 'item_source item_format item_file file dest_dir temp_files')
Input.__doc__ = '''Input and related materials for a file sent to a service
  'item_source' is the original source, which may be a URL or a file
  'item_format' is the data or file format of the original source
  'item_file' is the file we create to store the source content
  'file' is item_file after applying reductions
  'dest_dir' is the directory where normalized_file was written
  'temp_files' is a list of temporary files generated when creating normalized_file
'''

Result = namedtuple('Result', 'service original annotated report')
Result.__doc__ = '''Results from calling an HTR service on an input.
  'service' is the service used
  'original' is the original input image sent to the service
  'annotated' is the annotated image file we create from the service output
  'report' is a TSV file, the result of comparing the text to the ground truth
'''


# Main class.
# -----------------------------------------------------------------------------

class Manager:
    def __init__(self, service_names, num_threads, output_dir, make_grid,
                 compare, extended, say):
        '''Initialize manager for services.  This will also initialize the
        credentials for individual services.
        '''
        self._num_threads = num_threads
        self._extended_results = extended
        self._compare = compare
        self._output_dir = output_dir
        self._make_grid = make_grid
        self._say = say

        self._services = []
        for service_name in service_names:
            service = KNOWN_SERVICES[service_name]()
            service.init_credentials()
            self._services.append(service)

        # In order to make the results comparable, we resize all the images
        # to the smallest size accepted by any of the services we will run.
        self._max_size = None
        self._max_dimensions = None
        for service in self._services:
            if service.max_size():
                if self._max_size:
                    self._max_size = min(self._max_size, service.max_size())
                else:
                    self._max_size = service.max_size()
            if service.max_dimensions():
                if self._max_dimensions:
                    (max_width, max_height) = self._max_dimensions
                    service_max = service.max_dimensions()
                    self._max_dimensions = (min(max_width, service_max[0]),
                                            min(max_height, service_max[1]))
                else:
                    self._max_dimensions = service.max_dimensions()
        if __debug__: log('max_size = {}', self._max_size)
        if __debug__: log('max_dimensions = {}', self._max_dimensions)


    def run_services(self, item, index, base_name):
        '''Run all requested services on the image indicated by "item", using
        "index" and "base_name" to construct a download copy of the item if
        it has to be downloaded from a URL first.
        '''
        # Shortcuts to make the code more readable.
        services = self._services
        say = self._say
        use_color = say.use_color()

        say.info('Starting on {}'.format(styled(item, 'white') if use_color else item))
        try:
            (item_file, item_fmt) = self._get(item, base_name, index)
            if not item_file:
                return

            dest_dir = self._output_dir if self._output_dir else path.dirname(item_file)
            if not writable(dest_dir):
                say.error('Cannot write output in {}.'.format(dest_dir))
                return

            # Normalize input image to the lowest common denominator.
            page = self._normalized(item, item_fmt, item_file, dest_dir)
            if not page.file:
                say.warn('Skipping {}'.format(relative(item_file)))
                return

            # Send the file to the services and get Result tuples back.
            if self._num_threads == 1:
                # For 1 thread, avoid thread pool to make debugging easier.
                results = [self._send(page, s) for s in services]
            else:
                with ThreadPoolExecutor(max_workers = self._num_threads) as tpe:
                    results = list(tpe.map(self._send, repeat(page), iter(services)))

            # If a service failed for some reason (e.g., a network glitch), we
            # get no result back.  Remove empty results & go on with the rest.
            results = [x for x in results if x is not None]

            # Create grid file if requested.
            if self._make_grid:
                base = path.basename(filename_basename(item_file))
                grid_file = path.realpath(path.join(dest_dir, base + '.all-results.png'))
                say.info('Creating results grid image: {}'.format(relative(grid_file)))
                images = [r.annotated for r in results]
                width = math.ceil(math.sqrt(len(images)))
                create_image_grid(images, grid_file, max_horizontal = width)

            # Clean up after ourselves.
            if not self._extended_results:
                for file in set(page.temp_files | {r.annotated for r in results}):
                    if file and path.exists(file):
                        delete_existing(file)

            say.info('Done with {}'.format(relative(item)))
        except (KeyboardInterrupt, UserCancelled) as ex:
            say.warn('Interrupted')
            raise
        except Exception as ex:
            say.error('Stopping due to a problem')
            raise


    def _get(self, item, base_name, index):
        # Shortcuts to make the code more readable.
        output_dir = self._output_dir
        say = self._say

        # For URLs, we download the corresponding files and name them with
        # the base_name.
        if is_url(item):
            # First make sure the URL actually points to an image.
            if __debug__: log('testing if URL contains an image: {}', item)
            try:
                response = urllib.request.urlopen(item)
            except Exception as ex:
                say.warn('Skipping URL due to error: {}'.format(ex))
                return (None, None)
            if response.headers.get_content_maintype() != 'image':
                say.warn('Did not find an image at {}'.format(item))
                return (None, None)
            orig_fmt = response.headers.get_content_subtype()
            base = '{}-{}'.format(base_name, index)
            # If we weren't given an output dir, then for URLs, we have no
            # choice but to use the current dir to download the file.
            # Important: don't change self._output_dir because if other
            # inputs *are* files, then those files will need other output dirs.
            if not output_dir:
                output_dir = os.getcwd()
            file = path.realpath(path.join(output_dir, base + '.' + orig_fmt))
            if not download_file(item, file, say):
                say.warn('Unable to download {}'.format(item))
                return (None, None)
            url_file = path.realpath(path.join(output_dir, base + '.url'))
            with open(url_file, 'w') as f:
                f.write(url_file_content(item))
                say.info('Wrote URL to {}'.format(relative(url_file)))
        else:
            file = path.realpath(path.join(os.getcwd(), item))
            orig_fmt = filename_extension(file)[1:]

        if not path.getsize(file) > 0:
            say.warn('File has zero length: {}'.format(relative(file)))
            return (None, None)

        if __debug__: log('{} has original format {}', relative(file), orig_fmt)
        return (file, orig_fmt)


    def _send(self, image, service):
        '''Send the "image" to the service named "service" and write output in
        directory "dest_dir".
        '''
        say = self._say
        use_color = say.use_color()
        color = service.name_color()
        service_name = styled(service.name(), color) if use_color else service.name()

        say.info('Sending to {} and waiting for response ...'.format(service_name))
        last_time = timer()
        try:
            output = service.result(image.file)
        except AuthFailure as ex:
            raise AuthFailure('Unable to use {}: {}'.format(service, ex))
        except RateLimitExceeded as ex:
            time_passed = timer() - last_time
            if time_passed < 1/service.max_rate():
                say.warn('Pausing {} due to rate limits'.format(service_name))
                time.sleep(1/service.max_rate() - time_passed)
                # FIXME resend after pause
        if output.error:
            say.error('{} failed: {}'.format(service_name, output.error))
            say.warn('No result from {} for {}'.format(service_name, relative(image.file)))
            return None

        say.info('Got result from {}.'.format(service_name))
        file_name   = path.basename(image.file)
        base_path   = path.join(image.dest_dir, file_name)
        annot_path  = None
        report_path = None
        if self._make_grid:
            annot_path  = alt_extension(base_path, str(service) + '.png')
            say.info('Creating annotated image for {}.'.format(service_name))
            self._save_output(annotated_image(image.file, output.boxes, service), annot_path)
        if self._extended_results:
            txt_file  = alt_extension(base_path, str(service) + '.txt')
            json_file = alt_extension(base_path, str(service) + '.json')
            say.info('Saving all data for {}.'.format(service_name))
            self._save_output(json.dumps(output.data), json_file)
            say.info('Saving extracted text for {}.'.format(service_name))
            self._save_output(output.text, txt_file)
        if self._compare:
            gt_file = alt_extension(image.item_file, 'gt.txt')
            report_path = alt_extension(image.item_file, str(service) + '.tsv')
            if readable(gt_file):
                say.info('Saving {} comparison to ground truth'.format(service_name))
                self._save_output(self._error_report(output.text, gt_file), report_path)
            else:
                say.info('Skipping {} comparison because {} not available'.format(
                    service_name, relative(gt_file)))
        return Result(service, image, annot_path, report_path)


    def _normalized(self, orig_item, orig_fmt, item_file, dest_dir):
        '''Normalize images to same format and max size.'''
        # All services accept PNG, so normalize files to PNG.
        to_delete = set()
        file = item_file
        if orig_fmt != _OUTPUT_FORMAT:
            new_file = self._converted_file(file, _OUTPUT_FORMAT, dest_dir)
            if new_file and path.basename(new_file) != path.basename(file):
                to_delete.add(new_file)
            file = new_file
        # Resize if either size or dimensions are larger than accepted
        if file and self._max_size and self._max_size < image_size(file):
            new_file = self._smaller_file(file)
            if new_file and  path.basename(new_file) != path.basename(file):
                to_delete.add(new_file)
            file = new_file
        if file and self._max_dimensions:
            (image_width, image_height) = image_dimensions(file)
            (max_width, max_height) = self._max_dimensions
            if max_width < image_width or max_height < image_height:
                new_file = self._resized_image(file)
                if new_file and path.basename(new_file) != path.basename(file):
                    to_delete.add(new_file)
                file = new_file
        return Input(orig_item, orig_fmt, item_file, file, dest_dir, to_delete)


    def _converted_file(self, file, to_format, dest_dir):
        basename = path.basename(filename_basename(file))
        new_file = path.join(dest_dir, basename + '.' + to_format)
        say = self._say
        if path.exists(new_file):
            say.info('Using already converted image in {}'.format(relative(new_file)))
            return new_file
        else:
            say.info('Converting to {} format: {}'.format(to_format, relative(file)))
            (converted, error) = converted_image(file, to_format, new_file)
            if error:
                say.error('Failed to convert {}: {}'.format(relative(file), error))
                return None
            return converted


    def _smaller_file(self, file):
        if not file:
            return None
        say = self._say
        file_ext = filename_extension(file)
        if file.find('-reduced') > 0:
            new_file = file
        else:
            new_file = filename_basename(file) + '-reduced' + file_ext
        if path.exists(new_file):
            if image_size(new_file) < self._max_size:
                say.info('Reusing resized image found in {}'.format(relative(new_file)))
                return new_file
            else:
                # We found a "-reduced" file, perhaps from a previous run, but
                # for the current set of services, it's larger than allowed.
                if __debug__: log('existing resized file larger than {}b: {}',
                                  humanize.intcomma(self._max_size), new_file)
        say.info('Size too large; reducing size: {}'.format(relative(file)))
        (resized, error) = reduced_image_size(file, new_file, self._max_size)
        if error:
            say.error('Failed to resize {}: {}'.format(relative(file), error))
            return None
        return resized


    def _resized_image(self, file):
        (max_width, max_height) = self._max_dimensions
        file_ext = filename_extension(file)
        say = self._say
        if file.find('-reduced') > 0:
            new_file = file
        else:
            new_file = filename_basename(file) + '-reduced' + file_ext
        if path.exists(new_file) and readable(new_file):
            (image_width, image_height) = image_dimensions(new_file)
            if image_width < max_width and image_height < max_height:
                say.info('Using reduced image found in {}'.format(relative(new_file)))
                return new_file
            else:
                # We found a "-reduced" file, perhaps from a previous run, but
                # for the current set of services, dimension are too large.
                if __debug__: log('existing resized file larger than {}x{}: {}',
                                  max_width, max_height, new_file)
        say.info('Dimensions too large; reducing dimensions: {}'.format(relative(file)))
        (resized, error) = reduced_image_dimensions(file, new_file, max_width, max_height)
        if error:
            say.error('Failed to re-dimension {}: {}'.format(relative(file), error))
            return None
        return resized


    def _error_report(self, result_text, gt_file):
        say = self._say

        if __debug__: log('reading gt file {}', gt_file)
        gt_lines = []
        with open(gt_file, 'r') as f:
            gt_lines = f.read().splitlines()
        if len(gt_lines) == 0:
            say.warn('Empty ground truth file: {}'.format(gt_file))
            return None

        # We return data in tab-delimited format.
        output = ['# errors\tCER (%)\tExpected text\tActual text']
        result_lines = result_text.splitlines()
        total_errors = 0
        for expected, obtained in zip(gt_lines, result_lines):
            # The stringdist package definition of levenshtein_norm() divides
            # by the longest of the two strings, but it is more conventional in
            # OCR papers and software to divide by the length of the reference.
            lev = levenshtein(expected, obtained)
            if len(expected) > 0:
                cer = '{:.2f}'.format(100 * float(lev)/len(expected))
            else:
                cer = 'n/a'
            output.append('{}\t{}\t{}\t{}'.format(lev, cer, expected, obtained))
            total_errors += lev
        output.append('Total # errors')
        output.append(str(total_errors))
        return '\n'.join(output)


    def _save_output(self, result, file):
        say = self._say

        # First perform some sanity checks.
        if result is None:
            say.warn('No data for {}'.format(file))
            return
        if isinstance(result, tuple):
            # Assumes 2 elements: data, and error
            (data, error) = result
            if error:
                say.error('Error: {}'.format(error))
                say.warn('Unable to write {}'.format(file))
                return
            else:
                result = data

        if __debug__: log('writing output to file {}', relative(file))
        if isinstance(result, str):
            with open(file, 'w') as f:
                f.write(result)
        elif isinstance(result, io.BytesIO):
            with open(file, 'wb') as f:
                shutil.copyfileobj(result, f)
        else:
            # There's no other type in the code, so if we get here ...
            raise InternalError('Unexpected data in save_output() -- please report this.')


# Helper functions.
# ......................................................................

def url_file_content(url):
    return '[InternetShortcut]\nURL={}\n'.format(url)
