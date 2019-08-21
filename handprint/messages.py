'''
messages: message-printing utilities for Handprint

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018-2019 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import colorful
colorful.use_256_ansi_colors()

import sys

import handprint
from handprint.exceptions import *


# Exported classes.
# .............................................................................
# The basic principle of writing the classes (like this one) that get used
# elsewhere is that they should take the information they need.  This means,
# for example, that 'use_color' is handed to the CLI version of this object,
# not to the base class class, even though use_color is something that may be
# relevant to more than one of the main classes.  This is a matter of
# separation of concerns and information hiding.

class MessageHandlerBase():
    '''Base class for message-printing classes in Handprint!'''

    def __init__(self):
        pass


class MessageHandlerCLI(MessageHandlerBase):
    '''Class for printing console messages and asking the user questions.'''

    def __init__(self, use_color, quiet):
        super().__init__()
        self._colorize = use_color
        self._quiet = quiet


    def use_color(self):
        return self._colorize


    def be_quiet(self):
        return self._quiet


    def info_text(self, text, details = ''):
        '''Prints an informational message.'''
        if not self.be_quiet():
            return styled(text, 'info', self._colorize)


    def info(self, text, details = ''):
        '''Prints an informational message.'''
        if not self.be_quiet():
            print(self.info_text(text, details), flush = True)


    def warn_text(self, text, details = ''):
        '''Prints a nonfatal, noncritical warning message.'''
        return styled('Warning: ' + text, 'warn', self._colorize)


    def warn(self, text, details = ''):
        '''Prints a nonfatal, noncritical warning message.'''
        print(self.info_text(text, details), flush = True)


    def error_text(self, text, details = ''):
        '''Prints a message reporting a critical error.'''
        return styled('Error: ' + text, 'error', self._colorize)


    def error(self, text, details = ''):
        '''Prints a message reporting a critical error.'''
        print(self.error_text(text, details), flush = True)


    def fatal_text(self, text, details = ''):
        '''Prints a message reporting a fatal error.  This method does not
        exit the program; it leaves that to the caller in case the caller
        needs to perform additional tasks before exiting.
        '''
        return styled('FATAL: ' + text, 'fatal', self._colorize)


    def fatal(self, text, details = ''):
        '''Prints a message reporting a fatal error.  This method does not
        exit the program; it leaves that to the caller in case the caller
        needs to perform additional tasks before exiting.
        '''
        print(self.fatal_text(text, details), flush = True)


    def yes_no(self, question):
        '''Asks a yes/no question of the user, on the command line.'''
        return input("{} (y/n) ".format(question)).startswith(('y', 'Y'))


    def msg_text(self, text, flags = None):
        return styled(text, flags, self._colorize)


    def msg(self, text, flags = None):
        print(self.msg_text(text, flags), flush = True)


# Message utility funcions.
# .............................................................................

_STYLES_INITIALIZED = False

def styled(text, flags = None, colorize = True):
    '''Style the 'text' according to 'flags' if 'colorize' is True.
    'flags' can be a single string or a list of strings, as follows.
    Explicit colors (when not using a severity color code):
       Colors like 'white', 'blue', 'grey', 'cyan', 'magenta', or other colors
       defined in our messages_styles.py
    Additional color flags reserved for message severities:
       'info'  = informational (green)
       'warn'  = warning (yellow)
       'error' = severe error (red)
       'fatal' = really severe error (red, bold, underlined)
    Optional style additions:
       'bold', 'underlined', 'italic', 'blink', 'struckthrough'
    '''
    # Fail early if we're not colorizing.
    if not colorize:
        return text

    # Lazy-load the style definitions if needed.
    global _STYLES_INITIALIZED
    if not _STYLES_INITIALIZED:
        import handprint.messages_styles
        _STYLES_INITIALIZED = True
    from handprint.messages_styles import _STYLES, _COLORS
    if type(flags) is not list:
        flags = [flags]

    # Use colorful's clever and-or overloading mechanism to concatenate the
    # style definition, apply it to the text, and return the result.
    attribs = colorful.reset
    for c in flags:
        if c == 'reset':
            attribs &= colorful.reset
        elif c in _STYLES:
            attribs &= _STYLES[c]
        elif c in _COLORS:
            attribs &= getattr(colorful, c.lower())
    return attribs | text
