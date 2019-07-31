'''
amazon_auth.py: subclass of handprint.credentials.base
'''

import json
import os
from   os import path

import handprint

from .base import Credentials

class AmazonCredentials(Credentials):
    def __init__(self):
        self.creds_file = path.join(self.credentials_dir(), 'amazon_credentials.json')
        with open(self.creds_file, 'r') as file:
            self.credentials = json.load(file)
