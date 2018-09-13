'''
microsoft.py: interface to Microsoft HTR network service

This code was originally based on the sample provided by Microsoft at
https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/quickstarts/python-hand-text
'''

import os
from   os import path
import requests
import sys
import time

import handprint
from handprint.credentials.microsoft_auth import MicrosoftCredentials

from .base import HTR

# Main class.
# -----------------------------------------------------------------------------

class MicrosoftHTR(HTR):
    def init_credentials(self, credentials_dir = None):
        self.credentials = MicrosoftCredentials(credentials_dir).creds()


    def text_from(self, path):
        vision_base_url = "https://westcentralus.api.cognitive.microsoft.com/vision/v2.0/"
        text_recognition_url = vision_base_url + "recognizeText"

        headers = {'Ocp-Apim-Subscription-Key': self.credentials,
                   'Content-Type': 'application/octet-stream'}
        params  = {'mode': 'Handwritten'}
        image_data = open(path, 'rb').read()

        # MS seems to reject files larger than 1 MB.  The result is an HTTP
        # status code 400, "Bad Request for url".  So check it before trying.
        if len(image_data) > 1024*1024:
            msg('File "{}" too large for MS service'.format(path), 'warn')
            return ''

        # Post it to the Microsoft cloud service.
        response = requests.post(text_recognition_url, headers = headers,
                                 params = params, data = image_data)
        try:
            response.raise_for_status()
        except:
            msg('MS rejected "{}"'.format(path), 'warn')
            return ''

        # The Microsoft API for extracting handwritten text requires two API
        # calls: one call to submit the image for processing, the other to
        # retrieve the text found in the image.  We have to poll and wait
        # until a result is available.
        analysis = {}
        poll = True
        while (poll):
            response_final = requests.get(
                response.headers["Operation-Location"], headers=headers)
            analysis = response_final.json()
            time.sleep(1)
            if ("recognitionResult" in analysis):
                poll = False
            if ("status" in analysis and analysis['status'] == 'Failed'):
                poll = False

        lines = sorted(analysis['recognitionResult']['lines'],
                       key = lambda x: (x['boundingBox'][1], x['boundingBox'][0]))

        return ' '.join(x['text'] for x in lines)
