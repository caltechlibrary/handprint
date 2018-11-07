'''Handprint: HANDwritten Page RecognitIoN Test for Caltech Archives.

This project uses alternative text recognition methods on documents from the
Caltech Archives (http://archives.caltech.edu).  Tests include the use of
Google's OCR capabilities in their Google Cloud Vision API
(https://cloud.google.com/vision/docs/ocr), Microsoft's Azure, and others.

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from   halo import Halo
import json
import os
from   os import path
import plac
import requests
import sys
from   sys import exit as exit
try:
    from termcolor import colored
except:
    pass
import time
from   timeit import default_timer as timer
import traceback
from   urllib import request

import handprint
from handprint.constants import ON_WINDOWS, ACCEPTED_FORMATS, KNOWN_METHODS
from handprint.messages import msg, color, MessageHandlerCLI
from handprint.progress import ProgressIndicator
from handprint.network import network_available, download
from handprint.files import files_in_directory, replace_extension, handprint_path
from handprint.files import readable, writable
from handprint.files import filename_basename, filename_extension, relative
from handprint.files import convert_image, resize_image, image_dimensions
from handprint.methods import GoogleTR
from handprint.methods import MicrosoftTR
from handprint.exceptions import *
from handprint.debug import set_debug, log

# Main program.
# ......................................................................

@plac.annotations(
    creds_dir  = ('look for credentials files in directory "D"',     'option', 'c'),
    from_file  = ('read file names or URLs from file "F"',           'option', 'f'),
    list       = ('print list of known methods',                     'flag',   'l'),
    method     = ('use method "M" (default: "all")',                 'option', 'm'),
    output     = ('write output to directory "O"',                   'option', 'o'),
    root_name  = ('name downloaded images using root file name "R"', 'option', 'r'),
    given_urls = ('assume have URLs, not files (default: files)',    'flag',   'u'),
    quiet      = ('do not print info messages while working',        'flag',   'q'),
    no_color   = ('do not color-code terminal output',               'flag',   'C'),
    debug      = ('turn on debugging (console only)',                'flag',   'D'),
    version    = ('print version info and exit',                     'flag',   'V'),
    images     = 'if given -u, URLs, else directories and/or files',
)

def main(creds_dir = 'D', from_file = 'F', list = False, method = 'M',
         output = 'O', given_urls = False, root_name = 'R', quiet = False,
         no_color = False, debug = False, version = False, *images):
    '''Handprint (a loose acronym of "HANDwritten Page RecognitIoN Test") can
run alternative text recognition methods on images of document pages.

If given the command-line flag -l (or /l on Windows), Handprint will print a
list of the known methods and then exit.  The option -m (/m on Windows) can
be used to select a specific method.  (The default method is to run them all.)

When invoked, the command-line arguments should contain one of the following:

 a) one or more directory paths or one or more image file paths, which will
    be interpreted as images (either individually or in directories) to be
    processed;

 b) if given the -u option (/u on Windows), one or more URLs, which will be
    interpreted as network locations of image files to be processed;

 c) if given the -f option (/f on Windows), a file containing either image
    paths or (if combined with the -u option), image URLs

If given URLs (via the -u option), Handprint will first download the images
found at the URLs to a local directory indicated by the option -o (/o on
Windows).  Handprint will send each image file to OCR/HTR services from
Google, Microsoft and others.  It will write the results to new files placed
either in the same directories as the original files, or (if given the -o
option) to the directory indicated by the -o option value (/o on Windows).
The results will be written in files named after the original files with the
addition of a string that indicates the service used.  For example, a file
named "somefile.jpg" will produce

  somefile.jpg
  somefile.google.txt
  somefile.google.json
  somefile.microsoft.txt
  somefile.microsoft.json
  somefile.amazon.txt
  somefile.amazon.json
  ...

and so on for each image and each service used.  The .txt files will contain
the text extracted (if any).  The .json files will contain the complete
response from the service, converted to JSON by Handprint.  In some cases,
such as Google's API, the service may offer multiple operations and will
return individual results for different API calls or options; in those cases,
Handprint combines the results of multiple API calls into a single JSON
object.

Note that if -u (/u on Windows) is given, then an output directory MUST also
be specified using the option -o (/o on Windows) because it is not possible
to write the results in the network locations represented by the URLs.  Also,
when -u is used, the images and text results will be stored in files whose
root names have the form "document-N", where "N" is an integer.  The root
name can be changed using the -r option (/r on Windows).  The image will be
converted to ordinary JPEG format for maximum compatibility with the
different OCR services and written to "document-N.jpg", and the URL
corresponding to each document will be written in a file named
"document-N.url" so that it is possible to connect each "document-N.jpg" to
the URL it came from.

If images are too large for a method/service, then Handprint will resize them
prior to sending them.  It will write the reduced image to a file named
"FILENAME-reduced.EXT", where "FILENAME" is the original file name and "EXT"
is the file extension.  This means that if an image needs to be resized, the
results of applying the text recognition methods will be, e.g.,

  somefile-reduced.jpg
  somefile-reduced.google.txt
  somefile-reduced.google.json
  somefile-reduced.microsoft.txt
  somefile-reduced.microsoft.json
  somefile-reduced.amazon.txt
  somefile-reduced.amazon.json
  ...

Credentials for different services need to be provided to Handprint in the
form of JSON files.  Each service needs a separate JSON file named after the
service (e.g., "microsoft_credentials.json") and placed in a directory that
Handprint searches.  By default, Handprint searches for the files in a
subdirectory named "creds" where Handprint is installed, but an alternative
directory can be indicated at run-time using the -c command-line option (/c
on Windows).  The specific format of each credentials file is different for
each service; please consult the Handprint documentation for more details.

If given the -q option (/q on Windows), Handprint will not print its usual
informational messages while it is working.  It will only print messages
for warnings or errors.

If given the -V option (/V on Windows), this program will print version
information and exit without doing anything else.
'''

    # Prepare notification methods and hints.
    say = MessageHandlerCLI(not no_color, quiet)
    prefix = '/' if ON_WINDOWS else '-'
    hint = '(Hint: use {}h for help.)'.format(prefix)

    # Process arguments.
    if debug:
        set_debug(True)
    if version:
        print_version()
        exit()
    if list:
        say.info('Known methods:')
        for key in KNOWN_METHODS.keys():
            say.info('   {}'.format(key))
        exit()
    if not network_available():
        exit(say.fatal_text('No network.'))

    if from_file == 'F':
        from_file = None
    else:
        if not path.isabs(from_file):
            from_file = path.realpath(path.join(os.getcwd(), from_file))
        if not path.exists(from_file):
            exit(say.error_text('File not found: {}'.format(from_file)))
        if not readable(from_file):
            exit(say.error_text('File not readable: {}'.format(from_file)))

    if not images and not from_file:
        exit(say.error_text('Need provide images or URLs. {}'.format(hint)))
    if any(item.startswith('-') for item in images):
        exit(say.error_text('Unrecognized option in arguments. {}'.format(hint)))

    if creds_dir == 'D':
        creds_dir = path.join(handprint_path(), 'creds')
    if not readable(creds_dir):
        exit(say.error_text('Directory not readable: {}'.format(creds_dir)))
    else:
        if __debug__: log('Assuming credentials found in {}.', creds_dir)

    if method == 'M':
        method = 'all'
    method = method.lower()
    if method != 'all' and method not in KNOWN_METHODS:
        exit(say.error_text('"{}" is not a known method. {}'.format(method, hint)))

    if output == 'O':
        output = None
    else:
        if not path.isabs(output):
            output = path.realpath(path.join(os.getcwd(), output))
        if path.isdir(output):
            if not writable(output):
                exit(say.error_text('Directory not writable: {}'.format(output)))
        else:
            os.mkdir(output)
            if __debug__: log('Created output directory {}', output)
    if given_urls and not output:
        exit(say.error_text('Must provide an output directory if using URLs.'))
    if root_name != 'R' and not given_urls:
        exit(say.error_text('Option {}r can only be used with URLs.'.format(prefix)))
    if root_name == 'R':
        root_name = 'document'

    # Create a list of files to be processed.
    targets = targets_from_arguments(images, from_file, given_urls, say)
    if not targets:
        exit(say.warn_text('No images to process; quitting.'))

    # Let's do this thing.
    try:
        if method == 'all':
            say.info('Applying all methods in succession.')
            for m in KNOWN_METHODS.values():
                if not say.be_quiet():
                    say.msg('='*70, 'dark')
                run(m, targets, given_urls, output, root_name, creds_dir, say)
            if not say.be_quiet():
                say.msg('='*70, 'dark')
        else:
            m = KNOWN_METHODS[method]
            run(m, targets, given_urls, output, root_name, creds_dir, say)
    except (KeyboardInterrupt, UserCancelled) as err:
        exit(say.info_text('Quitting.'))
    except ServiceFailure as err:
        exit(say.error_text(str(err)))
    except Exception as err:
        if debug:
            import pdb; pdb.set_trace()
        exit(say.error_text('{}\n{}'.format(str(err), traceback.format_exc())))
    say.info('Done.')


# If this is windows, we want the command-line args to use slash intead
# of hyphen.

if ON_WINDOWS:
    main.prefix_chars = '/'


# Helper functions.
# ......................................................................

def run(method_class, targets, given_urls, output_dir, root_name, creds_dir, say):
    spinner = ProgressIndicator(say.use_color(), say.be_quiet())
    try:
        method = method_class()
        say.info('Using method "{}".'.format(method))
        method.init_credentials(creds_dir)
        for index, item in enumerate(targets, 1):
            last_time = timer()
            action = 'Downloading' if given_urls else 'Reading'
            spinner.start('{} {}'.format(action, relative(item)))
            if given_urls:
                # Make sure the URLs point to images.
                if __debug__: log('Testing if URL contains an image: {}', item)
                try:
                    response = request.urlopen(item)
                except Exception as err:
                    if __debug__: log('Network access resulted in error: {}', str(err))
                    spinner.fail('Skipping URL due to error: {}'.format(err))
                    continue
                if response.headers.get_content_maintype() != 'image':
                    spinner.fail('Did not find an image at {}'.format(item))
                    continue
                fmt = response.headers.get_content_subtype()
                base = '{}-{}'.format(root_name, index)
                file = path.realpath(path.join(output_dir, base + '.' + fmt))
                if __debug__: log('Downloading {}', item)
                error = download(item, file)
                if not error:
                    spinner.update('Wrote contents to {}'.format(relative(file)))
                else:
                    spinner.fail('Failed to download {}: {}'.format(item, error))
                    continue
                url_file = path.realpath(path.join(output_dir, base + '.url'))
                with open(url_file, 'w') as f:
                    f.write(url_file_content(item))
                    spinner.update('Wrote URL to {}'.format(relative(url_file)))
            else:
                file = path.realpath(path.join(os.getcwd(), item))
                fmt = filename_extension(file)

            dest_dir = output_dir if output_dir else path.dirname(file)
            if not writable(dest_dir):
                spinner.stop()
                say.fatal('Cannot write output in {}.'.format(dest_dir))
                continue

            # If need to convert format, best do it after resizing original fmt.
            need_convert = fmt not in method.accepted_formats()
            # Test the dimensions, not bytes, because of compression.
            if image_dimensions(file) > method.max_dimensions():
                file = file_after_resizing(file, method, spinner)
            if file and need_convert:
                file = file_after_converting(file, 'jpeg', method, spinner)
            if not file:
                continue

            spinner.update('Sending to {} and waiting for response'.format(method))
            try:
                result = method.result(file)
            except RateLimitExceeded as err:
                time_passed = timer() - last_time
                if time_passed < 1/method.max_rate():
                    spinner.warn('Pausing due to rate limits')
                    time.sleep(1/method.max_rate() - time_passed)
            if result.error:
                spinner.fail(result.error)
                continue

            file_name = path.basename(file)
            base_path = path.join(dest_dir, file_name)
            txt_file  = replace_extension(base_path, '.' + str(method) + '.txt')
            json_file = replace_extension(base_path, '.' + str(method) + '.json')
            spinner.update('Text -> {}'.format(relative(txt_file)))
            save_output(result.text, txt_file)
            spinner.update('All data -> {}'.format(relative(json_file)))
            save_output(json.dumps(result.data), json_file)
            spinner.stop('Done with {}'.format(relative(item)))
    except (KeyboardInterrupt, UserCancelled) as err:
        if spinner:
            spinner.warn('Interrupted')
    except AuthenticationFailure as err:
        spinner.fail('Unable to continue using {}: {}'.format(method, err))
        return
    except Exception as err:
        if spinner:
            spinner.fail(say.error_text('Stopping due to a problem'))
        raise


def targets_from_arguments(images, from_file, given_urls, say):
    targets = []
    if from_file:
        if __debug__: log('Opening {}', from_file)
        with open(from_file) as f:
            targets = f.readlines()
        targets = [line.rstrip('\n') for line in targets]
        if __debug__: log('Read {} lines from {}.', len(targets), from_file)
        if not given_urls:
            targets = filter_urls(targets, say)
    elif given_urls:
        # We assume that the arguments are URLs and take them as-is.
        targets = images
    else:
        # We were given files and/or directories.  Look for image files.
        for item in filter_urls(images, say):
            if path.isfile(item) and filename_extension(item) in ACCEPTED_FORMATS:
                targets.append(item)
            elif path.isdir(item):
                targets += files_in_directory(item, extensions = ACCEPTED_FORMATS)
            else:
                say.warn('"{}" not a file or directory'.format(item))
    return targets


def filter_urls(item_list, say):
    results = []
    for item in item_list:
        if item.startswith('http') or item.startswith('ftp'):
            say.warn('Unexpected URL skipped: {}'.format(item))
            continue
        else:
            results.append(item)
    return results


def url_file_content(url):
    return '[InternetShortcut]\nURL={}\n'.format(url)


def file_after_resizing(file, tool, spinner):
    file_ext = filename_extension(file)
    new_file = filename_basename(file) + '-reduced.' + file_ext
    if path.exists(new_file):
        spinner.update('Using reduced image found in {}'.format(relative(new_file)))
        return new_file
    else:
        spinner.update('Original image too large; reducing size')
        (resized, error) = resize_image(file, tool.max_dimensions())
        if not resized:
            spinner.fail('Failed to resize {}: {}'.format(relative(file, error)))
            return None
        return resized


def file_after_converting(file, to_format, tool, spinner):
    new_file = filename_basename(file) + '.' + to_format
    if path.exists(new_file):
        spinner.update('Using converted image found in {}'.format(relative(new_file)))
        return new_file
    else:
        spinner.update('Converting to {} format: {}'.format(to_format, relative(file)))
        (converted, error) = convert_image(file, to_format)
        if not converted:
            spinner.fail('Failed to convert {}: {}'.format(relative(file), error))
            return None
        return converted


def print_version():
    print('{} version {}'.format(handprint.__title__, handprint.__version__))
    print('Author: {}'.format(handprint.__author__))
    print('URL: {}'.format(handprint.__url__))
    print('License: {}'.format(handprint.__license__))


def save_output(text, file):
    with open(file, 'w') as f:
        f.write(text)


# Main entry point.
# ......................................................................
# The following allows users to invoke this using "python3 -m handprint".

if __name__ == '__main__':
    plac.call(main)


# For Emacs users
# ......................................................................
# Local Variables:
# mode: python
# python-indent-offset: 4
# End:
