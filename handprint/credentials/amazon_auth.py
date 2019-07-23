'''
amazon_auth.py: subclass of handprint.credentials.base
'''

import json
import os
from   os import path

import handprint

from .base import Credentials

class AmazonCredentials(Credentials):
    def __init__(self, credentials_dir = None):
        self.credentials_dir = credentials_dir
        self.credentials_file = path.join(credentials_dir, 'amazon_credentials.json')
        with open(self.credentials_file, 'r') as file:
            self.credentials = json.load(file)


    def credentials_file():
        return self.credentials_file
