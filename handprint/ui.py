'''ui.py: user interface

Generic framework for simple user interactions in both CLI and GUI programs.

Note: this was originally developed for another program that had a GUI
interface; this copy only has the CLI portion to avoid including unnecessary
imports and unused code in Handprint.

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2019-2020 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import getpass
from   queue import Queue
from   rich import box
from   rich.box import HEAVY
from   rich.console import Console
from   rich.panel import Panel
from   rich.style import Style
from   rich.theme import Theme
import shutil
import sys

if __debug__:
    from sidetrack import set_debug, log, logr

from .exceptions import *


# Constants.
# .............................................................................

_CLI_THEME = Theme({
    'info'        : 'green3',
    'warn'        : 'orange1',
    'warning'     : 'orange1',
    'alert'       : 'red',
    'alert_fatal' : 'bold red',
    'fatal'       : 'bold red',
})


# Exported functions.
# .............................................................................
# These methods get an instance of the UI by themselves and do not require
# callers to do it.  They are meant to be used largely like basic functions
# such as "print()" are used in Python.

def inform(text, *args):
    '''Print an informational message to the user.  The 'text' can contain
    string format placeholders such as "{}", and the additional arguments in
    args are values to use in those placeholders.
    '''
    ui = UI.instance()
    ui.inform(text, *args)


def warn(text, *args):
    '''Warn the user that something is not right.  This should be used in
    situations where the problem is not fatal nor will prevent continued
    execution.  (For problems that prevent continued execution, use the
    alert(...) method instead.)
    '''
    ui = UI.instance()
    ui.warn(text, *args)


def alert(text, *args):
    '''Alert the user to an error.  This should be used in situations where
    there is a problem that will prevent normal execution.
    '''
    ui = UI.instance()
    ui.alert(text, *args)


def alert_fatal(text, *args, **kwargs):
    '''Print or display a message reporting a fatal error.  The keyword
    argument 'details' can be supplied to pass a longer explanation that will
    be displayed (when a GUI is being used) if the user presses the 'Help'
    button in the dialog.

    Note that when a GUI interface is in use, this method will cause the
    GUI to exit after the user clicks the OK button, so that the calling
    application can regain control and exit.
    '''
    ui = UI.instance()
    ui.alert_fatal(text, *args, **kwargs)


def file_selection(type, purpose, pattern = '*'):
    '''Returns the file selected by the user.  The value of 'type' should be
    'open' if the reason for the request is to open a file for reading, and
    'save' if the reason is to save a file.  The argument 'purpose' should be
    a short text string explaining to the user why they're being asked for a
    file.  The 'pattern' is a file pattern expression of the kind accepted by
    wxPython FileDialog.
    '''
    ui = UI.instance()
    return ui.file_selection(type, purpose, pattern)


def login_details(prompt, user, password):
    '''Asks the user for a login name and password.  The value of 'user' and
    'password' will be used as initial values in the dialog.
    '''
    ui = UI.instance()
    return ui.login_details(prompt, user, password)


def confirm(question):
    '''Returns True if the user replies 'yes' to the 'question'.'''
    ui = UI.instance()
    return ui.confirm(question)


# Base class for UI implementations
# .............................................................................
# This class is not meant to be accessed by external code directly.  The
# classes below subclass from this one and provide the actual implementations
# for the methods depending on the type of interface (GUI or CLI).

class UIBase:
    '''Base class for user interface classes.'''

    def __init__(self, name, subtitle, use_gui, use_color, be_quiet):
        ''''name' is the name of the application.  'subtitle' is a short
        string shown next to the name, in the form "name -- subtitle".
        'use_gui' indicates whether a GUI or CLI interface should be used.
        'use_color' applies only to the CLI, and indicates whether terminal
        output should be colored to indicate different kinds of messages.
        Finally, 'be_quiet' also applies only to the CLI and, if True,
        indicates that informational messages should not be printed.
        '''
        self._name      = name
        self._subtitle  = subtitle
        self._use_gui   = use_gui
        self._use_color = use_color
        self._be_quiet  = be_quiet


    def use_gui(self):
        return self._use_gui


    def use_color(self):
        return self._use_color


    def app_name(self):
        return self._name


    def app_subtitle(self):
        return self._subtitle


    # Methods for starting and stopping the interface -------------------------

    def start(self): raise NotImplementedError
    def stop(self):  raise NotImplementedError


    # Methods to show messages to the user ------------------------------------

    def inform(self, text, *args):                    raise NotImplementedError
    def warn(self, text, *args):                      raise NotImplementedError
    def alert(self, text, *args):                     raise NotImplementedError
    def alert_fatal(self, text, *args, **kwargs):     raise NotImplementedError


    # Methods to ask the user -------------------------------------------------

    def file_selection(self, type, purpose, pattern): raise NotImplementedError
    def login_details(self, prompt, user, pswd):      raise NotImplementedError
    def confirm(self, question):                      raise NotImplementedError


# Exported classes.
# .............................................................................
# This class is essentially a wrapper that deals with selecting the real
# class that should be used for the kind of interface being used.  Internally
# it implements a singleton instance, and provides a method to access that
# instance.

class UI(UIBase):
    '''Wrapper class for the user interface.'''

    __instance = None

    def __new__(cls, name, subtitle, use_gui = False, use_color = True, be_quiet = False):
        '''Return an instance of the appropriate user interface handler.'''
        if cls.__instance is None:
            if use_gui:
                from .gui import GUI
                obj = GUI
            else:
                obj = CLI
            cls.__instance = obj(name, subtitle, use_gui, use_color, be_quiet)
        return cls.__instance


    @classmethod
    def instance(cls):
        return cls.__instance


class CLI(UIBase):
    '''Command-line interface.'''


    def __init__(self, name, subtitle,
                 use_gui = False, use_color = True, be_quiet = False):
        UIBase.__init__(self, name, subtitle, use_gui, use_color, be_quiet)
        if __debug__: log('initializing CLI')
        self._started = False

        # If another thread was eager to send messages before we finished
        # initialization, messages will get queued up on this internal queue.
        self._queue = Queue()

        # Initialize output configuration.
        self._console = Console(theme = _CLI_THEME,
                                color_system = "auto" if use_color else None)

        if not be_quiet:
            # We need the plain_text version in any case, to calculate length.
            plain_text = f'Welcome to {name}: {subtitle}'
            fancy_text = f'Welcome to [bold chartreuse1]{name}[/]: {subtitle}'
            text = fancy_text if self._use_color else plain_text
            terminal_width = shutil.get_terminal_size().columns or 80
            padding = (terminal_width - len(plain_text) - 2) // 2
            # Queueing up this message now will make it the 1st thing printed.
            self._print_or_queue(Panel(text, style = 'green3', box = HEAVY,
                                       padding = (0, padding)), style = 'green3')


    def start(self):
        '''Start the user interface.'''
        if __debug__: log('starting CLI')
        while not self._queue.empty():
            (text, style) = self._queue.get()
            self._console.print(text, style = style, highlight = False)
            sys.stdout.flush()
        self._started = True


    def stop(self):
        '''Stop the user interface.'''
        pass


    def _print_or_queue(self, text, style):
        if self._started:
            if __debug__: log(text)
            self._console.print(text, style = style, highlight = False)
        else:
            if __debug__: log(f'queueing message "{text}"')
            self._queue.put((text, style))


    def inform(self, text, *args):
        '''Print an informational message.'''
        if not self._be_quiet:
            self._print_or_queue(text.format(*args), 'info')
        else:
            if __debug__: log(text, *args)


    def warn(self, text, *args):
        '''Print a nonfatal, noncritical warning message.'''
        self._print_or_queue(text.format(*args), style = 'warn')


    def alert(self, text, *args):
        '''Print a message reporting an error.'''
        self._print_or_queue(text.format(*args), style = 'alert')


    def alert_fatal(self, text, *args, **kwargs):
        '''Print a message reporting a fatal error.

        This method returns after execution and does not force an exit of
        the application.  In that sense it mirrors the behavior of the GUI
        version of alert_fatal(...), which also returns, but unlike the GUI
        version, this method does not stop the user interface (because in the
        CLI case, there is nothing equivalent to a GUI to shut down).
        '''
        text += '\n' + kwargs['details'] if 'details' in kwargs else ''
        self._print_or_queue(text.format(*args), style = 'fatal')


    def confirm(self, question):
        '''Asks a yes/no question of the user, on the command line.'''
        return input(f'{question} (y/n) ').startswith(('y', 'Y'))


    def file_selection(self, operation_type, question, pattern):
        '''Ask the user to type in a file path.'''
        return input(operation_type.capitalize() + ' ' + question + ': ')


    def login_details(self, prompt, user = None, pswd = None):
        '''Returns a tuple of user, password, and a Boolean indicating
        whether the user cancelled the dialog.  If 'user' is provided, then
        this method offers that as a default for the user.  If both 'user'
        and 'pswd' are provided, both the user and password are offered as
        defaults but the password is not shown to the user.  If the user
        responds with empty strings, the values returned are '' and not None.
        '''
        try:
            text = (prompt + ' [default: ' + user + ']: ') if user else (prompt + ': ')
            input_user = input(text)
            if len(input_user) == 0:
                input_user = user
            hidden = ' [default: ' + '*'*len(pswd) + ']' if pswd else ''
            text = 'Password' + (' for "' + user + '"' if user else '') + hidden + ': '
            input_pswd = password(text)
            if len(input_pswd) == 0:
                input_pswd = pswd
            final_user = '' if input_user is None else input_user
            final_pswd = '' if input_pswd is None else input_pswd
            return final_user, final_pswd, False
        except (KeyboardInterrupt, UserCancelled):
            return user, pswd, True


class GUI(UIBase):
    '''Graphical user interface.'''
    # Not used in Handprint.
    pass


# Miscellaneous utilities
# .............................................................................

def password(prompt):
    # If it's a tty, use the version that doesn't echo the password.
    if sys.stdin.isatty():
        return getpass.getpass(prompt)
    else:
        sys.stdout.write(prompt)
        sys.stdout.flush()
        return sys.stdin.readline().rstrip()
