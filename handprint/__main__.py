'''Handprint: HANDwritten Page RecognitIoN Test for Caltech Archives.

This project uses alternative optical character recognition (OCR) and
handwritten text recognition (HTR) methods on documents from the Caltech
Archives (http://archives.caltech.edu).  Tests include the use of Google's
OCR capabilities in their Google Cloud Vision API
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
import traceback
from   urllib import request
import wget

import handprint
from handprint.constants import ON_WINDOWS, IMAGE_FORMATS, KNOWN_METHODS
from handprint.messages import msg, color, MessageHandlerCLI
from handprint.network import network_available
from handprint.files import files_in_directory, replace_extension, handprint_path
from handprint.files import readable, writable, filename_extension
from handprint.htr import GoogleHTR
from handprint.htr import MicrosoftHTR
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
run alternative optical character recognition (OCR) and handwritten text
recognition (HTR) methods on images of document pages.

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
either in the same directories as the original files or if given the -o
option (/o on Windows), to the directory indicated by the argument to the -o
option.  The results will be written in files named after the original files
with the addition of a string that indicates the service used.  For example,
a file named "somefile.jpg" will produce

  somefile.jpg
  somefile.google.txt
  somefile.microsoft.txt
  somefile.amazon.txt
  ...

and so on for each image and each service used.  Note that if -u (/u on
Windows) is given, then an output directory MUST also be specified using the
option -o (/o on Windows) because it is not possible to write the results in
the network locations represented by the URLs.  Also, when -u is used, the
images and text results will be stored in files whose root names have the
form "document-N", where "N" is an integer.  The root name can be changed
using the -r option (/r on Windows).

If given the command-line flag -l (or /l on Windows), Handprint will print a
list of the known methods and then exit.  The option -m (/m on Windows) can
be used to select a specific method.  (The default method is "google".)

Note: the only image formats recognized are JPG, PNG, GIF, and BMP.

Credentials for different services need to be provided to Handprint in the
form of JSON files.  Each service needs a separate JSON file named after the
service (e.g., "microsoft.json") and placed in a directory that Handprint
searches.  By default, Handprint searches for the files in a subdirectory
named "creds" where Handprint is installed, but an alternative directory can
be indicated at run-time using the -c command-line option (/c on Windows).
The specific format of each credentials file is different for each service;
please consult the Handprint documentation for more details.

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

    if creds_dir == 'D':
        creds_dir = path.join(handprint_path(), 'creds')
    if not readable(creds_dir):
        exit(say.error_text('Directory not readable: {}'.format(creds_dir)))
    else:
        if __debug__: log('Assuming credentials found in "{}".', creds_dir)

    if method == 'M':
        method = 'all'
    method = method.lower()
    if method != 'all' and method not in KNOWN_METHODS:
        exit(say.error_text('"{}" is not a known method. {}'.format(method, hint)))

    if not images and not from_file:
        exit(say.error_text('Need provide images or URLs. {}'.format(hint)))
    if any(item.startswith('-') for item in images):
        exit(say.error_text('Unrecognized option in arguments. {}'.format(hint)))

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
            if __debug__: log('Created output directory "{}"', output)
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
        exit(say.error_text(err))
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
    spinner = None
    try:
        tool = method_class()
        say.info('Using method "{}".'.format(tool.name()))
        tool.init_credentials(creds_dir)
        for index, item in enumerate(targets, 1):
            if not given_urls and (item.startswith('http') or item.startswith('ftp')):
                say.warn('Skipping URL "{}"'.format(item))
                continue
            if say.use_color() and not say.be_quiet():
                spinner = Halo(spinner='bouncingBall', text = color(item, 'info'))
                spinner.start()
            if given_urls:
                # Make sure the URLs point to images.
                response = request.urlopen(item)
                if response.headers.get_content_maintype() != 'image':
                    spinner.fail(say.error_text(
                        'Did not find an image at "{}"'.format(item)))
                    continue
                format = response.headers.get_content_subtype()
                if format not in IMAGE_FORMATS:
                    spinner.fail(say.error_text(
                        'Cannot use image format {} in "{}"'.format(format, item)))
                    continue
                # If we're given URLs, we have to invent file names to store
                # the images and the OCR results.
                base = '{}-{}'.format(root_name, index)
                url_file = path.realpath(path.join(output_dir, base + '.url'))
                if __debug__: log('Writing URL to {}', url_file)
                with open(url_file, 'w') as f:
                    f.write(url_file_content(item))
                if __debug__: log('Starting wget on {}', item)
                downloaded = wget.download(item, bar = None, out = output_dir)
                file = path.realpath(path.join(output_dir, base + '.' + format))
                if __debug__: log('Renaming downloaded file to {}', file)
                os.rename(downloaded, file)
                full_path = file
            else:
                file = item
                full_path = path.realpath(path.join(os.getcwd(), file))
            file_name = path.basename(full_path)
            if output_dir:
                dest_dir = output_dir
            else:
                dest_dir = path.dirname(full_path)
                if not writable(dest_dir):
                    say.fatal('Cannot write output in "{}".'.format(dest_dir))
                    return
            dest_file = replace_extension(path.join(dest_dir, file_name),
                                          '.' + tool.name() + '.txt')
            save_output(tool.text_from(file), dest_file)
            if say.use_color() and not say.be_quiet():
                short_path = path.relpath(dest_file, os.getcwd())
                spinner.succeed(color('{} -> {}'.format(file, short_path), 'info'))
                spinner.stop()
    except (KeyboardInterrupt, UserCancelled) as err:
        if spinner:
            spinner.stop()
        raise
    except ServiceFailure as err:
        if spinner:
            spinner.fail(say.error_text('Stopping due to a problem'))
        raise
    except Exception as err:
        if spinner:
            spinner.fail(say.error_text('Stopping due to a problem'))
        raise


def targets_from_arguments(images, from_file, given_urls, say):
    targets = []
    if from_file:
        with open(from_file) as f:
            targets = f.readlines()
        targets = [line.rstrip('\n') for line in targets]
        if __debug__: log('Read {} lines from "{}".', len(targets), from_file)
        if not given_urls:
            targets = filter_urls(targets, say)
    elif given_urls:
        # We assume that the arguments are URLs and take them as-is.
        targets = images
    else:
        # We were given files and/or directories.  Look for image files.
        for item in filter_urls(images, say):
            if path.isfile(item) and filename_extension(item) in IMAGE_FORMATS:
                targets.append(item)
            elif path.isdir(item):
                targets += files_in_directory(item, extensions = IMAGE_FORMATS)
            else:
                say.warn('"{}" not a file or directory'.format(item))
    return targets


def filter_urls(item_list, say):
    results = []
    for item in item_list:
        if item.startswith('http') or item.startswith('ftp'):
            say.warn('Unexpected URL: "{}"'.format(item))
            continue
        else:
            results.append(item)
    return results


def url_file_content(url):
    return '[InternetShortcut]\nURL={}\n'.format(url)


def print_version():
    print('{} version {}'.format(handprint.__title__, handprint.__version__))
    print('Author: {}'.format(handprint.__author__))
    print('URL: {}'.format(handprint.__url__))
    print('License: {}'.format(handprint.__license__))


def save_output(text, file):
    with open(file, 'w') as f:
        f.write(text)

# init_halo_hack() is mostly a guess at a way to keep the first part of the
# spinner printed by Halo from overwriting part of the first message we
# print.  It seems to work, but the problem that this tries to solve occurred
# sporadically anyway, so maybe the issue still remains and I just haven't
# seen it happen again.

def init_halo_hack():

    '''Write a blank to prevent occasional garbled first line printed by
    Halo.'''
    sys.stdout.write('')
    sys.stdout.flush()
    time.sleep(0.1)


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
