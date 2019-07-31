'''
microsoft_auth.py: subclass of handprint.credentials.base
'''

import json
import os
from   os import path

import handprint

from .base import Credentials

class MicrosoftCredentials(Credentials):
    def __init__(self):
        self.creds_file = path.join(self.credentials_dir(), 'microsoft_credentials.json')
        with open(self.creds_file, 'r') as file:
            creds = json.load(file)
            self.credentials = creds['subscription_key']
