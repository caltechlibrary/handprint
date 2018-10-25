'''
htr/base.py: base class definition for HTR systems.
'''

class HTR(object):
    def __init__(self):
        pass


    def init_credentials(self):
        '''Initializes the credentials to use for accessing this service.'''
        pass


    def name(self):
        '''Returns the canonical internal name for this service.'''
        pass


    def document_text(self, path):
        '''Returns the pure text extracted from the image by this service.'''
        pass


    def all_results(self, path):
        '''Returns all the results from the service as a Python dict.'''
        pass
