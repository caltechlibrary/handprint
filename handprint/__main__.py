'''Handprint: HANDwritten Page RecognitIoN Test for Caltech Archives.

This small project examines the use of alternative optical character
recognition (OCR) and handwritten text recognition (HTR) methods on documents
from the Caltech Archives (http://archives.caltech.edu).  Tests include the
use of Google's OCR capabilities in their Google Cloud Vision API
(https://cloud.google.com/vision/docs/ocr) and Tesseract
(https://en.wikipedia.org/wiki/Tesseract_(software)).

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

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

import handprint
from handprint.messages import msg, color
from handprint.network import network_available
from handprint.files import files_in_directory, replace_extension, readable
from handprint.htr.google import GoogleHTR


# Global constants.
# .............................................................................

_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.jp2', '.png', '.tif', '.tiff')

_ENGINES = {'google': GoogleHTR()}


# Main program.
# ......................................................................

@plac.annotations(
    engine   = ('use HTR engine "E" (default: google)', 'option', 'e'),
    list     = ('list known HTR engines',               'flag',   'l'),
    quiet    = ('do not print messages while working',  'flag',   'q'),
    no_color = ('do not color-code terminal output',    'flag',   'C'),
    version  = ('print version info and exit',          'flag',   'V'),
    files    = 'directories and/or files to process',
)

def main(engine = 'E', list = False,
         quiet = False, no_color = False, version = False, *files):

    # Our defaults are to do things like color the output, which means the
    # command line flags make more sense as negated values (e.g., "no-color").
    # However, dealing with negated variables in our code is confusing, so:
    use_color   = not no_color

    # Process arguments.
    if version:
        print_version()
        sys.exit()
    if list:
        msg('Known engines (use as values for option -e):', 'info', use_color)
        for key in _ENGINES.keys():
            msg('   {}'.format(key), 'info', use_color)
        sys.exit()
    if not files:
        raise SystemExit(color('No directories or files given', 'error', use_color))
    if not network_available():
        raise SystemExit(color('No network', 'error', use_color))
    if engine == 'E':
        engine = 'google'
    if not quiet:
        from halo import Halo

    # Let's do this thing.
    todo = []
    for item in files:
        if path.isfile(item) and path.splitext(item)[1] in _IMAGE_EXTENSIONS:
            todo.append(item)
        elif path.isdir(item):
            todo += files_in_directory(item, extensions = _IMAGE_EXTENSIONS)
        else:
            msg('"{}" not a file or directory'.format(item), 'warn', use_color)
    if engine in _ENGINES:
        htrengine = _ENGINES[engine]
    else:
        msg('"{}" is not known'.format(engine), 'error', use_color)
        sys.exit()

    if not quiet:
        msg('Using HTR engine "{}".'.format(engine), 'info', use_color)
    for file in todo:
        full_path = path.realpath(path.join(os.getcwd(), file))
        file_dir = path.dirname(full_path)
        file_name = path.basename(full_path)
        dest_dir = path.join(file_dir, engine)
        if not path.exists(dest_dir):
            os.makedirs(dest_dir)
        dest_file = replace_extension(path.join(dest_dir, file_name), '.txt')
        if use_color:
            with Halo(spinner='bouncingBall', enabled = not quiet):
                msg('"{}" -> "{}"'.format(file, dest_file), 'info', use_color)
                save_output(htrengine.text_from(file), dest_file)
        else:
            msg('"{}" -> "{}"'.format(file, dest_file))
            save_output(htrengine.text_from(file), dest_file)

    msg('Done.', 'info', use_color)


# If this is windows, we want the command-line args to use slash intead
# of hyphen.

if sys.platform.startswith('win'):
    main.prefix_chars = '/'


# Miscellaneous utilities.
# ......................................................................

def print_version():
    print('{} version {}'.format(turf.__title__, turf.__version__))
    print('Author: {}'.format(turf.__author__))
    print('URL: {}'.format(turf.__url__))
    print('License: {}'.format(turf.__license__))


def save_output(text, file):
    with open(file, 'w') as f:
        f.write(text)

# init_halo_hack() is mostly a guess at a way to keep the first part of the
# spinner printed by Halo from overwriting part of the first message we
# print.  It seems to work, but the problem that this tries to solve occurred
# sporadically anyway, so maybe the issue still remains and I just haven't
# seen it happen again.

def init_halo_hack():
    '''Write a blank to prevent occasional garbled first line printed by Halo.'''
    sys.stdout.write('')
    sys.stdout.flush()
    time.sleep(0.1)


# Main entry point.
# ......................................................................
# The following allows users to invoke this using "python3 -m turf".

if __name__ == '__main__':
    plac.call(main)


# For Emacs users
# ......................................................................
# Local Variables:
# mode: python
# python-indent-offset: 4
# End:
