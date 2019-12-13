'''
styled.py: styling text strings

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2019 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''


import colorful
from colorful.core import ColorfulString

colorful.use_256_ansi_colors()

from .debug import log


# Exported classes.
# .............................................................................

class Styled():
    '''Class of methods for styling messages that range from informational
    to critical fatal errors.
    '''

    def __init__(self, apply_styling = True, use_color = True):
        self._style = apply_styling
        self._colorize = use_color


    def info_text(self, text_with_fields, *args):
        '''Return an informational message.'''
        text = text_with_fields.format(*args)
        return styled(text, 'info', self._colorize) if self._style else text


    def warning_text(self, text_with_fields, *args):
        '''Return a nonfatal, noncritical warning message.'''
        text = text_with_fields.format(*args)
        return styled(text, 'warn', self._colorize) if self._style else text


    def error_text(self, text_with_fields, *args):
        '''Return a message reporting an error.'''
        text = text_with_fields.format(*args)
        return styled(text, 'error', self._colorize) if self._style else text


    def fatal_text(self, text_with_fields, *args):
        '''Return a message reporting a fatal error.  Note that this method
        does not exit the program; it leaves that to the caller in case the
        caller needs to perform additional tasks before exiting.
        '''
        text = 'FATAL: ' + text_with_fields.format(*args)
        return styled(text, ['error', 'bold'], self._colorize) if self._style else text


# Utility functions
# .............................................................................

_STYLES_INITIALIZED = False

def styled(text, flags = None, colorize = True):
    '''Style the 'text' according to 'flags' if 'colorize' is True.
    'flags' can be a single string or a list of strings, as follows.
    Explicit colors (when not using a severity color code):
       Colors like 'white', 'blue', 'grey', 'cyan', 'magenta', or other colors
       defined in our text_styles.py
    Additional color flags reserved for message severities:
       'info'  = informational (green)
       'warn'  = warning (yellow)
       'error' = severe error (red)
       'fatal' = really severe error (red, bold, underlined)
    Optional style additions:
       'bold', 'underlined', 'italic', 'blink', 'struckthrough'
    '''
    # Return early if we're not colorizing.
    if not colorize:
        return text

    # Lazy-load the style definitions if needed.
    global _STYLES_INITIALIZED
    if not _STYLES_INITIALIZED:
        from . import text_styles
        _STYLES_INITIALIZED = True
    from .text_styles import _STYLES
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


def unstyled(str):
    '''Remove styling, if any, from the given string.'''
    return str.orig_string if isinstance(str, ColorfulString) else str
