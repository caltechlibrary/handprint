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

from   concurrent.futures import ThreadPoolExecutor
import humanize
import io
from   itertools import repeat
import json
import os
from   os import path
import shutil
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


# Main class.
# -----------------------------------------------------------------------------

class Manager:
    def __init__(self, service_names, num_threads, output_dir, make_grid, extended, say):
        '''Initialize manager for services.  This will also initialize the
        credentials for individual services.
        '''
        self._num_threads = num_threads
        self._extended_results = extended
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
            # Only consider those services that do indicate maxima.
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
        output_dir = self._output_dir
        say = self._say

        try:
            say.info('Starting on {}'.format(
                styled(item, 'white') if say.use_color() else item))

            (file, orig_fmt) = self._get(item, base_name, index)
            if not file:
                return

            dest_dir = output_dir if output_dir else path.dirname(file)
            if not writable(dest_dir):
                say.error('Cannot write output in {}.'.format(dest_dir))
                return

            # Sanity check
            if not path.getsize(file) > 0:
                say.warn('Skipping zero-length file {}'.format(relative(file)))
                return

            # Save grid file name now, because it's based on the original file.
            basename = path.basename(filename_basename(file))
            grid_file = path.realpath(path.join(dest_dir, basename + '.all-results.png'))

            # We will usually delete temporary files we create.
            to_delete = set()

            # Normalize to the lowest common denominator.
            (new_file, intermediate_files) = self._normalized(file, orig_fmt, dest_dir)
            if not new_file:
                say.warn('Skipping {}'.format(relative(file)))
                return
            file = new_file
            if intermediate_files:
                to_delete.update(intermediate_files)

            # Send the file to the services.  If the number of threads is set
            # to 1, we force non-thread-pool execution to make debugging easier.
            results = []
            if self._num_threads == 1:
                results = [self._send(file, s, dest_dir) for s in services]
            else:
                with ThreadPoolExecutor(max_workers = self._num_threads) as executor:
                    results = list(executor.map(self._send, repeat(file),
                                                iter(services), repeat(dest_dir)))

            # If a service failed for some reason (e.g., a network glitch), we
            # get no result back.  Remove empty results & go on with the rest.
            results = [x for x in results if x is not None]
            to_delete.update(results)

            # Create grid file if requested.
            if self._make_grid:
                say.info('Creating results grid image: {}'.format(relative(grid_file)))
                create_image_grid(results, grid_file, max_horizontal = 2)

            # Clean up after ourselves.
            if self._make_grid and not self._extended_results:
                for image_file in to_delete:
                    delete_existing(image_file)

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

        if __debug__: log('{} has original format {}', relative(file), orig_fmt)
        return (file, orig_fmt)


    def _send(self, file, service, dest_dir):
        '''Send the "file" to the service named "service" and write output in
        directory "dest_dir".
        '''
        say = self._say
        use_color = say.use_color()
        color = service.name_color()
        service_name = styled(service.name(), color) if use_color else service.name()

        say.info('Sending to {} and waiting for response ...'.format(service_name))
        last_time = timer()
        try:
            result = service.result(file)
        except AuthFailure as ex:
            raise AuthFailure('Unable to use {}: {}'.format(service, ex))
        except RateLimitExceeded as ex:
            time_passed = timer() - last_time
            if time_passed < 1/service.max_rate():
                say.warn('Pausing {} due to rate limits'.format(service_name))
                time.sleep(1/service.max_rate() - time_passed)
                # FIXME resend after pause
        if result.error:
            say.error('{} failed: {}'.format(service_name, result.error))
            say.warn('No result from {} for {}'.format(service_name, relative(file)))
            return None

        say.info('Got result from {}.'.format(service_name))
        file_name  = path.basename(file)
        base_path  = path.join(dest_dir, file_name)
        annot_path = alt_extension(base_path, str(service) + '.png')
        say.info('Creating annotated image for {}.'.format(service_name))
        self._save_output(annotated_image(file, result.boxes, service), annot_path)
        if self._extended_results:
            txt_file  = alt_extension(base_path, str(service) + '.txt')
            json_file = alt_extension(base_path, str(service) + '.json')
            say.info('Saving all data for {}.'.format(service_name))
            self._save_output(json.dumps(result.data), json_file)
            say.info('Saving extracted text for {}.'.format(service_name))
            self._save_output(result.text, txt_file)

        # Return the annotated image file b/c we use it for the summary grid.
        return annot_path


    def _normalized(self, file, fmt, dest_dir):
        '''Normalize images to same format and max size.'''
        # All services accept PNG, so normalize files to PNG.
        to_delete = set()
        if fmt != _OUTPUT_FORMAT:
            new_file = self._converted_file(file, _OUTPUT_FORMAT, dest_dir)
            if path.basename(new_file) != path.basename(file):
                to_delete.add(new_file)
            file = new_file
        # Resize if either size or dimensions are larger than accepted
        if file and self._max_size and self._max_size < image_size(file):
            new_file = self._smaller_file(file)
            if path.basename(new_file) != path.basename(file):
                to_delete.add(new_file)
            file = new_file
        if file and self._max_dimensions:
            (image_width, image_height) = image_dimensions(file)
            (max_width, max_height) = self._max_dimensions
            if max_width < image_width or max_height < image_height:
                new_file = self._resized_image(file)
                if path.basename(new_file) != path.basename(file):
                    to_delete.add(new_file)
                file = new_file
        return (file, to_delete)


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
