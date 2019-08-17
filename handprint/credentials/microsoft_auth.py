'''
microsoft_auth.py: subclass of handprint.credentials.base
'''

import json
import os
from   os import path

import handprint
from handprint.exceptions import *
from handprint.files import readable

from .base import Credentials

class MicrosoftCredentials(Credentials):
    def __init__(self):
        cfile = path.join(self.credentials_dir(), 'microsoft_credentials.json')
        if not path.exists(cfile):
            raise AuthFailure('Credentials for Microsoft have not been installed')
        elif not readable(cfile):
            raise AuthFailure('Microsoft credentials file unreadable: {}'.format(cfile))

        self.creds_file = cfile
        try:
            with open(self.creds_file, 'r') as file:
                creds = json.load(file)
                self.credentials = creds['subscription_key']
        except Exception as ex:
            raise AuthFailure(
                'Unable to parse Microsoft exceptions file: {}'.format(str(ex)))
