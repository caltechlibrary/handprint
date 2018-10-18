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

import os
from   os import path
from   PIL import Image
import sys
import subprocess
import webbrowser

import handprint
from handprint.constants import ON_WINDOWS
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
    if ON_WINDOWS:
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
    return files


def filename_basename(file):
    parts = file.rpartition('.')
    if len(parts) > 1:
        return ''.join(parts[:-1]).rstrip('.')
    else:
        return file


def filename_extension(file):
    parts = file.rpartition('.')
    if len(parts) > 1:
        return parts[-1]
    else:
        return ''


def replace_extension(filepath, ext):
    return path.splitext(filepath)[0] + ext


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


def convert_image(file, from_format, to_format):
    '''Returns a tuple of (success, error-message).'''
    dest_file = filename_basename(file) + '.' + to_format
    try:
        im = Image.open(file)
        im.save(dest_file, to_format)
        return (True, '')
    except Exception as err:
        return (False, str(err))
