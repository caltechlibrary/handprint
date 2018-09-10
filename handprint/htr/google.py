'''
google.py: interface to Google HTR network service
'''

import io
import os
from os import path
from google.cloud import vision_v1p3beta1 as vision

import handprint
from handprint.files import module_path, handprint_path

from .base import HTR

# Main class.
# -----------------------------------------------------------------------------

class GoogleHTR(HTR):
    def __init__(self):
        credentials_file = path.join(handprint_path(), 'credentials.json')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file


    def text_from(self, path):
        with io.open(path, 'rb') as image_file:
            content = image_file.read()

        image    = vision.types.Image(content = content)
        context  = vision.types.ImageContext(language_hints = ['en-t-i0-handwrit'])
        client   = vision.ImageAnnotatorClient()
        response = client.document_text_detection(image = image,
                                                  image_context = context)

        return response.full_text_annotation.text
