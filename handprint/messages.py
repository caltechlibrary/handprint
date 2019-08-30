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
from handprint.debug import log
from handprint.exceptions import *


# Exported classes.
# .............................................................................

class MessageHandler():
    '''Class for printing console messages and asking the user questions.'''

    def __init__(self, use_color, quiet):
        super().__init__()
        self._colorize = use_color
        self._quiet = quiet


    def use_color(self):
        return self._colorize


    def be_quiet(self):
        return self._quiet


    def info_text(self, text, *args):
        '''Prints an informational message.'''
        if not self.be_quiet():
            return styled(text.format(*args), 'info', self._colorize)


    def info(self, text, *args):
        '''Prints an informational message.'''
        if not self.be_quiet():
            print(self.info_text(text, *args), flush = True)


    def warn_text(self, text, *args):
        '''Prints a nonfatal, noncritical warning message.'''
        return styled(text.format(*args), 'warn', self._colorize)


    def warn(self, text, *args):
        '''Prints a nonfatal, noncritical warning message.'''
        print(self.warn_text(text, *args), flush = True)


    def error_text(self, text, *args):
        '''Prints a message reporting a critical error.'''
        return styled(text.format(*args), 'error', self._colorize)


    def error(self, text, *args):
        '''Prints a message reporting a critical error.'''
        print(self.error_text(text, *args), flush = True)


    def fatal_text(self, text, *args):
        '''Prints a message reporting a fatal error.  This method does not
        exit the program; it leaves that to the caller in case the caller
        needs to perform additional tasks before exiting.
        '''
        return styled('FATAL: ' + text.format(*args), ['error', 'bold'], self._colorize)


    def fatal(self, text, *args):
        '''Prints a message reporting a fatal error.  This method does not
        exit the program; it leaves that to the caller in case the caller
        needs to perform additional tasks before exiting.
        '''
        print(self.fatal_text(text, *args), flush = True)


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
    from handprint.messages_styles import _STYLES
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
        else:
            # Color names for colorful have to start with a lower case letter,
            # which is really easy to screw up.  Let's help ourselves.
            c = c[:1].lower() + c[1:]
            try:
                attribs &= getattr(colorful, c)
            except Exception:
                if __debug__: log('colorful does not recognize color {}', c)
    return attribs | text
