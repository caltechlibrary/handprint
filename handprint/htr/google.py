'''
google.py: interface to Google HTR network service
'''

import io
import os
from os import path
import google
from google.cloud import vision_v1p3beta1 as vision
from google.api_core.exceptions import PermissionDenied

import handprint
from handprint.credentials.google_auth import GoogleCredentials
from handprint.messages import msg
from handprint.exceptions import ServiceFailure
from handprint.debug import log


from .base import HTR



# Main class.
# -----------------------------------------------------------------------------

class GoogleHTR(HTR):
    def init_credentials(self, credentials_dir = None):
        # Haven't been able to get this to work by reading the credentials
        # self.credentials = GoogleCredentials(credentials_dir).creds()
        GoogleCredentials(credentials_dir)


    def text_from(self, path):
        with io.open(path, 'rb') as image_file:
            image_data = image_file.read()

        # Google Cloud Vision API docs state that images cannot exceed 20 MB:
        # https://cloud.google.com/vision/docs/supported-files
        if len(image_data) > 20*1024*1024:
            text = 'Error: file "{}" is too large for Google service'.format(path)
            msg(text, 'warn')
            return text

        try:
            if __debug__: log('Building Google vision API object')
            image    = vision.types.Image(content = image_data)
            context  = vision.types.ImageContext(language_hints = ['en-t-i0-handwrit'])
            client   = vision.ImageAnnotatorClient()
            if __debug__: log('Sending image to Google ...')
            response = client.document_text_detection(image = image,
                                                      image_context = context)
            if __debug__: log('Received result.')
            return response.full_text_annotation.text
        except google.api_core.exceptions.PermissionDenied as err:
            text = 'Authentication failure for Google service -- {}'.format(err)
            raise ServiceFailure(text)
        except Exception as err:
            text = 'Error: failed to convert "{}": {}'.format(path, err)
            return text
