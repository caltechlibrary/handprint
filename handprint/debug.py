'''
debug.py: lightweight debug logging facility

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2019 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

# Everything is carefully conditionalized on __debug__.  This is meant to
# minimize the performance impact of this module by eliding everything when
# Python is running with the optimization flag -O.


# Logger configuration.
# .............................................................................

if __debug__:
    import inspect
    import logging
    from   os import path
    import sys

    # This next global variable makes a huge speed difference. It lets us avoid
    # calling logging.getLogger('packagename').isEnabledFor(logging.DEBUG)
    # at runtime in log() to test whether debugging is turned on.
    setattr(sys.modules[__package__], '_debugging', False)


# Exported functions.
# .............................................................................

def set_debug(enabled, dest = '-'):
    '''Turns on debug logging if 'enabled' is True; turns it off otherwise.
    Optional argument 'dest' changes the debug output to the given destination.
    The value can be a file path, or a single dash ('-') to indicate the
    console (standard output).  The default destination is the console.  For
    simplicity, only one destination is allowed at given a time; calling this
    function multiple times with different destinations simply switches the
    destination to the latest one.
    '''
    if __debug__:
        from logging import DEBUG, WARNING, FileHandler, StreamHandler
        setattr(sys.modules[__package__], '_debugging', enabled)

        # Set the appropriate output destination if we haven't already.
        if enabled:
            logger    = logging.getLogger(__package__)
            formatter = logging.Formatter('%(name)s %(message)s')
            # We only allow one active destination.
            for h in logger.handlers:
                logger.removeHandler(h)
            # We treat empty dest values as meaning "the default output".
            if dest in ['-', '', None]:
                handler = StreamHandler()
            else:
                handler = FileHandler(dest)
            handler.setFormatter(formatter)
            handler.setLevel(DEBUG)
            logger.addHandler(handler)
            logger.setLevel(DEBUG)
            setattr(sys.modules[__package__], '_logger', logger)
        elif getattr(sys.modules[__package__], '_logger'):
            logger = logging.getLogger(__package__)
            logger.setLevel(WARNING)


def log(s, *other_args):
    '''Logs a debug message. 's' can contain format directive, and the
    remaining arguments are the arguments to the format string.
    '''
    if __debug__:
        # This test for the level may seem redundant, but it's not: it prevents
        # the string format from always being performed if logging is not
        # turned on and the user isn't running Python with -O.
        if getattr(sys.modules[__package__], '_debugging'):
            func = inspect.currentframe().f_back.f_code.co_name
            file_path = inspect.currentframe().f_back.f_code.co_filename
            filename = path.basename(file_path)
            logging.getLogger(__package__).debug('{} {}(): '.format(filename, func)
                                                 + s.format(*other_args))
