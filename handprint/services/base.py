'''
base.py: base class definition for text recognition systems.

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018-2022 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from   collections import namedtuple
from   commonpy.file_utils import readable, relative
import imagesize

if __debug__:
    from sidetrack import log


# Named tuple definitions.
# .............................................................................

TRResult = namedtuple('TRResult', 'path data text boxes error')
TRResult.__doc__ = '''Results of invoking a text recognition service.
  'path' is the file path or URL of the item in question
  'data' is the full data result as a Python dict (or {} in case of error)
  'text' is the extracted text as a string (or '' in case of error)
  'boxes' is a list of text boxes
  'error' is None if no error occurred, or the text of any error messages
'''

Box = namedtuple('Box', 'kind bb text score')
Box.__doc__ = '''Representation of a single box, possibly containing text.
  'kind' is the type; this can be "word", "line", "paragraph".
  'bb' is the bounding box, as XY coordinates of corners starting with u.l.
  'text' is text (when the box contains text).
  'score' is the confidence score given to this item by the service.
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
        if isinstance(other, type(self)):
            return self.__dict__ == other.__dict__
        return NotImplemented


    def __ne__(self, other):
        # Based on lengthy Stack Overflow answer by user "Maggyero" posted on
        # 2018-06-02 at https://stackoverflow.com/a/50661674/743730
        eq = self.__eq__(other)
        if eq is not NotImplemented:
            return not eq
        return NotImplemented


    def __lt__(self, other):
        return self.name() < other.name()


    def __gt__(self, other):
        if isinstance(other, type(self)):
            return other.name() < self.name()
        return NotImplemented


    def __le__(self, other):
        if isinstance(other, type(self)):
            return not other.name() < self.name()
        return NotImplemented


    def __ge__(self, other):
        if isinstance(other, type(self)):
            return not self.name() < other.name()
        return NotImplemented


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


    def result(self, path, saved_result = None):
        '''Returns the text recognition results from the service as an
        TRResult named tuple.  If a saved result is supplied, use that.
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

        rel_path = relative(file_path)
        if not readable(file_path):
            return error_result(f'Unable to read file: {rel_path}')
        if __debug__: log(f'reading {rel_path} for {self.name()}')
        with open(file_path, 'rb') as image_file:
            image = image_file.read()
        if len(image) == 0:
            return error_result(f'Empty file: {rel_path}')
        if len(image) > self.max_size():
            text = f'Exceeds {self.max_size()} byte limit for service: {rel_path}'
            return error_result(text)
        width, height = imagesize.get(file_path)
        if __debug__: log(f'image size is width = {width}, height = {height}')
        if self.max_dimensions():
            max_width, max_height = self.max_dimensions()
            if width > max_width or height > max_height:
                text = f'Dimensions {width}x{height} exceed {self.name()} limits: {rel_path}'
                return error_result(text)
        return (image, None)
