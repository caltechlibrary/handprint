'''
credentials_files.py: mapping of services to credentials files

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018-2020 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

CREDENTIALS_FILES = {
    'amazon'             : 'amazon_credentials.json',
    'amazon-rekognition' : 'amazon_credentials.json',
    'amazon-textract'    : 'amazon_credentials.json',
    'google'             : 'google_credentials.json',
    'microsoft'          : 'microsoft_credentials.json',
}

def credentials_filename(service):
    assert service in CREDENTIALS_FILES
    return CREDENTIALS_FILES[service]
