'''
files.py: utilities for working with files.
'''

import os
from   os import path
import sys
import subprocess
import webbrowser

import handprint


# Main functions.
# .............................................................................

def readable(file):
    '''Returns True if the given 'file' is accessible and readable.'''
    return os.access(file, os.F_OK | os.R_OK)


def module_path():
    '''Returns the absolute path to our module installation directory.'''
    # The path returned by module.__path__ is to the directory containing
    # the __init__.py file.
    return path.abspath(handprint.__path__[0])


def files_in_directory(dir, extensions = None):
    if not path.isdir(dir):
        return []
    if not readable(dir):
        return []
    files = []
    for item in os.listdir(dir):
        full_path = path.join(dir, item)
        if path.isfile(full_path) and readable(full_path):
            if extensions and path.splitext(item)[1] in extensions:
                files.append(full_path)
    return files


def replace_extension(filepath, ext):
    return path.splitext(filepath)[0] + ext


def rename_existing(file, notifier):
    def rename(f):
        backup = f + '.bak'
        # If we fail, we just give up instead of throwing an exception.
        try:
            os.rename(f, backup)
        except:
            return
        notifier.msg('Renamed existing file "{}" to "{}"'.format(f, backup),
                     'To avoid overwriting the existing file "{}", '.format(f)
                     + 'it has been renamed to "{}"'.format(backup),
                     'info')

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
    webbrowser.open(url)
