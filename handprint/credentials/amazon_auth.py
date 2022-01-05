'''
amazon_auth.py: subclass of handprint.credentials.base

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018-2022 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from   commonpy.file_utils import readable
import json
import os
from   os import path
from   sidetrack import log

import handprint
from handprint.exceptions import *

from .base import Credentials
from .credentials_files import credentials_filename


# Main class.
# .............................................................................

class AmazonCredentials(Credentials):
    def __init__(self):
        cfile = path.join(self.credentials_dir(), credentials_filename('amazon'))
        if __debug__: log(f'credentials file for amazon is {cfile}')
        if not path.exists(cfile):
            raise AuthFailure('Credentials for Amazon have not been installed')
        elif not readable(cfile):
            raise AuthFailure(f'Amazon credentials file unreadable: {cfile}')

        try:
            with open(cfile, 'r') as file:
                self.credentials = json.load(file)
        except Exception as ex:
            raise AuthFailure(f'Unable to parse Amazon exceptions file: {str(ex)}')
