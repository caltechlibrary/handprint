'''
amazon_auth.py: subclass of handprint.credentials.base
'''

import json
import os
from   os import path

import handprint
from handprint.exceptions import *
from handprint.files import readable

from .base import Credentials

class AmazonCredentials(Credentials):
    def __init__(self):
        cfile = path.join(self.credentials_dir(), 'amazon_credentials.json')
        if not path.exists(cfile):
            raise AuthFailure('Credentials for Amazon have not been installed')
        elif not readable(cfile):
            raise AuthFailure('Amazon credentials file unreadable: {}'.format(cfile))

        self.creds_file = cfile
        try:
            with open(cfile, 'r') as file:
                self.credentials = json.load(file)
        except Exception as ex:
            raise AuthFailure(
                'Unable to parse Amazon exceptions file: {}'.format(str(ex)))
