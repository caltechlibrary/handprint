'''
tr/base.py: base class definition for text recognition systems.
'''

from collections import namedtuple


# Named tuple definitions.
# .............................................................................

TRResult = namedtuple('TRResult', 'path data text error')
TRResult.__doc__ = '''Results of invoking a text recognition service.
  'path' is the file path or URL of the item in question
  'data' is the full data result as a Python dict (or {} in case of error)
  'text' is the extracted text as a string (or '' in case of error)
  'error' is None if no error occurred, or the text of any error messages
'''


# Class definitions.
# .............................................................................

class TextRecognition(object):
    def __init__(self):
        pass


    def init_credentials(self):
        '''Initializes the credentials to use for accessing this service.'''
        pass


    def name(self):
        '''Returns the canonical internal name for this service.'''
        pass


    def result(self, path):
        '''Returns the output from the service as an TRResult named tuple.'''
        pass
