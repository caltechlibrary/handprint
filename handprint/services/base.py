'''
base.py: base class definition for text recognition systems.

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018-2020 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from collections import namedtuple
import imagesize

if __debug__:
    from sidetrack import set_debug, log, logr

import handprint
from handprint.files import readable


# Named tuple definitions.
# .............................................................................

TRResult = namedtuple('TRResult', 'path data text boxes error')
TRResult.__doc__ = '''Results of invoking a text recognition service.
  'path' is the file path or URL of the item in question
  'data' is the full data result as a Python dict (or {} in case of error)
  'text' is the extracted text as a string (or '' in case of error)
  'error' is None if no error occurred, or the text of any error messages
'''

TextBox = namedtuple('TextBox', 'text boundingBox')
TextBox.__doc__ = '''Representation of a single bounding box and text therein.
  'box' is the bounding box, as XY coordinates of corners starting with u.l.
  'text' is the text
'''


# Class definitions.
# .............................................................................
# Basics for the __eq__ etc. methods came from
# https://stackoverflow.com/questions/1061283/lt-instead-of-cmp

class TextRecognition(object):
    def __init__(self):
        pass


    def __str__(self):
        return self.name()


    def __repr__(self):
        return self.name()


    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        else:
            return not self.name() < other.name() and not other.name() < self.name()


    def __ne__(self, other):
        return not __eq__(self, other)


    def __lt__(self, other):
        return self.name() < other.name()


    def __gt__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        else:
            return other.name() < self.name()


    def __le__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        else:
            return not other.name() < self.name()


    def __ge__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        else:
            return not self.name() < other.name()


    def init_credentials(self):
        '''Initializes the credentials to use for accessing this service.'''
        pass


    def name(self):
        '''Returns the canonical internal name for this service.'''
        pass


    def name_color(self):
        '''Returns a color code for this service.  See the color definitions
        in messages.py.'''
        pass


    def max_rate(self):
        '''Returns the number of calls allowed per second.'''
        pass


    def max_size(self):
        '''Returns the maximum size of an acceptable image, in bytes.'''
        pass


    def max_dimensions(self):
        '''Maximum image size as a tuple of pixel numbers: (width, height).'''
        pass


    def result(self, path):
        '''Returns the text recognition results from the service as an
        TRResult named tuple.
        '''
        pass


    def _image_from_file(self, file_path):
        '''Helper function for subclasses to read image files.
        Returns a tuple, (image, error), where "error" is a TRResult with a
        non-empty error field value if an error occurred, and "image" is the
        bytes of the image if it was successfully read.
        '''

        def error_result(error_text):
            return (None, TRResult(path = file_path, data = {}, text = '',
                                   error = error_text, boxes = []))

        if not readable(file_path):
            return error_result('Unable to read file: {}'.format(file_path))
        if __debug__: log('reading image file {} for {}', file_path, self.name())
        with open(file_path, 'rb') as image_file:
            image = image_file.read()
        if len(image) == 0:
            return error_result('Empty file: {}'.format(file_path))
        if len(image) > self.max_size():
            text = 'Exceeds {} byte limit for service: {}'.format(self.max_size(), file_path)
            return error_result(text)
        width, height = imagesize.get(file_path)
        if __debug__: log('image size is width = {}, height = {}', width, height)
        if self.max_dimensions():
            max_width, max_height = self.max_dimensions()
            if width > max_width or height > max_height:
                text = 'Image dimensions {}x{} exceed {} limits: {}'.format(
                    width, height, self.name(), file_path)
                return error_result(text)
        return (image, None)
