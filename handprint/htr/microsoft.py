'''
microsoft.py: interface to Microsoft HTR network service

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
from handprint.htr.base import HTR
from handprint.messages import msg
from handprint.exceptions import ServiceFailure
from handprint.debug import log


# Main class.
# -----------------------------------------------------------------------------

class MicrosoftHTR(HTR):
    def init_credentials(self, credentials_dir = None):
        self.credentials = MicrosoftCredentials(credentials_dir).creds()


    def text_from(self, path):
        vision_base_url = "https://westus.api.cognitive.microsoft.com/vision/v2.0/"
        text_recognition_url = vision_base_url + "recognizeText"

        headers = {'Ocp-Apim-Subscription-Key': self.credentials,
                   'Content-Type': 'application/octet-stream'}
        params  = {'mode': 'Handwritten'}
        image_data = open(path, 'rb').read()

        # https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/home
        # states "The file size of the image must be less than 4 megabytes (MB)"
        if len(image_data) > 4*1024*1024:
            text = 'File "{}" is too large for Microsoft service'.format(path)
            msg(text, 'warn')
            return text

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
            elif code == 429:
                text = 'Server blocking further requests due to rate limits'
                raise ServiceFailure(text)
            elif code == 503:
                text = 'Server is unavailable -- try again later'
                raise ServiceFailure(text)
            else:
                text = 'Encountered network communications problem -- {}'.format(err) 
                raise ServiceFailure(text)
        except Exception as err:
            import pdb; pdb.set_trace()
            msg('MS rejected "{}"'.format(path), 'warn')
            return ''

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
        lines = sorted(analysis['recognitionResult']['lines'],
                       key = lambda x: (x['boundingBox'][1], x['boundingBox'][0]))

        return ' '.join(x['text'] for x in lines)
