'''
network.py: miscellaneous network utilities for Holdit.
'''

import http.client
from   http.client import responses as http_responses
import requests

import handprint
from   handprint.files import rename_existing
from   handprint.debug import log


def network_available():
    '''Return True if it appears we have a network connection, False if not.'''
    try:
        r = requests.get("https://www.caltech.edu")
        return True
    except requests.ConnectionError:
        if __debug__: log('Could not connect to https://www.caltech.edu')
        return False


# The following originally started out as the code here:
# https://stackoverflow.com/a/16696317/743730

def download_url(url, local_destination):
    '''Download the 'url' to the file 'local_destination' and return a tuple
    of (success, error) indicating whether the attempt succeeded and an error
    message if it failed.
    '''

    # Attempt to do the download.
    try:
        if __debug__: log('Requesting {}', url)
        req = requests.get(url, stream = True)
    except requests.exceptions.ConnectionError as err:
        if err.args and isinstance(err.args[0], urllib3.exceptions.MaxRetryError):
            return (False, 'Unable to resolve destination host')
        else:
            return (False, str(err))
    except requests.exceptions.InvalidSchema as err:
        return (False, 'Unsupported network protocol')
    except Exceptions as err:
        return (False, str(err))

    # Interpret the response.
    code = req.status_code
    if code == 202:
        # Code 202 = Accepted, "received but not yet acted upon."
        if __debug__: log('Pausing & retrying')
        sleep(1)                        # Sleep a short time and try again.
        return download_url(url, local_destination)
    elif 200 <= code < 400:
        if __debug__: log('Writing downloaded data to {}', local_destination)
        rename_existing(local_destination)
        with open(local_destination, 'wb') as f:
            for chunk in req.iter_content(chunk_size = 1024):
                if chunk:
                    f.write(chunk)
        req.close()
        return (True, '')
    elif code in [401, 402, 403, 407, 451, 511]:
        return (False, "Access is forbidden or requires authentication")
    elif code in [404, 410]:
        return (False, "No content found at this location")
    elif code in [405, 406, 409, 411, 412, 414, 417, 428, 431, 505, 510]:
        return (False, "Server returned code {} -- please report this".format(code))
    elif code in [415, 416]:
        return (False, "Server rejected the request")
    elif code == 429:
        return (False, "Server blocking further requests due to rate limits")
    elif code == 503:
        return (False, "Server is unavailable -- try again later")
    elif code in [500, 501, 502, 506, 507, 508]:
        return (False, "Internal server error")
    else:
        return (False, "Unable to resolve URL")
