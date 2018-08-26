'''
messages: message-printing utilities for Handprint.

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import sys
import wx
import wx.lib.dialogs

try:
    from termcolor import colored
    if sys.platform.startswith('win'):
        import colorama
        colorama.init()
except:
    pass

import handprint


# Class definitions.
# ......................................................................

class MessageHandlerCLI():
    colorize = True
    on_windows = sys.platform.startswith('win')

    def __init__(self, use_color = True):
        self.colorize = use_color


    def note(self, text):
        msg(text, 'info', self.colorize)


    def msg(self, text, details = '', severity = 'info'):
        msg(text, severity, self.colorize)


    def yes_no(self, question):
        return input("{} (y/n) ".format(question)).startswith(('y', 'Y'))


class MessageHandlerGUI():
    def __init__(self):
        pass


    def note(self, text):
        '''Displays a simple notice with a single OK button.'''
        app = wx.App()
        frame = wx.Frame(None)
        frame.Center()
        dlg = wx.GenericMessageDialog(frame, text, caption = "Handprint!",
                                      style = wx.OK | wx.ICON_INFORMATION)
        clicked = dlg.ShowModal()
        dlg.Destroy()
        frame.Destroy()


    def msg(self, text, details = '', severity = 'error'):
        # When running with a GUI, we only bring up error dialogs.
        if 'info' in severity:
            return
        app = wx.App()
        frame = wx.Frame(None)
        frame.Center()
        if 'fatal' in severity:
            short = text
            style = wx.OK | wx.HELP | wx.ICON_ERROR
        else:
            short = text + '\n\nWould you like to try to continue?\n(Click "no" to quit now.)'
            style = wx.YES_NO | wx.YES_DEFAULT | wx.HELP | wx.ICON_EXCLAMATION
        dlg = wx.MessageDialog(frame, message = short, style = style,
                               caption = "Handprint encountered a problem")
        clicked = dlg.ShowModal()
        if clicked == wx.ID_HELP:
            body = ("Handprint has encountered an error:\n"
                    + "─"*30
                    + "\n{}\n".format(details)
                    + "─"*30
                    + "\nIf the problem is due to a network timeout or "
                    + "similar transient error, then please quit and try again "
                    + "later. If you don't know why the error occurred or "
                    + "if it is beyond your control, please also notify the "
                    + "developers. You can reach the developers via email:\n\n"
                    + "    Email: mhucka@library.caltech.edu\n")
            info = wx.lib.dialogs.ScrolledMessageDialog(frame, body, "Error")
            info.ShowModal()
            info.Destroy()
            frame.Destroy()
        elif clicked in [wx.ID_NO, wx.ID_OK]:
            dlg.Destroy()
            frame.Destroy()
            raise UserCancelled
        else:
            dlg.Destroy()


    def yes_no(self, question):
        app = wx.App()
        frame = wx.Frame(None)
        frame.Center()
        dlg = wx.GenericMessageDialog(frame, question, caption = "Handprint!",
                                      style = wx.YES_NO | wx.ICON_QUESTION)
        clicked = dlg.ShowModal()
        dlg.Destroy()
        frame.Destroy()
        return clicked == wx.ID_YES


# Direct-access message utilities.
# ......................................................................

def msg(text, flags = None, colorize = True):
    '''Like the standard print(), but flushes the output immediately and
    colorizes the output by default. Flushing immediately is useful when
    piping the output of a script, because Python by default will buffer the
    output in that situation and this makes it very difficult to see what is
    happening in real time.
    '''
    if colorize and 'termcolor' in sys.modules:
        print(color(text, flags), flush = True)
    else:
        print(text, flush = True)


def color(text, flags = None, colorize = True):
    '''Color-code the 'text' according to 'flags' if 'colorize' is True.
    'flags' can be a single string or a list of strings, as follows.
    Explicit colors (when not using a severity color code):
       'white', 'blue', 'grey', 'cyan', 'magenta'
    Additional color codes reserved for message severities:
       'info'  = informational (green)
       'warn'  = warning (yellow)
       'error' = severe error (red)
    Optional color modifiers:
       'underline', 'bold', 'reverse', 'dark'
    '''
    (prefix, color_name, attributes) = _color_codes(flags)
    if colorize:
        if attributes and color_name:
            return colored(text, color_name, attrs = attributes)
        elif color_name:
            return colored(text, color_name)
        elif attributes:
            return colored(text, attrs = attributes)
        else:
            return text
    elif prefix:
        return prefix + ': ' + str(text)
    else:
        return text


# Internal utilities.
# ......................................................................

def _print_header(text, flags, quiet = False, colorize = True):
    if not quiet:
        msg('')
        msg('{:-^78}'.format(' ' + text + ' '), flags, colorize)
        msg('')


def _color_codes(flags):
    color_name  = ''
    prefix = ''
    if type(flags) is not list:
        flags = [flags]
    if sys.platform.startswith('win'):
        attrib = [] if 'dark' in flags else ['bold']
    else:
        attrib = []
    if 'error' in flags:
        prefix = 'ERROR'
        color_name = 'red'
    if 'warning' in flags or 'warn' in flags:
        prefix = 'WARNING'
        color_name = 'yellow'
    if 'info' in flags:
        color_name = 'green'
    if 'white' in flags:
        color_name = 'white'
    if 'blue' in flags:
        color_name = 'blue'
    if 'grey' in flags:
        color_name = 'grey'
    if 'cyan' in flags:
        color_name = 'cyan'
    if 'magenta' in flags:
        color_name = 'magenta'
    if 'underline' in flags:
        attrib.append('underline')
    if 'bold' in flags:
        attrib.append('bold')
    if 'reverse' in flags:
        attrib.append('reverse')
    if 'dark' in flags:
        attrib.append('dark')
    return (prefix, color_name, attrib)


# Please leave the following for Emacs users.
# ......................................................................
# Local Variables:
# mode: python
# python-indent-offset: 4
# End:
