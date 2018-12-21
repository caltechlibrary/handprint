'''
files.py: utilities for working with files.

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import io
import os
from   os import path
from   PIL import Image
import re
import sys
import subprocess
import warnings
import webbrowser

import handprint
from handprint.debug import log


# Constants.
# .............................................................................

_HANDPRINT_REG_PATH = r'Software\Caltech Library\Handprint\Settings'


# Main functions.
# .............................................................................

def readable(dest):
    '''Returns True if the given 'dest' is accessible and readable.'''
    return os.access(dest, os.F_OK | os.R_OK)


def writable(dest):
    '''Returns True if the destination is writable.'''
    return os.access(dest, os.F_OK | os.W_OK)


def module_path():
    '''Returns the absolute path to our module installation directory.'''
    # The path returned by module.__path__ is to the directory containing
    # the __init__.py file.
    return path.abspath(handprint.__path__[0])


def handprint_path():
    '''Returns the path to where Handprint is installed.'''
    # The path returned by module.__path__ is to the directory containing
    # the __init__.py file.  What we want here is the path to the installation
    # of the Handprint binary.
    if sys.platform.startswith('win'):
        from winreg import OpenKey, CloseKey, QueryValueEx, HKEY_LOCAL_MACHINE, KEY_READ
        try:
            if __debug__: log('Reading Windows registry entry')
            key = OpenKey(HKEY_LOCAL_MACHINE, _HANDPRINT_REG_PATH)
            value, regtype = QueryValueEx(key, 'Path')
            CloseKey(key)
            if __debug__: log('Path to windows installation: {}'.format(value))
            return value
        except WindowsError:
            # Kind of a problem. Punt and return a default value.
            return path.abspath('C:\Program Files\Handprint')
    else:
        return path.abspath(path.join(module_path(), '..'))


def desktop_path():
    '''Returns the path to the user's desktop directory.'''
    if ON_WINDOWS:
        return path.join(path.join(os.environ['USERPROFILE']), 'Desktop')
    else:
        return path.join(path.join(path.expanduser('~')), 'Desktop')


def files_in_directory(dir, extensions = None):
    if not path.isdir(dir):
        return []
    if not readable(dir):
        return []
    files = []
    for item in os.listdir(dir):
        full_path = path.join(dir, item)
        if path.isfile(full_path) and readable(full_path):
            if extensions and filename_extension(item) in extensions:
                files.append(full_path)
    return sorted(files)


def filename_basename(file):
    parts = file.rpartition('.')
    if len(parts) > 1:
        return ''.join(parts[:-1]).rstrip('.')
    else:
        return file


def filename_extension(file):
    parts = file.rpartition('.')
    if len(parts) > 1:
        return parts[-1].lower()
    else:
        return ''


def alt_extension(filepath, ext):
    '''Returns the 'filepath' with the extension replaced by 'ext'.  The
    extension given in 'ext' should NOT have a leading period: that is, it
    should be "foo", not ".foo".'''
    return path.splitext(filepath)[0] + '.' + ext


def is_url(string):
    '''Return True if the 'string' looks like a URL, False otherwise.'''
    return re.match(r'^[a-zA-Z]+:/', string)


def relative(file):
    '''Returns a path that is relative to the current directory.  If the
    relative path would require more than one parent step (i.e., ../../*
    instead of ../*) then it will return an absolute path instead.  If the
    argument is actuall a file path, it will return it unchanged.'''
    if is_url(file):
        return file
    candidate = path.relpath(file, os.getcwd())
    if not candidate.startswith('../..'):
        return candidate
    else:
        return path.realpath(candidate)


def rename_existing(file):
    '''Renames 'file' to 'file.bak'.'''

    def rename(f):
        backup = f + '.bak'
        # If we fail, we just give up instead of throwing an exception.
        try:
            if __debug__: log('Renaming existing file {}', f)
            os.rename(f, backup)
        except:
            return

    if path.exists(file):
        rename(file)
        return
    full_path = path.join(os.getcwd(), file)
    if path.exists(full_path):
        rename(full_path)
        return


def open_file(file):
    '''Open document with default application in Python.'''
    # Code originally from https://stackoverflow.com/a/435669/743730
    if sys.platform.startswith('darwin'):
        subprocess.call(('open', file))
    elif os.name == 'nt':
        os.startfile(file)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', file))


def open_url(url):
    '''Open the given 'url' in a web browser using the current platform's
    default approach.'''
    webbrowser.open(url)


def image_size(file):
    '''Returns the size of the image in 'file', in units of bytes.'''
    return path.getsize(file)


def image_dimensions(file):
    '''Returns the pixel dimensions of the image as a tuple of (width, height).'''
    # When converting images, PIL may issue a DecompressionBombWarning but
    # it's not a concern in our application.  Ignore it.
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        im = Image.open(file)
        return im.size


def converted_image(file, to_format):
    '''Returns a tuple of (success, output file, error message).
    Returns a tuple of (new_file, error).  The value of 'error' will be None
    if no error occurred; otherwise, the value will be a string summarizing the
    error that occurred and 'new_file' will be set to None.
    '''
    dest_file = filename_basename(file) + '.' + to_format
    # When converting images, PIL may issue a DecompressionBombWarning but
    # it's not a concern in our application.  Ignore it.
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        try:
            im = Image.open(file)
            im.save(dest_file, canonical_format_name(to_format))
            if __debug__: log('Saved converted image to {}', dest_file)
            return (dest_file, None)
        except Exception as ex:
            return (None, str(ex))


def reduced_image(file, max_dimensions):
    '''Resizes the image and writes a new file named "ORIGINAL-reduced.EXT".
    Returns a tuple of (new_file, error).  The value of 'error' will be None
    if no error occurred; otherwise, the value will be a string summarizing the
    error that occurred and 'new_file' will be set to None.
    '''
    extension = filename_extension(file)
    dest_file = filename_basename(file) + '-reduced.' + extension
    with warnings.catch_warnings():
        # Catch warnings from image conversion, like DecompressionBombWarning
        warnings.simplefilter('ignore')
        try:
            im = Image.open(file)
            dims = im.size
            width_ratio = max_dimensions[0]/dims[0]
            length_ratio = max_dimensions[1]/dims[1]
            ratio = min(width_ratio, length_ratio)
            new_dims = (round(dims[0] * ratio), round(dims[1] * ratio))
            if __debug__: log('Resizing image to {}', new_dims)
            resized = im.resize(new_dims, Image.HAMMING)
            resized.save(dest_file)
            if __debug__: log('Saved converted image to {}', dest_file)
            return (dest_file, None)
        except Exception as ex:
            return (None, str(ex))


def canonical_format_name(format):
    format = format.lower()
    if format in ['jpg', 'jpeg']:
        return 'jpeg'
    elif format in ['tiff', 'tif']:
        return 'tiff'
    else:
        return format
