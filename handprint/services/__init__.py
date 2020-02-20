'''
Handprint module for interfacing to text recognition cloud services.

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018-2020 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from .amazon import AmazonRekognitionTR, AmazonTextractTR
from .google import GoogleTR
from .microsoft import MicrosoftTR

ACCEPTED_FORMATS = ('.jpg', '.jpeg', '.jp2', '.pdf', '.png', '.gif', '.bmp',
                    '.tif', '.tiff')

KNOWN_SERVICES = {
    'amazon-rekognition': AmazonRekognitionTR,
    'amazon-textract': AmazonTextractTR,
    'google': GoogleTR,
    'microsoft': MicrosoftTR,
}

# Save this list to avoid recreating it all the time.
SERVICES_LIST = sorted(KNOWN_SERVICES.keys())

def services_list():
    return SERVICES_LIST
