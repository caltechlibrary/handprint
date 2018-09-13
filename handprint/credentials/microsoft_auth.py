'''
microsoft_auth.py: subclass of handprint.credentials.base
'''

import json
import os
from   os import path

import handprint

from .base import Credentials

class MicrosoftCredentials(Credentials):
    def __init__(self, credentials_dir = None):
        self.credentials_dir = credentials_dir
        self.credentials_file = path.join(credentials_dir, 'microsoft_credentials.json')
        with open(self.credentials_file, 'r') as file:
            creds = json.load(file)
            self.credentials = creds['subscription_key']


    def credentials_file(self):
        return self.credentials_file
