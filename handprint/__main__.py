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
import io
import json
import os
from   os import path
import plac
import requests
import shutil
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
from handprint.network import network_available, download, disable_ssl_cert_check
from handprint.files import files_in_directory, alt_extension, handprint_path
from handprint.files import readable, writable, is_url, image_dimensions
from handprint.files import filename_basename, filename_extension, relative
from handprint.files import converted_image, reduced_image
from handprint.methods import GoogleTR
from handprint.methods import MicrosoftTR
from handprint.exceptions import *
from handprint.debug import set_debug, log
from handprint.annotate import annotated_image

# Disable certificate verification.  FIXME: probably shouldn't do this.
disable_ssl_cert_check()


# Main program.
# ......................................................................

@plac.annotations(
    base_name  = ('use base name "B" to name downloaded images',     'option', 'b'),
    creds_dir  = ('look for credentials files in directory "C"',     'option', 'c'),
    from_file  = ('read file names or URLs from file "F"',           'option', 'f'),
    list       = ('print list of known methods',                     'flag',   'l'),
    method     = ('use method "M" (default: "all")',                 'option', 'm'),
    output     = ('write output to directory "O"',                   'option', 'o'),
    given_urls = ('assume have URLs, not files (default: files)',    'flag',   'u'),
    quiet      = ('do not print info messages while working',        'flag',   'q'),
    no_annot   = ('do not produce annotated images (default: do)',   'flag',   'A'),
    no_color   = ('do not color-code terminal output (default: do)', 'flag',   'C'),
    debug      = ('turn on debugging',                               'flag',   'D'),
    version    = ('print version info and exit',                     'flag',   'V'),
    images     = 'if given -u, URLs, else directories and/or files',
)

def main(base_name = 'B', creds_dir = 'C', from_file = 'F', list = False,
         method = 'M', output = 'O', given_urls = False, quiet = False,
         no_annot = False, no_color = False, debug = False, version = False,
         *images):
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
addition of a string that indicates the method used.  For example, a file
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

Unless given the do-not-annotate option, -A (/A on Windows), Handprint will
also generate a copy of the image with superimposed bounding boxes and text
to show the recognition results.  The annotated images will include the name
of the service; in other words, the list of files produced by Handprint will
include

  somefile.google.jpg
  somefile.microsoft.jpg
  ...

and so on.  (They are distinguished from the original unannotated image, which
will be left in somefile.jpg.)

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
  somefile-reduced.google.jpg
  somefile-reduced.google.json
  somefile-reduced.microsoft.txt
  somefile-reduced.microsoft.jpg
  somefile-reduced.microsoft.json
  somefile-reduced.amazon.txt
  somefile-reduced.amazon.jpg
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

    # Reverse some flags for easier code readability
    annotate = not no_annot

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

    if creds_dir == 'C':
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
    if base_name != 'B' and not given_urls:
        exit(say.error_text('Option {}r can only be used with URLs.'.format(prefix)))
    if base_name == 'B':
        base_name = 'document'

    # Create a list of files to be processed.
    targets = targets_from_arguments(images, from_file, given_urls, say)
    if not targets:
        exit(say.warn_text('No images to process; quitting.'))

    # Let's do this thing.
    try:
        num_items = len(targets)
        print_separators = num_items > 1 and not say.be_quiet()
        if method == 'all':
            # Order doesn't really matter; just make it consistent run-to-run.
            methods = sorted(KNOWN_METHODS.values(), key = lambda x: str(x))
            say.info('Will apply all known methods to {} images.'.format(num_items))
        else:
            methods = [KNOWN_METHODS[method]]
            say.info('Will apply method "{}" to {} images.'.format(method, num_items))
        for index, item in enumerate(targets, start = 1):
            if print_separators:
                say.msg('='*70, 'dark')
            run(methods, item, index, base_name, output, creds_dir, annotate, say)
        if print_separators:
            say.msg('='*70, 'dark')
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

def run(classes, item, index, base_name, output_dir, creds_dir, annotate, say):
    spinner = ProgressIndicator(say.use_color(), say.be_quiet())
    try:
        spinner.start('Starting on {}'.format(relative(item)))
        if is_url(item):
            # Make sure the URLs point to images.
            if __debug__: log('Testing if URL contains an image: {}', item)
            try:
                response = request.urlopen(item)
            except Exception as err:
                if __debug__: log('Network access resulted in error: {}', str(err))
                spinner.fail('Skipping URL due to error: {}'.format(err))
                return
            if response.headers.get_content_maintype() != 'image':
                spinner.fail('Did not find an image at {}'.format(item))
                return
            fmt = response.headers.get_content_subtype()
            base = '{}-{}'.format(base_name, index)
            file = path.realpath(path.join(output_dir, base + '.' + fmt))
            error = download(item, file)
            if not error:
                spinner.update('Wrote contents to {}'.format(relative(file)))
            else:
                spinner.fail('Failed to download {}: {}'.format(item, error))
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

        # Iterate over the methods.
        for method_class in classes:
            method = method_class()
            method.init_credentials(creds_dir)
            last_time = timer()

            # If need to convert format, best do it after resizing original fmt.
            need_convert = fmt not in method.accepted_formats()
            # Test the dimensions, not bytes, because of compression.
            if image_dimensions(file) > method.max_dimensions():
                file = file_after_resizing(file, method, spinner)
            if file and need_convert:
                file = file_after_converting(file, 'jpg', method, spinner)
            if not file:
                return

            spinner.update('Sending to {} {}'.format(
                color(method, 'white', say.use_color()),
                # Need explicit color research or colorization goes wrong.
                color('and waiting for response', 'info', say.use_color())))
            try:
                result = method.result(file)
            except RateLimitExceeded as err:
                time_passed = timer() - last_time
                if time_passed < 1/method.max_rate():
                    spinner.warn('Pausing due to rate limits')
                    time.sleep(1/method.max_rate() - time_passed)
            if result.error:
                spinner.fail(result.error)
                return

            file_name  = path.basename(file)
            base_path  = path.join(dest_dir, file_name)
            txt_file   = alt_extension(base_path, str(method) + '.txt')
            json_file  = alt_extension(base_path, str(method) + '.json')
            annot_file = alt_extension(base_path, str(method) + '.jpg')
            spinner.update('Text -> {}'.format(relative(txt_file)))
            save_output(result.text, txt_file)
            spinner.update('All data -> {}'.format(relative(json_file)))
            save_output(json.dumps(result.data), json_file)
            if annotate:
                spinner.update('Annotated image -> {}'.format(relative(annot_file)))
                save_output(annotated_image(file, result.boxes), annot_file)
        spinner.stop('Done with {}'.format(relative(item)))
    except (KeyboardInterrupt, UserCancelled) as err:
        spinner.warn('Interrupted')
        raise
    except AuthenticationFailure as err:
        spinner.fail('Unable to continue using {}: {}'.format(method, err))
        return
    except Exception as err:
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
        # Ignore files that appear to be the previous output of Handprint.
        # These are files that end in, e.g., ".google.jpg"
        handprint_endings = ['.' + x + '.jpg' for x in KNOWN_METHODS.keys()]
        non_urls = filter_urls(images, say)
        non_urls = filter_endings(non_urls, handprint_endings)
        for item in non_urls:
            if path.isfile(item) and filename_extension(item) in ACCEPTED_FORMATS:
                targets.append(item)
            elif path.isdir(item):
                files = files_in_directory(item, extensions = ACCEPTED_FORMATS)
                files = filter_endings(files, handprint_endings)
                targets += files
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


def filter_endings(item_list, endings):
    if not endings:
        return item_list
    if not item_list:
        return []
    results = item_list
    for ending in endings:
        results = list(filter(lambda name: ending not in name.lower(), results))
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
        (resized, error) = reduced_image(file, tool.max_dimensions())
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
        (converted, error) = converted_image(file, to_format)
        if not converted:
            spinner.fail('Failed to convert {}: {}'.format(relative(file), error))
            return None
        return converted


def print_version():
    print('{} version {}'.format(handprint.__title__, handprint.__version__))
    print('Author: {}'.format(handprint.__author__))
    print('URL: {}'.format(handprint.__url__))
    print('License: {}'.format(handprint.__license__))


def save_output(data, file):
    if isinstance(data, str):
        with open(file, 'w') as f:
            f.write(data)
    elif isinstance(data, io.BytesIO):
        with open(file, 'wb') as f:
            shutil.copyfileobj(data, f)


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
