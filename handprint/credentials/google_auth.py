'''
google_auth.py: subclass of handprint.credentials.base
'''

import json
import os
from   os import path

import handprint

from .base import Credentials

class GoogleCredentials(Credentials):
    def __init__(self):
        self.creds_file = path.join(self.credentials_dir(), 'google_credentials.json')
        # Haven't been able to make it work; only the environment variable
        # approach has been working for me.
        #
        # with open(self.credentials_file, 'r') as file:
        #     self.credentials = json.load(file)
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.creds_file
