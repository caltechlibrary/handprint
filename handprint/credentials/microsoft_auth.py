'''
microsoft_auth.py: subclass of handprint.credentials.base

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018-2020 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import json
import os
from   os import path
from   sidetrack import log

import handprint
from handprint.exceptions import *
from handprint.files import readable

from .base import Credentials
from .credentials_files import credentials_filename


# Constants.
# .............................................................................

_DEFAULT_ENDPOINT = 'https://westus.api.cognitive.microsoft.com'


# Main class.
# .............................................................................

class MicrosoftCredentials(Credentials):
    def __init__(self):
        cfile = path.join(self.credentials_dir(), credentials_filename('microsoft'))
        if __debug__: log('credentials file for microsoft is {}', cfile)
        if not path.exists(cfile):
            raise AuthFailure('Credentials for Microsoft have not been installed')
        elif not readable(cfile):
            raise AuthFailure('Microsoft credentials file unreadable: {}'.format(cfile))

        try:
            with open(cfile, 'r') as file:
                creds = json.load(file)
                if 'endpoint' in creds:
                    endpoint = creds['endpoint'].rstrip('/')
                    if not endpoint.startswith('http'):
                        endpoint = 'https://' + endpoint
                else:
                    if __debug__: log('endpoint not found; using default')
                    endpoint = _DEFAULT_ENDPOINT
                creds['endpoint'] = endpoint
                self.credentials = creds
        except Exception as ex:
            raise AuthFailure(
                'Unable to parse Microsoft exceptions file: {}'.format(str(ex)))
