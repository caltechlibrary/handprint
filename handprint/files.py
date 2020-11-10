'''
files.py: utilities for working with files.

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018-2020 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import io
import os
from   os import path
import re
import shutil
import sys
import subprocess
import tempfile
import webbrowser

if __debug__:
    from sidetrack import set_debug, log, logr

import handprint


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

    # Helper function to test if a directory is writable.
    def dir_writable(dir):
        # This is based on the following Stack Overflow answer by user "zak":
        # https://stackoverflow.com/a/25868839/743730
        try:
            testfile = tempfile.TemporaryFile(dir = dir)
            testfile.close()
        except (OSError, IOError) as e:
            return False
        return True

    if path.exists(dest) and not path.isdir(dest):
        # Path is an existing file.
        return os.access(dest, os.F_OK | os.W_OK)
    elif path.isdir(dest):
        # Path itself is an existing directory.  Is it writable?
        return dir_writable(dest)
    else:
        # Path is a file but doesn't exist yet. Can we write to the parent dir?
        return dir_writable(path.dirname(dest))


def nonempty(dest):
    '''Returns True if the file is not empty.'''
    return os.stat(file).st_size != 0


def module_path():
    '''Returns the absolute path to our module installation directory.'''
    # The path returned by module.__path__ is to the directory containing
    # the __init__.py file.
    this_module = sys.modules[__package__]
    module_path = this_module.__path__[0]
    return path.abspath(module_path)


def handprint_path():
    '''Returns the path to where Handprint is installed.'''
    # The path returned by module.__path__ is to the directory containing
    # the __init__.py file.  What we want here is the path to the installation
    # of the Handprint binary.
    if sys.platform.startswith('win'):
        from winreg import OpenKey, CloseKey, QueryValueEx, HKEY_LOCAL_MACHINE, KEY_READ
        try:
            if __debug__: log('reading Windows registry entry')
            key = OpenKey(HKEY_LOCAL_MACHINE, _HANDPRINT_REG_PATH)
            value, regtype = QueryValueEx(key, 'Path')
            CloseKey(key)
            if __debug__: log(f'path to windows installation: {value}')
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
        if __debug__: log(f'reusing existing directory {dir_path}')
        return
    else:
        if __debug__: log(f'creating directory {dir_path}')
        # If this gets an exception, let it bubble up to caller.
        os.makedirs(dir_path)


def rename_existing(file):
    '''Renames 'file' to 'file.bak'.'''

    def rename(f):
        backup = f + '.bak'
        # If we fail, we just give up instead of throwing an exception.
        try:
            os.rename(f, backup)
            if __debug__: log(f'renamed {file} to {backup}')
        except:
            try:
                delete_existing(backup)
                os.rename(f, backup)
            except:
                if __debug__: log(f'failed to delete {backup}')
                if __debug__: log(f'failed to rename {file} to {backup}')

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
        if __debug__: log(f'doing rmtree on directory {file}')
        try:
            shutil.rmtree(file)
        except:
            if __debug__: log(f'unable to rmtree {file}; will try renaming')
            try:
                rename_existing(file)
            except:
                if __debug__: log(f'unable to rmtree or rename {file}')
    else:
        if __debug__: log(f'doing os.remove on file {file}')
        os.remove(file)


def copy_file(src, dst):
    '''Copy a file from "src" to "dst".'''
    if __debug__: log(f'copying file {src} to {dst}')
    try:
        shutil.copy2(src, dst, follow_symlinks = True)
    except:
        if __debug__: log('shutils.copy2() failed; trying copy()')
        shutil.copy(src, dst, follow_symlinks = True)


def open_file(file):
    '''Open document with default application in Python.'''
    # Code originally from https://stackoverflow.com/a/435669/743730
    if __debug__: log(f'opening file {file}')
    if sys.platform.startswith('darwin'):
        subprocess.call(('open', file))
    elif os.name == 'nt':
        os.startfile(file)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', file))


def open_url(url):
    '''Open the given 'url' in a web browser using the current platform's
    default approach.'''
    if __debug__: log(f'opening url {url}')
    webbrowser.open(url)
