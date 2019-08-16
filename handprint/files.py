'''
files.py: utilities for working with files.

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
import numpy as np
import os
from   os import path
from   PIL import Image
import re
import shutil
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
    if sys.platform.startswith('win'):
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
        return '.' + parts[-1].lower()
    else:
        return ''


def alt_extension(filepath, ext):
    '''Returns the 'filepath' with the extension replaced by 'ext'.  The
    extension given in 'ext' should NOT have a leading period: that is, it
    should be "foo", not ".foo".'''
    return path.splitext(filepath)[0] + '.' + ext


def filter_by_extensions(item_list, endings):
    if not item_list:
        return []
    if not endings:
        return item_list
    results = item_list
    for ending in endings:
        results = list(filter(lambda name: ending not in name.lower(), results))
    return results


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


def make_dir(dir_path):
    '''Creates directory 'dir_path' (including intermediate directories).'''
    if path.isdir(dir_path):
        if __debug__: log('Reusing existing directory {}', dir_path)
        return
    else:
        if __debug__: log('Creating directory {}', dir_path)
        # If this gets an exception, let it bubble up to caller.
        os.makedirs(dir_path)


def rename_existing(file):
    '''Renames 'file' to 'file.bak'.'''

    def rename(f):
        backup = f + '.bak'
        # If we fail, we just give up instead of throwing an exception.
        try:
            os.rename(f, backup)
            if __debug__: log('renamed {} to {}', file, backup)
        except:
            try:
                delete_existing(backup)
                os.rename(f, backup)
            except:
                if __debug__: log('failed to delete {}', backup)
                if __debug__: log('failed to rename {} to {}', file, backup)

    if path.exists(file):
        rename(file)
        return
    full_path = path.join(os.getcwd(), file)
    if path.exists(full_path):
        rename(full_path)
        return


def delete_existing(file):
    '''Delete the given file.'''
    # Check if it's actually a directory.
    if path.isdir(file):
        if __debug__: log('doing rmtree on directory {}', file)
        try:
            shutil.rmtree(file)
        except:
            if __debug__: log('unable to rmtree {}; will try renaming', file)
            try:
                rename_existing(file)
            except:
                if __debug__: log('unable to rmtree or rename {}', file)
    else:
        if __debug__: log('doing os.remove on file {}', file)
        os.remove(file)


def copy_file(src, dst):
    '''Copy a file from "src" to "dst".'''
    if __debug__: log('copying file {} to {}', src, dst)
    shutil.copy2(src, dst, follow_symlinks = True)


def open_file(file):
    '''Open document with default application in Python.'''
    # Code originally from https://stackoverflow.com/a/435669/743730
    if __debug__: log('opening file {}', file)
    if sys.platform.startswith('darwin'):
        subprocess.call(('open', file))
    elif os.name == 'nt':
        os.startfile(file)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', file))


def open_url(url):
    '''Open the given 'url' in a web browser using the current platform's
    default approach.'''
    if __debug__: log('opening url {}', url)
    webbrowser.open(url)


def image_size(file):
    '''Returns the size of the image in 'file', in units of bytes.'''
    if not file or not readable(file):
        return 0
    return path.getsize(file)


def image_dimensions(file):
    '''Returns the pixel dimensions of the image as a tuple of (width, height).'''
    # When converting images, PIL may issue a DecompressionBombWarning but
    # it's not a concern in our application.  Ignore it.
    if not file:
        return (0, 0)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        im = Image.open(file)
        if not im:
            return (0, 0)
        return im.size


def converted_image(file, to_format, dest_file = None):
    '''Returns a tuple of (success, output file, error message).
    Returns a tuple of (new_file, error).  The value of 'error' will be None
    if no error occurred; otherwise, the value will be a string summarizing the
    error that occurred and 'new_file' will be set to None.
    '''
    if dest_file is None:
        dest_file = filename_basename(file) + '.' + to_format
    # When converting images, PIL may issue a DecompressionBombWarning but
    # it's not a concern in our application.  Ignore it.
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        try:
            im = Image.open(file)
            im.convert('RGB')
            im.save(dest_file, canonical_format_name(to_format))
            if __debug__: log('saved converted image to {}', dest_file)
            return (dest_file, None)
        except Exception as ex:
            return (None, str(ex))


def reduced_image_size(orig_file, dest_file, max_size):
    '''Resizes the image and writes a new file named "ORIGINAL-reduced.EXT".
    Returns a tuple of (new_file, error).  The value of 'error' will be None
    if no error occurred; otherwise, the value will be a string summarizing the
    error that occurred and 'new_file' will be set to None.
    '''
    with warnings.catch_warnings():
        # Catch warnings from image conversion, like DecompressionBombWarning
        warnings.simplefilter('ignore')
        try:
            i_size = image_size(orig_file)
            if i_size <= max_size:
                if __debug__: log('file already smaller than requested: {}', orig_file)
                return (orig_file, None)
            ratio = max_size/i_size
            if __debug__: log('resize ratio = {}', ratio)
            im = Image.open(orig_file)
            dims = im.size
            new_dims = (round(dims[0] * ratio), round(dims[1] * ratio))
            if __debug__: log('resizing image to {}', new_dims)
            resized = im.resize(new_dims, Image.HAMMING)
            resized.save(dest_file)
            if __debug__: log('saved resized image to {}', dest_file)
            return (dest_file, None)
        except Exception as ex:
            return (None, str(ex))


def reduced_image_dimensions(orig_file, dest_file, max_width, max_height):
    '''Resizes the image and writes a new file named "ORIGINAL-reduced.EXT".
    Returns a tuple of (new_file, error).  The value of 'error' will be None
    if no error occurred; otherwise, the value will be a string summarizing the
    error that occurred and 'new_file' will be set to None.
    '''
    with warnings.catch_warnings():
        # Catch warnings from image conversion, like DecompressionBombWarning
        warnings.simplefilter('ignore')
        try:
            im = Image.open(orig_file)
            dims = im.size
            width_ratio = max_width/dims[0]
            length_ratio = max_height/dims[1]
            ratio = min(width_ratio, length_ratio)
            new_dims = (round(dims[0] * ratio), round(dims[1] * ratio))
            if __debug__: log('resizing image to {}', new_dims)
            resized = im.resize(new_dims, Image.HAMMING)
            resized.save(dest_file)
            if __debug__: log('saved re-dimensioned image to {}', dest_file)
            return (dest_file, None)
        except Exception as ex:
            return (None, str(ex))


def canonical_format_name(format):
    '''Convert format name "format" to a consistent version.'''
    format = format.lower()
    if format in ['jpg', 'jpeg']:
        return 'jpeg'
    elif format in ['tiff', 'tif']:
        return 'tiff'
    else:
        return format


# This function was originally based on code posted by user "Maxim" to
# Stack Overflow: https://stackoverflow.com/a/46877433/743730

def create_image_grid(image_files, dest_file, max_horizontal = np.iinfo(int).max):
    '''Create image by tiling a list of images read from files.'''
    n_images = len(image_files)
    n_horiz = min(n_images, max_horizontal)
    h_sizes = [0] * n_horiz
    v_sizes = [0] * ((n_images // n_horiz) + (1 if n_images % n_horiz > 0 else 0))
    images = [Image.open(f) for f in image_files]
    for i, im in enumerate(images):
        h, v = i % n_horiz, i // n_horiz
        h_sizes[h] = max(h_sizes[h], im.size[0])
        v_sizes[v] = max(v_sizes[v], im.size[1])
    h_sizes, v_sizes = np.cumsum([0] + h_sizes), np.cumsum([0] + v_sizes)
    im_grid = Image.new('RGB', (h_sizes[-1], v_sizes[-1]), color = 'white')
    for i, im in enumerate(images):
        im_grid.paste(im, (h_sizes[i % n_horiz], v_sizes[i // n_horiz]))
    im_grid.save(dest_file)
    return im_grid
