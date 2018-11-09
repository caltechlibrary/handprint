'''
tr/base.py: base class definition for text recognition systems.
'''

from collections import namedtuple


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


    def accepted_formats(self):
        '''Returns a list of supported image file formats.'''
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


    def boxes(self, result):
        '''Returns a list of TextBox tuples representing bounding boxes of
        recognized text in the TRResult named tuple provided in parameter
        'result'.
        '''
        import pdb; pdb.set_trace()
