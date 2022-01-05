'''
amazon.py: interface to Amazon network services Rekognition and Textract

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018-2022 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from   commonpy.file_utils import readable, relative
from   commonpy.interrupt import raise_for_interrupts
import imagesize
import os
import sys

if __debug__:
    from sidetrack import log

import handprint
from handprint.credentials.amazon_auth import AmazonCredentials
from handprint.exceptions import *
from handprint.services.base import TextRecognition, TRResult, Box


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
        # https://docs.aws.amazon.com/textract/latest/dg/textract-dg.pdf#limits
        return 10*1024*1024


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

    def amazon_result(self, file_path, variant, method, image_keyword,
                      result_key, value_key, block_key, result):
        '''Returns the result from calling the service on the 'file_path'.
        The result is returned as an TRResult named tuple.
        '''

        # Delay loading the API packages until needed because they take time to
        # load.  Doing this speeds up overall application start time.
        import boto3
        import botocore

        if not result:
            # If any exceptions occur, let them be passed to caller.
            (image, error) = self._image_from_file(file_path)
            if error:
                return TRResult(path = file_path, data = {}, boxes = [],
                                text = '', error = error)
            try:
                if __debug__: log(f'setting up Amazon client function "{variant}"')
                creds = self._credentials
                session = boto3.session.Session()
                client = session.client(variant, region_name = creds['region_name'],
                                        aws_access_key_id = creds['aws_access_key_id'],
                                        aws_secret_access_key = creds['aws_secret_access_key'])
                if __debug__: log('calling Amazon API function')
                result = getattr(client, method)( **{ image_keyword : {'Bytes': image} })
                if __debug__: log(f'received {len(result[result_key])} blocks')
            except botocore.exceptions.EndpointConnectionError as ex:
                raise AuthFailure(f'Problem with credentials file -- {str(ex)}')
            except KeyboardInterrupt as ex:
                raise
            except KeyError as ex:
                msg = f'Amazon credentials file is missing {",".join(ex.args)}'
                raise AuthFailure(msg)
            except Exception as ex:
                if getattr(ex, 'response', False) and 'Error' in ex.response:
                    error = ex.response['Error']
                    code = error['Code']
                    text = error['Message']
                    path = relative(file_path)
                    if code in ['UnsupportedDocumentException', 'BadDocumentException']:
                        msg = f'Amazon {variant} reports bad or corrupted image in {path}'
                        raise CorruptedContent(msg)
                    elif code in ['InvalidSignatureException', 'UnrecognizedClientException']:
                        raise AuthFailure(f'Problem with credentials file -- {text}')
                # Fallback if we can't get details.
                if __debug__: log(f'Amazon returned exception {str(ex)}')
                msg = f'Amazon {variant} failure for {path} -- {error["Message"]}'
                raise ServiceFailure(msg)

        raise_for_interrupts()
        full_text = ''
        boxes = []
        width, height = imagesize.get(file_path)
        if __debug__: log(f'parsing Amazon result for {relative(file_path)}')
        for block in result[result_key]:
            if value_key not in block:
                continue
            kind = block[value_key].lower()
            if kind in ['word', 'line']:
                text = block[block_key]
                corners = corner_list(block['Geometry']['Polygon'], width, height)
                if corners:
                    boxes.append(Box(kind = kind, bb = corners, text = text,
                                     score = block['Confidence'] / 100))
                else:
                    # Something's wrong with the vertex list. Skip & continue.
                    if __debug__: log(f'bad bb for {text}: {bb}')
            if kind == "line":
                if 'Text' in block:
                    full_text += block['Text'] + '\n'
                elif 'DetectedText' in block:
                    full_text += block['DetectedText'] + '\n'
        return TRResult(path = file_path, data = result, boxes = boxes,
                        text = full_text, error = None)


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


    def result(self, file_path, saved_result):
        '''Returns the result from calling the service on the 'file_path'.
        The result is returned as an TRResult named tuple.
        '''
        return self.amazon_result(file_path, 'textract',
                                  'detect_document_text',
                                  'Document',
                                  'Blocks',     # result_key
                                  'BlockType',  # value_key
                                  'Text',       # block_key
                                  saved_result)


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


    def result(self, file_path, saved_result = None):
        '''Returns the result from calling the service on the 'file_path'.
        The result is returned as an TRResult named tuple.
        '''
        return self.amazon_result(file_path, 'rekognition',
                                  'detect_text',
                                  'Image',
                                  'TextDetections', # result_key
                                  'Type',           # value_key
                                  'DetectedText',   # block_key
                                  saved_result)

# Miscellaneous utilities.
# .............................................................................

def corner_list(polygon, width, height):
    '''Takes a boundingBox value from Amazon's JSON output and returns
    a condensed version, in the form [x y x y x y x y], with the first x, y
    pair representing the upper left corner.'''
    corners = []
    for poly_corner in polygon:
        if 'X' in poly_corner and 'Y' in poly_corner:
            # Results  are in percentages of the image.  Convert to pixels.
            corners.append(int(round(poly_corner['X'] * width)))
            corners.append(int(round(poly_corner['Y'] * height)))
        else:
            return []
    return corners
