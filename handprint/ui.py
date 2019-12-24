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

Copyright (c) 2019 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import getpass
import os
import os.path as path
import sys
from   time import sleep

from .debug import log
from .exceptions import *
from .files import readable
from .styled import Styled, unstyled


# Exported functions
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
    if not ui.use_color():
        text = unstyled(text)
        args = [unstyled(x) for x in args]
    ui.inform(text, *args)


def warn(text, *args):
    '''Warn the user that something is not right.  This should be used in
    situations where the problem is not fatal nor will prevent continued
    execution.  (For problems that prevent continued execution, use the
    alert(...) method instead.)
    '''
    ui = UI.instance()
    if not ui.use_color():
        text = unstyled(text)
        args = [unstyled(x) for x in args]
    ui.warn(text, *args)


def alert(text, *args):
    '''Alert the user to an error.  This should be used in situations where
    there is a problem that will prevent normal execution.
    '''
    ui = UI.instance()
    if not ui.use_color():
        text = unstyled(text)
        args = [unstyled(x) for x in args]
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
    if not ui.use_color():
        text = unstyled(text)
        args = [unstyled(x) for x in args]
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

    def __new__(cls, name, subtitle, use_gui, use_color, be_quiet):
        '''Return an instance of the appropriate user interface handler.'''
        if cls.__instance is None:
            obj = GUI if use_gui else CLI
            cls.__instance = obj(name, subtitle, use_gui, use_color, be_quiet)
        return cls.__instance


    @classmethod
    def instance(cls):
        return cls.__instance


class CLI(UIBase, Styled):
    '''Command-line interface.'''

    def __init__(self, name, subtitle, use_gui, use_color, be_quiet):
        UIBase.__init__(self, name, subtitle, use_gui, use_color, be_quiet)
        Styled.__init__(self, apply_styling = not use_gui, use_color = use_color)


    def start(self):
        '''Start the user interface.'''
        pass


    def stop(self):
        '''Stop the user interface.'''
        pass


    def inform(self, text, *args):
        '''Print an informational message.'''
        if __debug__: log(text, *args)
        if not self._be_quiet:
            print(self.info_text(text, *args), flush = True)


    def warn(self, text, *args):
        '''Print a nonfatal, noncritical warning message.'''
        if __debug__: log(text, *args)
        print(self.warning_text(text, *args), flush = True)


    def alert(self, text, *args):
        '''Print a message reporting an error.'''
        if __debug__: log(text, *args)
        print(self.error_text(text, *args), flush = True)


    def alert_fatal(self, text, *args, **kwargs):
        '''Print a message reporting a fatal error.

        This method returns after execution and does not force an exit of
        the application.  In that sense it mirrors the behavior of the GUI
        version of alert_fatal(...), which also returns, but unlike the GUI
        version, this method does not stop the user interface (because in the
        CLI case, there is nothing equivalent to a GUI to shut down).
        '''
        if __debug__: log(text, *args)
        text += '\n' + kwargs['details'] if 'details' in kwargs else ''
        print(self.fatal_text(text, *args), flush = True)


    def confirm(self, question):
        '''Asks a yes/no question of the user, on the command line.'''
        return input("{} (y/n) ".format(question)).startswith(('y', 'Y'))


    def file_selection(self, operation_type, question, pattern):
        '''Ask the user to type in a file path.'''
        return input(operation_type.capitalize() + ' ' + question + ': ')


    def login_details(self, prompt, user = None, pswd = None):
        '''Returns a tuple of user, password, and a Boolean indicating
        whether the user cancelled the dialog.  If 'user' is provided, then
        this method offers that as a default for the user.  If both 'user'
        and 'pswd' are provided, both the user and password are offered as
        defaults but the password is not shown to the user.
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
            return input_user, input_pswd, False
        except KeyboardInterrupt:
            return user, pswd, True


class GUI(UIBase, Styled):
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
