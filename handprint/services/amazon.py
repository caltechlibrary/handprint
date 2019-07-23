'''
amazon.py: interface to Amazon Textextract network service
'''

import boto3
import imagesize
import os
from   os import path
import sys
from   time import sleep

import handprint
from handprint.credentials.microsoft_auth import MicrosoftCredentials
from handprint.services.base import TextRecognition, TRResult, TextBox
from handprint.messages import msg
from handprint.exceptions import *
from handprint.debug import log
from handprint.network import net


# Main class.
# -----------------------------------------------------------------------------

class AmazonTR(TextRecognition):
    def __init__(self):
        '''Initializes the credentials to use for accessing this service.'''
        self._results = {}


    def init_credentials(self, credentials_dir = None):
        pass


    def name(self):
        '''Returns the canonical internal name for this service.'''
        return "amazon"


    def accepted_formats(self):
        '''Returns a list of supported image file formats.'''
        return ['jpeg', 'jpg', 'png', 'pdf']


    def max_rate(self):
        '''Returns the number of calls allowed per second.'''
        # https://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html#limits_textract
        return 0.25


    def max_size(self):
        '''Returns the maximum size of an acceptable image, in bytes.'''
        # https://docs.aws.amazon.com/textract/latest/dg/limits.html
        return 5*1024*1024


    def max_dimensions(self):
        '''Maximum image size as a tuple of pixel numbers: (width, height).'''
        # https://docs.aws.amazon.com/textract/latest/dg/limits.html
        return (2880, 2880)


    def result(self, path):
        '''Returns the results from calling the service on the 'path'.  The
        results are returned as an TRResult named tuple.
        '''
        # Check if we already processed it.
        if path in self._results:
            return self._results[path]

        if __debug__: log('Reading {}', path)
        image = open(path, 'rb').read()
        if len(image) > self.max_size():
            text = 'File exceeds {} byte limit for Amazon service'.format(self.max_size())
            return TRResult(path = path, data = {}, text = '', error = text)

        width, height = imagesize.get(path)
        if __debug__: log('Image size is width = {}, height = {}', width, height)
        max_width, max_height = self.max_dimensions()
        if width > max_width or height > max_height:
            text = 'Image dimensions exceed limits for Amazon service'
            return TRResult(path = path, data = {}, text = '', error = text, boxes = [])

        try:
            if __debug__: log('Sending file to Amazon service')
            client = boto3.client('textract', region_name = 'us-west-2')
            response = client.detect_document_text(Document = {'Bytes': image})
            if __debug__: log('Received {} blocks', len(response['Blocks']))

            full_text = ''
            boxes = []
            for block in response['Blocks']:
                if block['BlockType'] == "WORD":
                    text = block['Text']
                    full_text += (text + ' ')

                    corners = corner_list(block['Geometry']['Polygon'], width, height)
                    if corners:
                        boxes.append(TextBox(boundingBox = corners, text = text))
                    else:
                        # Something is wrong with the vertex list.
                        # Skip it and continue.
                        if __debug__: log('Bad bb for {}: {}', text, bb)

            self._results[path] = TRResult(path = path, data = response,
                                           boxes = boxes, text = full_text,
                                           error = None)
            return self._results[path]
        except Exception as ex:
            import pdb; pdb.set_trace()



def corner_list(polygon, width, height):
    '''Takes a boundingBox value from Google vision's JSON output and returns
    a condensed version, in the form [x y x y x y x y], with the first x, y
    pair representing the upper left corner.'''
    corners = []
    for index in [0, 1, 2, 3]:
        if 'X' in polygon[index] and 'Y' in polygon[index]:
            corners.append(int(round(polygon[index]['X'] * width)))
            corners.append(int(round(polygon[index]['Y'] * height)))
        else:
            return []
    return corners
