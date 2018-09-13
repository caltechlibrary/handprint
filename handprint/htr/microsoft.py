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
        response = requests.post(text_recognition_url, data = image_data,
                                 params = params, headers = headers)
        response.raise_for_status()

        # Extracting handwritten text requires two API calls: One call to submit the
        # image for processing, the other to retrieve the text found in the image.

        # Holds the URI used to retrieve the recognized text.
        operation_url = response.headers["Operation-Location"]

        # The recognized text isn't immediately available, so poll to wait for completion.
        analysis = {}
        poll = True
        while (poll):
            response_final = requests.get(
                response.headers["Operation-Location"], headers=headers)
            analysis = response_final.json()
            time.sleep(1)
            if ("recognitionResult" in analysis):
                poll= False
                if ("status" in analysis and analysis['status'] == 'Failed'):
                    poll= False

        lines = sorted(analysis['recognitionResult']['lines'],
                       key = lambda x: (x['boundingBox'][1], x['boundingBox'][0]))

        import pdb; pdb.set_trace()
        return ' '.join(x['text'] for x in lines)
