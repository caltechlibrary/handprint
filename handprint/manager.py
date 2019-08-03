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

from   blessings import Terminal
from   concurrent.futures import ThreadPoolExecutor
import io
import json
import os
from   os import path
import shutil
from   threading import Thread
import sys
import time
from   timeit import default_timer as timer

import handprint
from handprint.annotate import annotated_image
from handprint.exceptions import *
from handprint.files import converted_image, reduced_image
from handprint.files import filename_basename, filename_extension, relative
from handprint.files import files_in_directory, alt_extension, handprint_path
from handprint.files import readable, writable, is_url, image_dimensions
from handprint.messages import color
from handprint.network import network_available, download_file, disable_ssl_cert_check
from handprint.progress import ProgressIndicator
from handprint.services import KNOWN_SERVICES


# Main class.
# -----------------------------------------------------------------------------

class Manager:
    def __init__(self, services, num_threads, output_dir, extended_results, say):
        self._services = services
        self._num_threads = num_threads
        self._extended_results = extended_results
        self._output_dir = output_dir
        self._say = say
        self._spinner = None


    def process(self, item, index, base_name):
        # Shortcuts to make the code more readable.
        output_dir = self._output_dir
        spinner = self._spinner
        say = self._say

        try:
            say.msg('{} {}'.format(
                color('Starting on', 'info', say.use_color()),
                color(item, 'white', say.use_color())))
            if is_url(item):
                # Make sure the URLs point to images.
                if __debug__: log('Testing if URL contains an image: {}', item)
                try:
                    response = request.urlopen(item)
                except Exception as ex:
                    if __debug__: log('Network access resulted in error: {}', str(ex))
                    say.warn('Skipping URL due to error: {}'.format(ex))
                    return
                if response.headers.get_content_maintype() != 'image':
                    say.warn('Did not find an image at {}'.format(item))
                    return
                fmt = response.headers.get_content_subtype()
                base = '{}-{}'.format(base_name, index)
                file = path.realpath(path.join(output_dir, base + '.' + fmt))
                if not download_file(item, file, spinner = spinner):
                    return
                url_file = path.realpath(path.join(output_dir, base + '.url'))
                with open(url_file, 'w') as f:
                    f.write(url_file_content(item))
                    say.info('Wrote URL to {}'.format(relative(url_file)))
            else:
                file = path.realpath(path.join(os.getcwd(), item))
                fmt = filename_extension(file)

            dest_dir = output_dir if output_dir else path.dirname(file)
            if not writable(dest_dir):
                say.error('Cannot write output in {}.'.format(dest_dir))
                return

            # Wrap calls to the services so we can loop more easily.
            def do_send(service):
                say.msg('{} {} {}'.format(
                    color('Sending to', 'info', say.use_color()),
                    color(service, 'magenta', say.use_color()),
                    # Need explicit color research or colorization goes wrong.
                    color('and waiting for response ...', 'info', say.use_color())))
                service_class = KNOWN_SERVICES[service]
                self._send(service_class, file, fmt, dest_dir)

            # Debugging is easier if thread pools are not used.  If the number
            # of threads is set to 1, we force non-thread-pool execution.
            if self._num_threads == 1:
                for service in self._services:
                    do_send(service)
            else:
                with ThreadPoolExecutor(max_workers = self._num_threads) as executor:
                    executor.map(do_send, iter(self._services))
            say.info('Done with {}'.format(relative(item)))
        except (KeyboardInterrupt, UserCancelled) as ex:
            say.warn('Interrupted')
            raise
        except AuthenticationFailure as ex:
            say.error('Unable to continue using {}: {}'.format(service, ex))
            return
        except Exception as ex:
            say.error('Stopping due to a problem')
            raise


    def _send(self, service_class, file, file_format, dest_dir):
        # Shortcuts to make the code more readable.
        say = self._say

        # The index is used both to identify the service class and to position
        # the cursor on different lines for producing output.
        service = service_class()
        service.init_credentials()
        last_time = timer()

        # If need to convert format, best do it after resizing original fmt.
        need_convert = file_format not in service.accepted_formats()
        # Test the dimensions, not bytes, because of compression.
        if image_dimensions(file) > service.max_dimensions():
            file = self._file_after_resizing(file, service)
        if file and need_convert:
            file = self._file_after_converting(file, 'jpg', service)
        if not file:
            return

        try:
            result = service.result(file)
        except RateLimitExceeded as ex:
            time_passed = timer() - last_time
            if time_passed < 1/service.max_rate():
                say.warn('Pausing due to rate limits')
                time.sleep(1/service.max_rate() - time_passed)
        if result.error:
            say.error(result.error)
            return

        say.msg('{} {}.'.format(
            color('Got result from', 'info', say.use_color()),
            color(service, 'magenta', say.use_color())))
        file_name  = path.basename(file)
        base_path  = path.join(dest_dir, file_name)
        annot_file = alt_extension(base_path, str(service) + '.jpg')
        say.info('Creating annotated image: {}'.format(relative(annot_file)))
        save_output(annotated_image(file, result.boxes), annot_file)
        if self._extended_results:
            txt_file  = alt_extension(base_path, str(service) + '.txt')
            json_file = alt_extension(base_path, str(service) + '.json')
            say.info('Saving all data: {}'.format(relative(json_file)))
            save_output(json.dumps(result.data), json_file)
            say.info('Saving extracted text: {}'.format(relative(txt_file)))
            save_output(result.text, txt_file)


    def _file_after_resizing(self, file, tool):
        file_ext = filename_extension(file)
        new_file = filename_basename(file) + '-reduced.' + file_ext
        say = self._say
        if path.exists(new_file):
            if __debug__: log('Using reduced image found in {}'.format(relative(new_file)))
            return new_file
        else:
            say.info('Original image too large; reducing size')
            (resized, error) = reduced_image(file, tool.max_dimensions())
            if not resized:
                say.error('Failed to resize {}: {}'.format(relative(file, error)))
                return None
            return resized


    def _file_after_converting(self, file, to_format, tool):
        new_file = filename_basename(file) + '.' + to_format
        say = self._say
        if path.exists(new_file):
            say.info('Using converted image found in {}'.format(relative(new_file)))
            return new_file
        else:
            say.info('Converting to {} format: {}'.format(to_format, relative(file)))
            (converted, error) = converted_image(file, to_format)
            if not converted:
                say.error('Failed to convert {}: {}'.format(relative(file), error))
                return None
            return converted


# Helper functions.
# ......................................................................

def save_output(data, file):
    if isinstance(data, str):
        with open(file, 'w') as f:
            f.write(data)
    elif isinstance(data, io.BytesIO):
        with open(file, 'wb') as f:
            shutil.copyfileobj(data, f)


def url_file_content(url):
    return '[InternetShortcut]\nURL={}\n'.format(url)
