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

        vision_base_url = "https://westus.api.cognitive.microsoft.com/vision/v2.0/"
        text_recognition_url = vision_base_url + "recognizeText"

        headers = {'Ocp-Apim-Subscription-Key': self.credentials,
                   'Content-Type': 'application/octet-stream'}
        params  = {'mode': 'Handwritten'}
        image_data = open(path, 'rb').read()

        if len(image_data) > self.max_size():
            text = 'Error: file "{}" is too large for Microsoft service'.format(path)
            return TRResult(path = path, data = {}, text = '', error = text)

        # Post it to the Microsoft cloud service.
        if __debug__: log('Sending file to MS cloud service')
        response = requests.post(text_recognition_url, headers = headers,
                                 params = params, data = image_data)
        try:
            response.raise_for_status()
        except HTTPError as err:
            # FIXME this might be a good place to suggest to the user that they
            # visit https://blogs.msdn.microsoft.com/kwill/2017/05/17/http-401-access-denied-when-calling-azure-cognitive-services-apis/
            if response.status_code in [401, 402, 403, 407, 451, 511]:
                text = 'Authentication failure for MS service -- {}'.format(err)
                raise ServiceFailure(text)
            elif response.status_code == 429:
                text = 'Server blocking further requests due to rate limits'
                raise RateLimitExceeded(text)
            elif response.status_code == 503:
                text = 'Server is unavailable -- try again later'
                raise ServiceFailure(text)
            else:
                text = 'Encountered network communications problem -- {}'.format(err) 
                raise ServiceFailure(text)
        except Exception as err:
            text = 'MS rejected "{}"'.format(path)
            return TRResult(path = path, data = {}, text = '', error = text)

        # The Microsoft API for extracting handwritten text requires two API
        # calls: one call to submit the image for processing, the other to
        # retrieve the text found in the image.  We have to poll and wait
        # until a result is available.
        analysis = {}
        poll = True
        if __debug__: log('Polling MS for results ...')
        while (poll):
            response_final = requests.get(
                response.headers["Operation-Location"], headers=headers)
            analysis = response_final.json()
            time.sleep(1)
            if ("recognitionResult" in analysis):
                poll = False
            if ("status" in analysis and analysis['status'] == 'Failed'):
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
