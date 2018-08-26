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

import handprint
from handprint.messages import msg, color
from handprint.network import network_available
from handprint.files import files_in_directory, replace_extension, readable
from handprint.google_ocr import GoogleHTR


# Global constants.
# .............................................................................

_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.jp2', '.png', '.tif', '.tiff')


# Main program.
# ......................................................................

@plac.annotations(
    quiet    = ('do not print messages while working', 'flag',   'q'),
    no_color = ('do not color-code terminal output',   'flag',   'C'),
    version  = ('print version info and exit',         'flag',   'V'),
    files    = 'directories and/or files to process',
)

def main(quiet = False, no_color = False, version = False, *files):

    # Our defaults are to do things like color the output, which means the
    # command line flags make more sense as negated values (e.g., "no-color").
    # However, dealing with negated variables in our code is confusing, so:
    use_color   = not no_color

    # Process arguments.
    if version:
        print_version()
        sys.exit()
    if not files:
        raise SystemExit(color('No directories or files given', 'error', use_color))
    if not network_available():
        raise SystemExit(color('No network', 'error', use_color))

    # Let's do this thing.
    todo = []
    for item in files:
        if path.isfile(item) and path.splitext(item)[1] in _IMAGE_EXTENSIONS:
            todo.append(item)
        elif path.isdir(item):
            todo += files_in_directory(item, extensions = _IMAGE_EXTENSIONS)
        else:
            raise ValueError(color('"{}" not a file or directory', 'warn', use_color))
    google = GoogleHTR()
    for file in todo:
        save_output(google.text(file), replace_extension(file, '.g_txt'))

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
    import pdb; pdb.set_trace()
    with open(file, 'w') as f:
        f.write(text)


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
