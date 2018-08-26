
import io
import os
from os import path
from google.cloud import vision_v1p3beta1 as vision

import handprint
from handprint.files import module_path


class GoogleHTR(object):
    def __init__(self):
        credentials_file = path.join(module_path(), 'credentials.json')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file


    def text(self, path):
        with io.open(path, 'rb') as image_file:
            content = image_file.read()

        image    = vision.types.Image(content = content)
        context  = vision.types.ImageContext(language_hints = ['en-t-i0-handwrit'])
        client   = vision.ImageAnnotatorClient()
        response = client.document_text_detection(image = image,
                                                  image_context = context)

        return response.full_text_annotation.text
