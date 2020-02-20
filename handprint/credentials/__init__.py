'''
Handprint module for handling credentials.

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018-2020 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from .base import Credentials
from .amazon_auth import AmazonCredentials
from .google_auth import GoogleCredentials
from .microsoft_auth import MicrosoftCredentials
