'''
interruptions.py: provide an interruptible wait(...) and related utilities.

This module includes wait(...), a replacement for sleep(...) that is
interruptible and works with multiple threads.  It also provides methods to
cause an interruption, check whether an interruption occurred, and other
related operations.

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2020 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import threading

if __debug__:
    from sidetrack import set_debug, log, logr

from .exceptions import *


# Global variables.
# .............................................................................

__waiter = threading.Event()
'''Internal state variable used to record if an interrupt occurred.'''


# Main functions.
# .............................................................................

def wait(duration):
    '''Wait for "duration" seconds, in a way that can be interrupted.

    This is a replacement for sleep(duration).  If interrupted, this function
    raises the exception UserCancelled.
    '''
    if __debug__: log(f'waiting for {duration} s')
    __waiter.wait(duration)
    if interrupted():
        if __debug__: log(f'raising UserCancelled')
        raise UserCancelled('Interrupted by user')


def interrupt():
    '''Interrupt any waits and internally record an interrupt has occurred.'''
    if __debug__: log(f'interrupting wait')
    __waiter.set()


def interrupted():
    '''Return True if interrupt() has been called and not cleared.'''
    return __waiter.is_set()


def raise_for_interrupts():
    '''Check whether an interrupt occurred; if so, raise UserCancelled.'''
    if interrupted():
        if __debug__: log(f'raising UserCancelled')
        raise UserCancelled('Interrupted by user')


def reset():
    '''Clear the internal marker that an interrupt occurred.'''
    if __debug__: log(f'clearing wait')
    __waiter.clear()
