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
try:
    from termcolor import colored
except:
    pass
import time
import traceback

import handprint
from handprint.messages import msg, color
from handprint.network import network_available
from handprint.files import files_in_directory, replace_extension, handprint_path
from handprint.files import readable
from handprint.htr import GoogleHTR
from handprint.htr import MicrosoftHTR
from handprint.exceptions import *
from handprint.debug import set_debug, log


# Global constants.
# .............................................................................

_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')

_METHODS = {
    'google': GoogleHTR,
    'microsoft': MicrosoftHTR,
}


# Main program.
# ......................................................................

@plac.annotations(
    credsdir = ('look for credentials files in directory "D"', 'option', 'c'),
    list     = ('print list of known HTR methods',             'flag',   'l'),
    method   = ('use HTR method "M" (default: "all")',         'option', 'm'),
    quiet    = ('do not print messages while working',         'flag',   'q'),
    no_color = ('do not color-code terminal output',           'flag',   'C'),
    debug    = ('turn on debugging (console only)',            'flag',   'D'),
    version  = ('print version info and exit',                 'flag',   'V'),
    files    = 'directories and/or files to process',
)

def main(credsdir = 'D', list = False, method = 'M', quiet = False,
         no_color = False, debug = False, version = False, *files):
    '''Handprint (a loose acronym of "HANDwritten Page RecognitIoN Test") can
run alternative optical character recognition (OCR) and handwritten text
recognition (HTR) methods on documents.

When invoked, the command-line arguments should end with either one or more
directory names or one or more image files.  Handprint will send each image
file found to OCR/HTR services from Google, Microsoft and others, and write the
text returned by them to text files in the same directories as the images.
The text files will be placed in new directories named after the service being
used; e.g., "microsoft" for the results of using Microsoft's Azure API.

If given the command-line flag -l (or /l on Windows), Handprint will print a
list of the known methods and then exit.  The option -m (/m on Windows) can
be used to select a specific method.  (The default method is "google".)

If given the -V option (/V on Windows), this program will print version
information and exit without doing anything else.
'''

    # Our defaults are to do things like color the output, which means the
    # command line flags make more sense as negated values (e.g., "no-color").
    # However, dealing with negated variables in our code is confusing, so:
    use_color   = not no_color

    # Process arguments.
    if debug:
        set_debug(True)
    if version:
        print_version()
        sys.exit()
    if list:
        msg('Known methods (for use as values for option -m):', 'info', use_color)
        for key in _METHODS.keys():
            msg('   {}'.format(key), 'info', use_color)
        sys.exit()
    if not files:
        raise SystemExit(color('No directories or files given', 'error', use_color))
    if not network_available():
        raise SystemExit(color('No network', 'error', use_color))
    if credsdir == 'D':
        credsdir = path.join(handprint_path(), 'creds')
    if not readable(credsdir):
        raise SystemExit(color('"{}" not readable'.format(credsdir), 'error', use_color))
    else:
        if __debug__: log('Assuming credentials found in {}', credsdir)
    if method == 'M':
        method = 'all'
    if method != 'all' and method.lower() not in _METHODS:
        msg('"{}" is not a known method'.format(method), 'error', use_color)
        sys.exit()
    if not quiet:
        from halo import Halo

    # Create a list of files to be processed.
    files_list = []
    for item in files:
        if path.isfile(item) and path.splitext(item)[1] in _IMAGE_EXTENSIONS:
            files_list.append(item)
        elif path.isdir(item):
            files_list += files_in_directory(item, extensions = _IMAGE_EXTENSIONS)
        else:
            msg('"{}" not a file or directory'.format(item), 'warn', use_color)

    # Let's do this thing.
    methods = _METHODS.values() if method == 'all' else [_METHODS[method.lower()]]
    if method == 'all':
        msg('Applying all methods in succession.', 'info', use_color)
    for method_object in methods:
        if method == 'all':
            msg('='*70, 'dark', use_color)
        run(method_object, files_list, credsdir, use_color, quiet, debug)
    if method == 'all':
        msg('='*70, 'dark', use_color)
    msg('Done.', 'info', use_color)


# If this is windows, we want the command-line args to use slash intead
# of hyphen.

if sys.platform.startswith('win'):
    main.prefix_chars = '/'


# Helper functions.
# ......................................................................

def run(method_object, files_list, credsdir, use_color, quiet, debug):
    spinner = None
    try:
        tool = method_object()
        msg('Using method "{}".'.format(tool.name()), 'info', use_color)
        tool.init_credentials(credsdir)
        for file in files_list:
            if use_color and not quiet:
                spinner = Halo(spinner='bouncingBall', text = color(file, 'info'))
                spinner.start()
            full_path = path.realpath(path.join(os.getcwd(), file))
            file_name = path.basename(full_path)
            dest_dir = path.join(path.dirname(full_path), tool.name())
            if not path.exists(dest_dir):
                if __debug__: log('Creating {}', dest_dir)
                os.makedirs(dest_dir)
            dest_file = replace_extension(path.join(dest_dir, file_name), '.txt')
            save_output(tool.text_from(file), dest_file)
            if use_color and not quiet:
                short_path = path.relpath(dest_file, os.getcwd())
                spinner.succeed(color('{} -> {}'.format(file, short_path), 'info'))
                spinner.stop()
    except (KeyboardInterrupt, UserCancelled) as err:
        if spinner:
            spinner.stop()
        msg('Quitting.', 'info', use_color)
        sys.exit()
    except ServiceFailure as err:
        if spinner:
            spinner.fail(color('Stopping due to a problem', 'error', use_color))
        msg(err, 'error', use_color)
        sys.exit()
    except Exception as err:
        if spinner:
            spinner.fail(color('Stopping due to a problem', 'error', use_color))
        if debug:
            import pdb; pdb.set_trace()
        msg('{}\n{}'.format(str(err), traceback.format_exc()), 'error', use_color)
        sys.exit()


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
