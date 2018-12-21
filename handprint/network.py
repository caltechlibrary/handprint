'''
network.py: miscellaneous network utilities for Handprint.
'''

import http.client
from   http.client import responses as http_responses
import requests
from   requests.packages.urllib3.exceptions import InsecureRequestWarning
from   time import sleep
import ssl
import urllib
from   urllib import request
import urllib3
import warnings

import handprint
from   handprint.files import rename_existing
from   handprint.debug import log
from   handprint.exceptions import *


# Main functions.
# .............................................................................

def network_available():
    '''Return True if it appears we have a network connection, False if not.'''
    r = None
    try:
        r = urllib.request.urlopen("http://www.google.com")
        return True
    except Exception:
        if __debug__: log('Could not connect to https://www.google.com')
        return False
    if r:
        r.close()


def timed_request(get_or_post, url, **kwargs):
    # Wrap requests.get() with a timeout.
    # 'verify' means whether to perform HTTPS certificate verification.
    http_method = requests.get if get_or_post == 'get' else requests.post
    with warnings.catch_warnings():
        # When verify = True, the underlying urllib3 library used by the
        # Python requests module will issue a warning about unverified HTTPS
        # requests.  If we don't care, then the warnings are a constant
        # annoyance.  See also this for a discussion:
        # https://github.com/kennethreitz/requests/issues/2214
        warnings.simplefilter("ignore", InsecureRequestWarning)
        return http_method(url, timeout = 10, verify = False, **kwargs)


def download_file(url, output_file, user = None, pswd = None, spinner = None):
    if spinner:
        spinner.update('Downloading {}'.format(url))
    try:
        download(url, user, pswd, output_file)
        return True
    except (NoContent, ServiceFailure, AuthenticationFailure) as ex:
        if spinner:
            spinner.fail('Failed to download {}: {}'.format(url, str(ex)))
    return False


def download(url, user, password, local_destination, recursing = 0):
    '''Download the 'url' to the file 'local_destination'.'''
    def addurl(text):
        return (text + ' for {}').format(url)

    try:
        req = timed_request('get', url, stream = True, auth = (user, password))
    except requests.exceptions.ConnectionError as ex:
        if recursing >= _MAX_RECURSIVE_CALLS:
            raise NetworkFailure(addurl('Too many connection errors'))
        arg0 = ex.args[0]
        if isinstance(arg0, urllib3.exceptions.MaxRetryError):
            if network_available():
                raise NetworkFailure(addurl('Unable to resolve host'))
            else:
                raise NetworkFailure(addurl('Lost network connection with server'))
        elif (isinstance(arg0, urllib3.exceptions.ProtocolError)
              and arg0.args and isinstance(args0.args[1], ConnectionResetError)):
            if __debug__: log('download() got ConnectionResetError; will recurse')
            sleep(1)                    # Sleep a short time and try again.
            recursing += 1
            download(url, user, password, local_destination, recursing)
        else:
            raise NetworkFailure(str(ex))
    except requests.exceptions.ReadTimeout as ex:
        if network_available():
            raise ServiceFailure(addurl('Timed out reading data from server'))
        else:
            raise NetworkFailure(addurl('Timed out reading data over network'))
    except requests.exceptions.InvalidSchema as ex:
        raise NetworkFailure(addurl('Unsupported network protocol'))
    except Exception as ex:
        raise

    # Interpret the response.
    code = req.status_code
    if code == 202:
        # Code 202 = Accepted, "received but not yet acted upon."
        sleep(1)                        # Sleep a short time and try again.
        recursing += 1
        if __debug__: log('Calling download() recursively for http code 202')
        download(url, user, password, local_destination, recursing)
    elif 200 <= code < 400:
        # The following originally started out as the code here:
        # https://stackoverflow.com/a/16696317/743730
        with open(local_destination, 'wb') as f:
            for chunk in req.iter_content(chunk_size = 1024):
                if chunk:
                    f.write(chunk)
        req.close()
    elif code in [401, 402, 403, 407, 451, 511]:
        raise AuthenticationFailure(addurl('Access is forbidden'))
    elif code in [404, 410]:
        raise NoContent(addurl('No content found'))
    elif code in [405, 406, 409, 411, 412, 414, 417, 428, 431, 505, 510]:
        raise InternalError(addurl('Server returned code {}'.format(code)))
    elif code in [415, 416]:
        raise ServiceFailure(addurl('Server rejected the request'))
    elif code == 429:
        raise RateLimitExceeded('Server blocking further requests due to rate limits')
    elif code == 503:
        raise ServiceFailure('Server is unavailable -- try again later')
    elif code in [500, 501, 502, 506, 507, 508]:
        raise ServiceFailure(addurl('Internal server error (HTTP code {})'.format(code)))
    else:
        raise NetworkFailure('Unable to resolve {}'.format(url))


def net(get_or_post, url, polling = False, recursing = 0, **kwargs):
    '''Gets or posts the 'url' with optional keyword arguments provided.
    Returns a tuple of (response, exception), where the first element is
    the response from the get or post http call, and the second element is
    an exception object if an exception occurred.  If no exception occurred,
    the second element will be None.  This allows the caller to inspect the
    response even in cases where exceptions are raised.

    If keyword 'polling' is True, certain statuses like 404 are ignored and
    the response is returned; otherwise, they are considered errors.
    '''
    def addurl(text):
        return (text + ' for {}').format(url)

    req = None
    try:
        if __debug__: log('HTTP {} {}', get_or_post, url)
        req = timed_request(get_or_post, url, **kwargs)
    except requests.exceptions.ConnectionError as ex:
        if recursing >= _MAX_RECURSIVE_CALLS:
            return (req, NetworkFailure(addurl('Too many connection errors')))
        arg0 = ex.args[0]
        if isinstance(arg0, urllib3.exceptions.MaxRetryError):
            return (req, NetworkFailure(addurl('Unable to resolve host')))
        elif (isinstance(arg0, urllib3.exceptions.ProtocolError)
              and arg0.args and isinstance(args0.args[1], ConnectionResetError)):
            if __debug__: log('net() got ConnectionResetError; will recurse')
            sleep(1)                    # Sleep a short time and try again.
            recursing += 1
            return net(get_or_post, url, polling, recursing, **kwargs)
        else:
            return (req, NetworkFailure(str(ex)))
    except requests.exceptions.ReadTimeout as ex:
        if network_available():
            return (req, ServiceFailure(addurl('Timed out reading data from server')))
        else:
            return (req, NetworkFailure(addurl('Timed out reading data over network')))
    except requests.exceptions.InvalidSchema as ex:
        return (req, NetworkFailure(addurl('Unsupported network protocol')))
    except Exception as ex:
        return (req, ex)

    # Interpret the response.
    code = req.status_code
    error = None
    if code in [404, 410] and not polling:
        error = NoContent(addurl("No content found"))
    elif code in [401, 402, 403, 407, 451, 511]:
        error = AuthenticationFailure(addurl('Access is forbidden'))
    elif code in [405, 406, 409, 411, 412, 414, 417, 428, 431, 505, 510]:
        error = InternalError(addurl('Server returned code {}'.format(code)))
    elif code in [415, 416]:
        error = ServiceFailure(addurl('Server rejected the request'))
    elif code == 429:
        error = RateLimitExceeded('Server blocking further requests due to rate limits')
    elif code == 503:
        error = ServiceFailure('Server is unavailable -- try again later')
    elif code in [500, 501, 502, 506, 507, 508]:
        error = ServiceFailure('Internal server error (HTTP code {})'.format(code))
    elif not (200 <= code < 400):
        error = NetworkFailure("Unable to resolve {}".format(url))
    return (req, error)


# Next code originally from https://stackoverflow.com/a/39779918/743730
def disable_ssl_cert_check():
    requests.packages.urllib3.disable_warnings()
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context
