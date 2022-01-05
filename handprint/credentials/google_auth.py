'''
google_auth.py: subclass of handprint.credentials.base

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

class GoogleCredentials(Credentials):
    def __init__(self):
        cfile = path.join(self.credentials_dir(), credentials_filename('google'))
        if __debug__: log(f'credentials file for google is {cfile}')
        if not path.exists(cfile):
            raise AuthFailure('Credentials for Google have not been installed')
        elif not readable(cfile):
            raise AuthFailure(f'Google credentials file unreadable: {cfile}')

        # Haven't been able to make it work; only the environment variable
        # approach has been working for me.
        #
        # with open(self.credentials_file, 'r') as file:
        #     self.credentials = json.load(file)
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = cfile
