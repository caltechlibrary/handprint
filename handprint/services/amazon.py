'''
amazon.py: interface to Amazon network services Rekognition and Textract

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018-2020 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import boto3
import imagesize
import os
from   os import path
import sys

if __debug__:
    from sidetrack import set_debug, log, logr

import handprint
from handprint.credentials.amazon_auth import AmazonCredentials
from handprint.exceptions import *
from handprint.files import readable
from handprint.interruptions import interrupted, raise_for_interrupts, wait
from handprint.network import net
from handprint.services.base import TextRecognition, TRResult, TextBox


# Main class.
# .............................................................................

class AmazonTR(TextRecognition):
    '''Base class for Amazon text recognition services.'''

    def init_credentials(self):
        '''Initializes the credentials to use for accessing this service.'''
        try:
            if __debug__: log('initializing credentials')
            self._credentials = AmazonCredentials().creds()
        except Exception as ex:
            raise AuthFailure(str(ex))


    def max_rate(self):
        '''Returns the number of calls allowed per second.'''
        # https://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html#limits_textract
        return 0.25


    def max_size(self):
        '''Returns the maximum size of an acceptable image, in bytes.'''
        # https://docs.aws.amazon.com/textract/latest/dg/limits.html
        return 5*1024*1024


    def max_dimensions(self):
        '''Maximum image size as a tuple of pixel numbers: (width, height).
        A value of None indicates the limits are unknown.'''
        # I can't find a limit stated in the Amazon docs.
        return None


    # General scheme of things:
    #
    # * Return errors (via TRResult) if a result could not be obtained
    #   because of an error specific to a particular path/item.  The guiding
    #   principle here is: if the calling loop is processing multiple items,
    #   can it be expected to be able to go on to the next item if this error
    #   occurred?
    #
    # * Raises exceptions if a problem occurs that should stop the calling
    #   code from continuing with this service.  This includes things like
    #   authentication failures, because authentication failures tend to
    #   involve all uses of a service and not just a specific item.
    #
    # * Otherwise, returns a TRResult if successful.

    def amazon_result(self, file_path, variant, api_method, image_keyword,
                      response_key, value_key, block_key):
        '''Returns the results from calling the service on the 'file_path'.
        The results are returned as an TRResult named tuple.
        '''
        # Read the image and proceed with contacting the service.
        # If any exceptions occur, let them be passed to caller.
        (image, error) = self._image_from_file(file_path)
        if error:
            return TRResult(path = file_path, data = {}, boxes = [],
                            text = '', error = error)

        if __debug__: log('setting up Amazon client function "{}"', variant)
        creds = self._credentials
        try:
            session = boto3.session.Session()
            client = session.client(variant, region_name = creds['region_name'],
                                  aws_access_key_id = creds['aws_access_key_id'],
                                  aws_secret_access_key = creds['aws_secret_access_key'])
            if __debug__: log('calling Amazon API function')
            response = getattr(client, api_method)( **{ image_keyword : {'Bytes': image} })
            if __debug__: log('received {} blocks', len(response[response_key]))
            raise_for_interrupts()
            full_text = ''
            boxes = []
            width, height = imagesize.get(file_path)
            for block in response[response_key]:
                if value_key in block and block[value_key] == "WORD":
                    text = block[block_key]
                    full_text += (text + ' ')
                    corners = corner_list(block['Geometry']['Polygon'], width, height)
                    if corners:
                        boxes.append(TextBox(boundingBox = corners, text = text))
                    else:
                        # Something's wrong with the vertex list. Skip & continue.
                        if __debug__: log('bad bb for {}: {}', text, bb)

            return TRResult(path = file_path, data = response, boxes = boxes,
                            text = full_text, error = None)
        except KeyboardInterrupt as ex:
            raise
        except Exception as ex:
            text = 'Error: {} -- {}'.format(str(ex), file_path)
            return TRResult(path = file_path, data = {}, boxes = [],
                            text = '', error = text)


class AmazonTextractTR(AmazonTR):
    '''Subclass of AmazonTR for the Textract service.'''

    @classmethod
    def name(self):
        '''Returns the canonical internal name for this service.'''
        return "amazon-textract"


    @classmethod
    def name_color(self):
        '''Returns a color code for this service.  See the color definitions
        in messages.py.'''
        return 'light_goldenrod2'


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

    @classmethod
    def name(self):
        '''Returns the canonical internal name for this service.'''
        return "amazon-rekognition"


    @classmethod
    def name_color(self):
        '''Returns a color code for this service.  See the color definitions
        in messages.py.'''
        return 'dark_orange'


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


# Miscellaneous utilities.
# .............................................................................

def corner_list(polygon, width, height):
    '''Takes a boundingBox value from Google vision's JSON output and returns
    a condensed version, in the form [x y x y x y x y], with the first x, y
    pair representing the upper left corner.'''
    corners = []
    for index in [0, 1, 2, 3]:
        if 'X' in polygon[index] and 'Y' in polygon[index]:
            # Results  are in percentages of the image.  Convert to pixels.
            corners.append(int(round(polygon[index]['X'] * width)))
            corners.append(int(round(polygon[index]['Y'] * height)))
        else:
            return []
    return corners
