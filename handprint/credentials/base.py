'''
base.py: credentials base class
'''

from appdirs import user_config_dir
import os
from   os import path

import handprint
from handprint.debug import log
from handprint.files import make_dir, copy_file


# Main class.
# -----------------------------------------------------------------------------

class Credentials(object):
    creds_dir = user_config_dir('Handprint')

    def __init__(self):
        self.creds_file = None
        self.credentials = None


    def creds(self):
        return self.credentials


    def credentials_file(self):
        return self.creds_file


    @classmethod
    def credentials_dir(self):
        return Credentials.creds_dir


    @classmethod
    def save_credentials(self, service, creds_file):
        if not path.isdir(Credentials.creds_dir):
            if __debug__: log('creating credentials dir: {}.', Credentials.creds_dir)
            make_dir(Credentials.creds_dir)
        if __debug__: log('saving credentials for {}: {}.', service, creds_file)
        copy_file(creds_file, Credentials.creds_dir)
