'''
constants: global constants for Handprint.

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import sys

import handprint
from handprint.methods import GoogleTR
from handprint.methods import MicrosoftTR

ON_WINDOWS = sys.platform.startswith('win')

ACCEPTED_FORMATS = ('jpg', 'jpeg', 'jp2', 'png', 'gif', 'bmp', 'tif', 'tiff')

FORMATS_MUST_CONVERT = ('jp2', 'tif', 'tiff')

KNOWN_METHODS = {
    'google': GoogleTR,
    'microsoft': MicrosoftTR,
}
