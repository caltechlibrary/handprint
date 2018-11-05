'''
microsoft.py: interface to Microsoft text recognition network service

This code was originally based on the sample provided by Microsoft at
https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/quickstarts/python-hand-text
'''

import os
from   os import path
import requests
from requests.exceptions import HTTPError
import sys
import time
from   timeit import default_timer as timer

import handprint
from handprint.credentials.microsoft_auth import MicrosoftCredentials
from handprint.methods.base import TextRecognition, TRResult
from handprint.messages import msg
from handprint.exceptions import ServiceFailure, RateLimitExceeded
from handprint.debug import log


# Main class.
# -----------------------------------------------------------------------------

class MicrosoftTR(TextRecognition):
    def __init__(self):
        '''Initializes the credentials to use for accessing this service.'''
        self._results = {}


    def init_credentials(self, credentials_dir = None):
        '''Initializes the credentials to use for accessing this service.'''
        if __debug__: log('Getting credentials from {}', credentials_dir)
        self.credentials = MicrosoftCredentials(credentials_dir).creds()


    def name(self):
        '''Returns the canonical internal name for this service.'''
        return "microsoft"


    def accepted_formats(self):
        '''Returns a list of supported image file formats.'''
        return ['jpeg', 'jpg', 'png', 'gif', 'bmp']


    def max_rate(self):
        '''Returns the number of calls allowed per second.'''
        # https://azure.microsoft.com/en-us/pricing/details/cognitive-services/computer-vision/
        return 0.333


    def max_size(self):
        '''Returns the maximum size of an acceptable image, in bytes.'''
        # https://cloud.google.com/vision/docs/supported-files
        # Google Cloud Vision API docs state that images can't exceed 20 MB
        # but the JSON request size limit is 10 MB.  We hit the 10 MB limit
        # even though we're using the Google API library, which I guess must
        # be transferring JSON under the hood.
        return 4*1024*1024


    def max_dimensions(self):
        '''Maximum image size as a tuple of pixel numbers: (width, height).'''
        # For OCR, max image dimensions are 4200 x 4200.
        # https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/home
        return (4200, 4200)


    def result(self, path):
        '''Returns all the results from the service as a Python dict.'''
        # Check if we already processed it.
        if path in self._results:
            return self._results[path]

        image = open(path, 'rb').read()
        if len(image) > self.max_size():
            text = 'Error: file "{}" is too large for Microsoft service'.format(path)
            return TRResult(path = path, data = {}, text = '', error = text)

        base_url = "https://westus.api.cognitive.microsoft.com/vision/v2.0/"
        url = base_url + "recognizeText"
        params  = {'mode': 'Handwritten'}
        headers = {'Ocp-Apim-Subscription-Key': self.credentials,
                   'Content-Type': 'application/octet-stream'}
        start_time = timer()

        # The Microsoft API for extracting text requires two phases: one call
        # to submit the image for processing, then polling to wait until the
        # text is ready to be retrieved.

        if __debug__: log('Sending file to MS cloud service')
        response = requests.post(url, headers = headers, params = params, data = image)
        (rate_limit, error) = self._status_check(response)
        if rate_limit:
            # Pause for a full minute to let the server reset its timers.
            if __debug__: log('Hit rate limit; sleeping for 60 s')
            time.sleep(60)
        elif error:
            if __debug__: log('MS call produced an error: {}', error)
            return TRResult(path = path, data = {}, text = '', error = error)

        analysis = {}
        poll = True
        while poll:
            if __debug__: log('Polling MS for results ...')
            # I never have seen results returned in 1 sec, and meanwhile the
            # repeated polling counts against your rate limit.  So, wait for
            # 2 sec to reduce the number of calls.
            time.sleep(2)
            response_final = requests.get(
                response.headers["Operation-Location"], headers=headers)
            (rate_limit, error) = self._status_check(response)
            if rate_limit:
                # Pause for a full minute to let the server reset its timers.
                if __debug__: log('Hit rate limit; sleeping for 60 s')
                time.sleep(60)
            elif error:
                if __debug__: log('MS call produced an error: {}', error)
                return TRResult(path = path, data = {}, text = '', error = error)

            analysis = response_final.json()
            if "recognitionResult" in analysis:
                poll = False
            if "status" in analysis and analysis['status'] == 'Failed':
                poll = False
        if __debug__: log('Results received.')

        # Have to extract the text into a single string.
        full_text = ''
        if 'recognitionResult' in analysis:
            lines = analysis['recognitionResult']['lines']
            sorted_lines = sorted(lines, key = lambda x: (x['boundingBox'][1], x['boundingBox'][0]))
            full_text = ' '.join(x['text'] for x in sorted_lines)

        # Put it all together.
        self._results[path] = TRResult(path = path, data = analysis,
                                       text = full_text, error = None)
        return self._results[path]


    def _status_check(self, response):
        hit_rate_limit = False
        error = None
        if response.status_code in [401, 402, 403, 407, 451, 511]:
            # FIXME this might be a good place to suggest to the user that they
            # visit https://blogs.msdn.microsoft.com/kwill/2017/05/17/http-401-access-denied-when-calling-azure-cognitive-services-apis/
            error = 'Authentication failure for MS service -- {}'.format(err)
        elif response.status_code == 429:
            hit_rate_limit = True
        elif response.status_code == 503:
            error = 'Service is unavailable -- try again later'
        elif response.status_code in [500, 501, 502, 503, 506, 507, 508]:
            error = "Internal server error {}".format(response.status_code)
        elif response.status_code > 400:
            error = 'Problem contacting Microsoft service: {}'.format(err)
        elif response.status_code > 500:
            error = 'Problem reported by Microsoft Azure: {}'.format(err)
        return (hit_rate_limit, error)
