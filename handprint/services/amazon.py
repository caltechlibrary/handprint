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
from handprint.credentials.amazon_auth import AmazonCredentials
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
        '''Initializes the credentials to use for accessing this service.'''
        if __debug__: log('Getting credentials from {}', credentials_dir)
        try:
            self._credentials = AmazonCredentials(credentials_dir).creds()
        except Exception as ex:
            raise AuthenticationFailure(str(ex))


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


    def amazon_result(self, file_path, variant, method_name, keyword_arg,
                      response_key, value_key, block_key):
        '''Returns the results from calling the service on the 'file_path'.
        The results are returned as an TRResult named tuple.
        '''
        # Check if we already processed it.
        if file_path in self._results:
            return self._results[file_path]

        if __debug__: log('Reading {}', file_path)
        image = open(file_path, 'rb').read()
        if len(image) > self.max_size():
            text = 'File exceeds {} byte limit for Amazon service'.format(self.max_size())
            return TRResult(path = file_path, data = {}, text = '', error = text, boxes = [])

        width, height = imagesize.get(file_path)
        if __debug__: log('Image size is width = {}, height = {}', width, height)
        max_width, max_height = self.max_dimensions()
        if width > max_width or height > max_height:
            text = 'Image dimensions exceed limits for Amazon service'
            return TRResult(path = file_path, data = {}, text = '', error = text, boxes = [])

        try:
            if __debug__: log('Sending file to Amazon service')
            creds = self._credentials
            client = boto3.client(variant, region_name = creds['region_name'],
                                  aws_access_key_id = creds['aws_access_key_id'],
                                  aws_secret_access_key = creds['aws_secret_access_key'])
            if hasattr(client, method_name):
                amazon_api = getattr(client, method_name)
            response = amazon_api( **{ keyword_arg : {'Bytes': image} })
            if __debug__: log('Received {} blocks', len(response[response_key]))

            full_text = ''
            boxes = []
            for block in response[response_key]:
                if value_key in block and block[value_key] == "WORD":
                    text = block[block_key]
                    full_text += (text + ' ')

                    corners = corner_list(block['Geometry']['Polygon'], width, height)
                    if corners:
                        boxes.append(TextBox(boundingBox = corners, text = text))
                    else:
                        # Something is wrong with the vertex list.
                        # Skip it and continue.
                        if __debug__: log('Bad bb for {}: {}', text, bb)

            self._results[file_path] = TRResult(path = file_path, data = response,
                                           boxes = boxes, text = full_text,
                                           error = None)
            return self._results[file_path]
        except Exception as ex:
            import pdb; pdb.set_trace()



class AmazonTextractTR(AmazonTR):
    '''Subclass of AmazonTR for the Textract service.'''

    def name(self):
        '''Returns the canonical internal name for this service.'''
        return "amazon-textract"


    def accepted_formats(self):
        '''Returns a list of supported image file formats.'''
        return ['jpeg', 'jpg', 'png', 'pdf']


    def result(self, file_path):
        '''Returns the results from calling the service on the 'file_path'.
        The results are returned as an TRResult named tuple.
        '''
        return self.amazon_result(file_path, 'textract',
                                  'detect_document_text',
                                  'Document',
                                  'Blocks',     # response_key
                                  'BlockType',  # value_key
                                  'Text')       # block_key


class AmazonRekognitionTR(AmazonTR):
    '''Subclass of AmazonTR for the Rekognition service.'''

    def name(self):
        '''Returns the canonical internal name for this service.'''
        return "amazon-rekognition"


    def accepted_formats(self):
        '''Returns a list of supported image file formats.'''
        return ['jpeg', 'jpg', 'png']


    def result(self, file_path):
        '''Returns the results from calling the service on the 'file_path'.
        The results are returned as an TRResult named tuple.
        '''
        return self.amazon_result(file_path, 'rekognition',
                                  'detect_text',
                                  'Image',
                                  'TextDetections', # response_key
                                  'Type',           # value_key
                                  'DetectedText')   # block_key


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
