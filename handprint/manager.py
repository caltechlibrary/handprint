'''
manager.py: main loop for Handprint

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018-2020 by the California Institute of Technology.  This code
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
import signal
import sys
import threading
from   threading import Thread, Lock
from   timeit import default_timer as timer
import urllib

if __debug__:
    from sidetrack import set_debug, log, logr

import handprint
from handprint import _OUTPUT_EXT, _OUTPUT_FORMAT
from handprint.comparison import text_comparison
from handprint.exceptions import *
from handprint.files import filename_basename, filename_extension, relative
from handprint.files import files_in_directory, alt_extension, handprint_path
from handprint.files import readable, writable, nonempty, is_url
from handprint.files import delete_existing
from handprint.images import converted_image, annotated_image, create_image_grid
from handprint.images import image_size, image_dimensions
from handprint.images import reduced_image_size, reduced_image_dimensions
from handprint.interruptions import interrupt, raise_for_interrupts
from handprint.network import network_available, download_file, disable_ssl_cert_check
from handprint.services import KNOWN_SERVICES
from handprint.ui import inform, alert, warn


# Helper data types.
# .............................................................................

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
# .............................................................................

class Manager:
    '''Manage invocation of services and creation of outputs.'''

    def __init__(self, service_names, num_threads, output_dir, make_grid,
                 compare, extended):
        '''Initialize manager for services.  This will also initialize the
        credentials for individual services.
        '''
        self._num_threads = num_threads
        self._extended_results = extended
        self._compare = compare
        self._output_dir = output_dir
        self._make_grid = make_grid

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
        if __debug__: log(f'max_size = {self._max_size}')
        if __debug__: log(f'max_dimensions = {self._max_dimensions}')

        # An unfortunate feature of Python's thread handling is that threads
        # don't get interrupt signals: if the user hits ^C, the parent thread
        # has to do something to interrupt the child threads deliberately.
        # We can't do that unless we keep a pointer to the futures/subthreads.
        self._senders = []


    def run_services(self, item, index, base_name):
        '''Run all requested services on the image indicated by "item", using
        "index" and "base_name" to construct a download copy of the item if
        it has to be downloaded from a URL first.
        '''
        # Shortcuts to make the code more readable.
        services = self._services

        inform(f'Starting on [white]{item}[/]')
        (item_file, item_fmt) = self._get(item, base_name, index)
        if not item_file:
            return

        dest_dir = self._output_dir if self._output_dir else path.dirname(item_file)
        if not writable(dest_dir):
            alert(f'Cannot write output in {dest_dir}.')
            return

        # Normalize input image to the lowest common denominator.
        image = self._normalized(item, item_fmt, item_file, dest_dir)
        if not image.file:
            warn(f'Skipping {relative(item_file)}')
            return

        # Send the file to the services and get Result tuples back.
        self._senders = []
        if self._num_threads == 1:
            # For 1 thread, avoid thread pool to make debugging easier.
            results = [self._send(image, s) for s in services]
        else:
            executor = ThreadPoolExecutor(max_workers = self._num_threads,
                                          thread_name_prefix = 'ServiceThread')
            for service in services:
                future = executor.submit(self._send, image, service)
                self._senders.append(future)
            results = [future.result() for future in self._senders]

        # If a service failed for some reason (e.g., a network glitch), we
        # get no result back.  Remove empty results & go on with the rest.
        results = [x for x in results if x is not None]
        if not results:
            warn(f'Nothing to do for {item}')
            return

        # Create grid file if requested.
        if self._make_grid:
            base = path.basename(filename_basename(item_file))
            grid_file = path.realpath(path.join(dest_dir, base + '.handprint-all.png'))
            inform(f'Creating results grid image: {relative(grid_file)}')
            all_results = [r.annotated for r in results]
            width = math.ceil(math.sqrt(len(all_results)))
            create_image_grid(all_results, grid_file, max_horizontal = width)

        # Clean up after ourselves.
        if not self._extended_results:
            for file in set(image.temp_files | {r.annotated for r in results}):
                if file and path.exists(file):
                    delete_existing(file)

        inform(f'Done with {relative(item)}')


    def stop_services(self):
        if __debug__: log('stopping sender threads')
        # Doing cancel on the threads will not do anything if they are still
        # running.  However, we should still do it.
        for s in self._senders:
            if s.cancel():
                if __debug__: log(f'succeeded in cancelling {s}')
            else:
                if __debug__: log(f'unable to cancel {s}')


    def _get(self, item, base_name, index):
        # Shortcuts to make the code more readable.
        output_dir = self._output_dir

        # For URLs, we download the corresponding files and name them with
        # the base_name.
        if is_url(item):
            # First make sure the URL actually points to an image.
            if __debug__: log(f'testing if URL contains an image: {item}')
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'}
            try:
                request = urllib.request.Request(item, None, headers)
                response = urllib.request.urlopen(request)
            except Exception as ex:
                warn(f'Skipping URL due to error: {ex}')
                return (None, None)
            if response.headers.get_content_maintype() != 'image':
                warn(f'Did not find an image at {item}')
                return (None, None)
            orig_fmt = response.headers.get_content_subtype()
            base = f'{base_name}-{index}'
            # If we weren't given an output dir, then for URLs, we have no
            # choice but to use the current dir to download the file.
            # Important: don't change self._output_dir because if other
            # inputs *are* files, then those files will need other output dirs.
            if not output_dir:
                output_dir = os.getcwd()
            file = path.realpath(path.join(output_dir, base + '.' + orig_fmt))
            if not download_file(item, file):
                warn(f'Unable to download {item}')
                return (None, None)
            url_file = path.realpath(path.join(output_dir, base + '.url'))
            with open(url_file, 'w') as f:
                f.write(url_file_content(item))
                inform(f'Wrote URL to [white on grey42]{relative(url_file)}[/]')
        else:
            file = path.realpath(path.join(os.getcwd(), item))
            orig_fmt = filename_extension(file)[1:]

        if not path.getsize(file) > 0:
            warn(f'File has zero length: {relative(file)}')
            return (None, None)

        if __debug__: log(f'{relative(file)} has original format {orig_fmt}')
        return (file, orig_fmt)


    # The following thread lock is used in _send(...) around a call to creating
    # an annotated image of the results from a service.  The annotation
    # function in question uses image functions from matplotlib, and during
    # multithreaded execution, for reasons that are not clear to me, sometimes
    # an annotated image for a given service would end up with results from
    # another service also added over it.  I've been unable to find an error
    # in my code, and suspect the problem is some kind of thread safety issue
    # in those low-level image functions (perhaps only on some platforms like
    # macOS).  Preventing multithreaded execution around that one call seems
    # to be enough to stop the problem.  Admittedly, it's a sledgehammer
    # approach, but many hours of testing have yet to find a better solution.
    _lock = Lock()

    def _send(self, image, service):
        '''Send the "image" to the service named "service" and write output in
        directory "dest_dir".
        '''

        service_name = f'[{service.name_color()}]{service.name()}[/]'
        inform(f'Sending to {service_name} and waiting for response ...')
        last_time = timer()
        try:
            output = service.result(image.file)
        except AuthFailure as ex:
            raise AuthFailure(f'Unable to use {service}: {str(ex)}')
        except RateLimitExceeded as ex:
            time_passed = timer() - last_time
            if time_passed < 1/service.max_rate():
                warn(f'Pausing {service_name} due to rate limits')
                wait(1/service.max_rate() - time_passed)
                warn(f'Continuing {service_name}')
                return self._send(image, service)
        if output.error:
            # Sanitize the error string in case it contains '{' characters.
            msg = output.error.replace('{', '{{{{').replace('}', '}}}}')
            alert(f'{service_name} failed: {msg}')
            warn(f'No result from {service_name} for {relative(image.file)}')
            return None
        inform(f'Got result from {service_name}.')
        raise_for_interrupts()

        inform(f'Creating annotated image for {service_name}.')
        file_name   = path.basename(image.file)
        base_path   = path.join(image.dest_dir, file_name)
        annot_path  = self._renamed(base_path, str(service), 'png')
        report_path = None
        with self._lock:
            self._save(annotated_image(image.file, output.boxes, service), annot_path)
        if self._extended_results:
            txt_file  = self._renamed(base_path, str(service), 'txt')
            json_file = self._renamed(base_path, str(service), 'json')
            inform(f'Saving all data for {service_name}.')
            self._save(json.dumps(output.data), json_file)
            inform(f'Saving extracted text for {service_name}.')
            self._save(output.text, txt_file)
        if self._compare:
            gt_file = alt_extension(image.item_file, 'gt.txt')
            gt_path = relative(gt_file)
            report_path = self._renamed(image.item_file, str(service), 'tsv')
            relaxed = (self._compare == 'relaxed')
            if readable(gt_file) and nonempty(gt_file):
                if __debug__: log(f'reading ground truth from {gt_file}')
                gt_text = open(gt_file, 'r').read()
                inform(f'Saving {service_name} comparison to ground truth')
                self._save(text_comparison(output.text, gt_text, relaxed), report_path)
            elif not nonempty(gt_file):
                warn(f'Skipping {service_name} comparison because {gt_path} is empty')
            else:
                warn(f'Skipping {service_name} comparison because {gt_path} not available')
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
        if file and self._max_dimensions:
            (image_width, image_height) = image_dimensions(file)
            (max_width, max_height) = self._max_dimensions
            if max_width < image_width or max_height < image_height:
                new_file = self._resized_image(file)
                if new_file and path.basename(new_file) != path.basename(file):
                    to_delete.add(new_file)
                file = new_file
        if file and self._max_size and self._max_size < image_size(file):
            new_file = self._smaller_file(file)
            if new_file and  path.basename(new_file) != path.basename(file):
                to_delete.add(new_file)
            file = new_file
        return Input(orig_item, orig_fmt, item_file, file, dest_dir, to_delete)


    def _converted_file(self, file, to_format, dest_dir):
        basename = path.basename(filename_basename(file))
        new_file = path.join(dest_dir, basename + '.handprint.' + to_format)
        if path.exists(new_file):
            inform(f'Using existing converted image in {relative(new_file)}')
            return new_file
        else:
            inform(f'Converting to {to_format} format: {relative(file)}')
            (converted, error) = converted_image(file, to_format, new_file)
            if error:
                alert(f'Failed to convert {relative(file)}: {error}')
                return None
            return converted


    def _smaller_file(self, file):
        if not file:
            return None
        file_ext = filename_extension(file)
        name_tail = '.handprint' + file_ext
        new_file = file if name_tail in file else filename_basename(file) + name_tail
        if path.exists(new_file):
            if image_size(new_file) < self._max_size:
                inform(f'Reusing resized image found in {relative(new_file)}')
                return new_file
            else:
                # We found a ".handprint.ext" file, perhaps from a previous run,
                # but for the current set of services, it's larger than allowed.
                if __debug__: log('existing resized file larger than {}b: {}',
                                  humanize.intcomma(self._max_size), new_file)
        inform(f'Size too large; reducing size: {relative(file)}')
        (resized, error) = reduced_image_size(file, new_file, self._max_size)
        if error:
            alert(f'Failed to resize {relative(file)}: {error}')
            return None
        return resized


    def _resized_image(self, file):
        (max_width, max_height) = self._max_dimensions
        file_ext = filename_extension(file)
        name_tail = '.handprint' + file_ext
        new_file = file if name_tail in file else filename_basename(file) + name_tail
        if path.exists(new_file) and readable(new_file):
            (image_width, image_height) = image_dimensions(new_file)
            if image_width < max_width and image_height < max_height:
                inform(f'Using reduced image found in {relative(new_file)}')
                return new_file
            else:
                # We found a "-reduced" file, perhaps from a previous run, but
                # for the current set of services, dimension are too large.
                if __debug__: log('existing resized file larger than {}x{}: {}',
                                  max_width, max_height, new_file)
        inform(f'Dimensions too large; reducing dimensions: {relative(file)}')
        (resized, error) = reduced_image_dimensions(file, new_file, max_width, max_height)
        if error:
            alert(f'Failed to re-dimension {relative(file)}: {error}')
            return None
        return resized


    def _save(self, result, file):
        # First perform some sanity checks.
        if result is None:
            warn(f'No data for {file}')
            return
        if isinstance(result, tuple):
            # Assumes 2 elements: data, and error
            (data, error) = result
            if error:
                alert(f'Error: {error}')
                warn(f'Unable to write {file}')
                return
            else:
                result = data

        if __debug__: log(f'writing output to file {relative(file)}')
        if isinstance(result, str):
            with open(file, 'w') as f:
                f.write(result)
        elif isinstance(result, io.BytesIO):
            with open(file, 'wb') as f:
                shutil.copyfileobj(result, f)
        else:
            # There's no other type in the code, so if we get here ...
            raise InternalError('Unexpected data in save_output() -- please report this.')


    def _renamed(self, base_path, service_name, format):
        (root, ext) = path.splitext(base_path)
        if '.handprint' in root:
            return f'{root}-{service_name}.{format}'
        else:
            return f'{root}.handprint-{service_name}.{format}'


# Helper functions.
# ......................................................................

def url_file_content(url):
    return f'[InternetShortcut]\nURL={url}\n'
