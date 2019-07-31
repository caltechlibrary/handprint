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

import io
import json
import os
from   os import path
import shutil
import time
from   timeit import default_timer as timer

import handprint
from handprint.annotate import annotated_image
from handprint.files import converted_image, reduced_image
from handprint.files import filename_basename, filename_extension, relative
from handprint.files import files_in_directory, alt_extension, handprint_path
from handprint.files import readable, writable, is_url, image_dimensions
from handprint.messages import color
from handprint.network import network_available, download_file, disable_ssl_cert_check
from handprint.progress import ProgressIndicator


# Main class.
# -----------------------------------------------------------------------------

class Manager:
    def __init__(self, classes, output_dir, say):
        self._classes = classes
        self._output_dir = output_dir
        self._say = say
        self._spinner = ProgressIndicator(say.use_color(), say.be_quiet())


    def process(self, item, index, base_name, all_results):
        # Shortcuts to make the code more readable.
        output_dir = self._output_dir
        spinner = self._spinner
        say = self._say

        try:
            spinner.start('Starting on {}'.format(relative(item)))
            if is_url(item):
                # Make sure the URLs point to images.
                if __debug__: log('Testing if URL contains an image: {}', item)
                try:
                    response = request.urlopen(item)
                except Exception as ex:
                    if __debug__: log('Network access resulted in error: {}', str(ex))
                    spinner.fail('Skipping URL due to error: {}'.format(ex))
                    return
                if response.headers.get_content_maintype() != 'image':
                    spinner.fail('Did not find an image at {}'.format(item))
                    return
                fmt = response.headers.get_content_subtype()
                base = '{}-{}'.format(base_name, index)
                file = path.realpath(path.join(output_dir, base + '.' + fmt))
                if not download_file(item, file, spinner = spinner):
                    return
                url_file = path.realpath(path.join(output_dir, base + '.url'))
                with open(url_file, 'w') as f:
                    f.write(url_file_content(item))
                    spinner.update('Wrote URL to {}'.format(relative(url_file)))
            else:
                file = path.realpath(path.join(os.getcwd(), item))
                fmt = filename_extension(file)

            dest_dir = output_dir if output_dir else path.dirname(file)
            if not writable(dest_dir):
                say.fatal('Cannot write output in {}.'.format(dest_dir))
                return

            # Iterate over the services.
            for service_class in self._classes:
                service = service_class()
                service.init_credentials()
                last_time = timer()

                # If need to convert format, best do it after resizing original fmt.
                need_convert = fmt not in service.accepted_formats()
                # Test the dimensions, not bytes, because of compression.
                if image_dimensions(file) > service.max_dimensions():
                    file = self._file_after_resizing(file, service, spinner)
                if file and need_convert:
                    file = self._file_after_converting(file, 'jpg', service, spinner)
                if not file:
                    return

                spinner.update('Sending to {} {}'.format(
                    color(service, 'white', say.use_color()),
                    # Need explicit color research or colorization goes wrong.
                    color('and waiting for response', 'info', say.use_color())))
                try:
                    result = service.result(file)
                except RateLimitExceeded as ex:
                    time_passed = timer() - last_time
                    if time_passed < 1/service.max_rate():
                        spinner.warn('Pausing due to rate limits')
                        time.sleep(1/service.max_rate() - time_passed)
                if result.error:
                    spinner.fail(result.error)
                    return

                file_name  = path.basename(file)
                base_path  = path.join(dest_dir, file_name)
                annot_file = alt_extension(base_path, str(service) + '.jpg')
                spinner.update('Annotated image -> {}'.format(relative(annot_file)))
                save_output(annotated_image(file, result.boxes), annot_file)
                if all_results:
                    txt_file  = alt_extension(base_path, str(service) + '.txt')
                    json_file = alt_extension(base_path, str(service) + '.json')
                    spinner.update('Text -> {}'.format(relative(txt_file)))
                    save_output(result.text, txt_file)
                    spinner.update('All data -> {}'.format(relative(json_file)))
                    save_output(json.dumps(result.data), json_file)
            spinner.stop('Done with {}'.format(relative(item)))
        except (KeyboardInterrupt, UserCancelled) as ex:
            spinner.warn('Interrupted')
            raise
        except AuthenticationFailure as ex:
            spinner.fail('Unable to continue using {}: {}'.format(service, ex))
            return
        except Exception as ex:
            spinner.fail(say.error_text('Stopping due to a problem'))
            raise


    def _file_after_resizing(self, file, tool, spinner):
        file_ext = filename_extension(file)
        new_file = filename_basename(file) + '-reduced.' + file_ext
        if path.exists(new_file):
            spinner.update('Using reduced image found in {}'.format(relative(new_file)))
            return new_file
        else:
            spinner.update('Original image too large; reducing size')
            (resized, error) = reduced_image(file, tool.max_dimensions())
            if not resized:
                spinner.fail('Failed to resize {}: {}'.format(relative(file, error)))
                return None
            return resized


    def _file_after_converting(self, file, to_format, tool, spinner):
        new_file = filename_basename(file) + '.' + to_format
        if path.exists(new_file):
            spinner.update('Using converted image found in {}'.format(relative(new_file)))
            return new_file
        else:
            spinner.update('Converting to {} format: {}'.format(to_format, relative(file)))
            (converted, error) = converted_image(file, to_format)
            if not converted:
                spinner.fail('Failed to convert {}: {}'.format(relative(file), error))
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
