'''
progress.py: show indication of progresss

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from   halo import Halo
import sys
import time

try:
    from termcolor import colored
    if sys.platform.startswith('win'):
        import colorama
        colorama.init()
except:
    pass

import handprint
from handprint.messages import color, msg
from handprint.debug import log


class ProgressIndicator():

    def __init__(self, colorize, quiet):
        self._colorize = colorize
        self._quiet = quiet
        self._current_message = ''


    def start(self, message = None):
        if self._quiet:
            return
        if message is None:
            message = ''
        if self._colorize:
            text = color(message, 'info')
            self._spinner = Halo(spinner='bouncingBall', text = text)
            self._spinner.start()
            self._current_message = message
        else:
            msg(message)


    def update(self, message = None):
        if self._quiet:
            return
        if self._colorize:
            if self._current_message:
                self._spinner.succeed(color(self._current_message, 'info', self._colorize))
            self._spinner.stop()
            self.start(message)
        else:
            msg(message)


    def warn(self, message = None):
        if self._quiet:
            return
        if self._colorize:
            self._spinner.succeed(color(self._current_message, 'info', self._colorize))
            self._spinner.stop()
            self._spinner.warn(color(message, 'warn', self._colorize))
            self._current_message = ''
        else:
            msg('WARNING: ' + message)


    def stop(self, message = None):
        if self._quiet:
            return
        if self._colorize:
            if self._current_message:
                self._spinner.succeed(color(self._current_message, 'info', self._colorize))
            self._spinner.stop()
            self.start(message)
            self._spinner.succeed(color(message, 'info', self._colorize))
            self._spinner.stop()
        else:
            msg(message)


    def fail(self, message = None):
        if self._colorize:
            self._spinner.fail(color(self._current_message, 'error', self._colorize))
            self._spinner.stop()
            self.start(message)
            self._spinner.fail(color(message, 'error', self._colorize))
            self._spinner.stop()
        else:
            msg('ERROR: ' + message)
