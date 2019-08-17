'''
google_auth.py: subclass of handprint.credentials.base
'''

import json
import os
from   os import path

import handprint
from handprint.exceptions import *
from handprint.files import readable

from .base import Credentials

class GoogleCredentials(Credentials):
    def __init__(self):
        cfile = path.join(self.credentials_dir(), 'google_credentials.json')
        if not path.exists(cfile):
            raise AuthFailure('Credentials for Google have not been installed')
        elif not readable(cfile):
            raise AuthFailure('Google credentials file unreadable: {}'.format(cfile))

        self.creds_file = cfile
        # Haven't been able to make it work; only the environment variable
        # approach has been working for me.
        #
        # with open(self.credentials_file, 'r') as file:
        #     self.credentials = json.load(file)
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = cfile
