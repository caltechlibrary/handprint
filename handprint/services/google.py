'''
google.py: interface to Google text recognition network service
'''

import io
import math
import os
from os import path
import google
from google.cloud import vision_v1p3beta1 as gv
from google.api_core.exceptions import PermissionDenied
from google.cloud.vision import enums
from google.cloud.vision import types
from google.protobuf.json_format import MessageToDict
import json

import handprint
from handprint.credentials.google_auth import GoogleCredentials
from handprint.services.base import TextRecognition, TRResult, TextBox
from handprint.exceptions import *
from handprint.debug import log


# Main class.
# -----------------------------------------------------------------------------
# The self._results property is a dictionary used to cache the results for
# a given file.  This is to avoid using API calls to get the different
# subelements of the results.

class GoogleTR(TextRecognition):
    # The following is based on the table of Google Cloud Vision features at
    # https://cloud.google.com/vision/docs/reference/rpc/google.cloud.vision.v1p3beta1#type_1
    # as of 2018-10-25.
    _known_features = ['face_detection', 'landmark_detection',
                       'label_detection', 'text_detection',
                       'document_text_detection', 'image_properties']


    def __init__(self):
        '''Initializes the credentials to use for accessing this service.'''
        # Dictionary where the keys are the paths and values are an TRResult.
        self._results = {}


    def init_credentials(self, credentials_dir = None):
        '''Initializes the credentials to use for accessing this service.'''
        # Haven't been able to get this to work by reading the credentials:
        # self.credentials = GoogleCredentials(credentials_dir).creds()
        if __debug__: log('Getting credentials from {}', credentials_dir)
        try:
            GoogleCredentials(credentials_dir)
        except Exception as ex:
            raise AuthenticationFailure(str(ex))


    def name(self):
        '''Returns the canonical internal name for this service.'''
        return "google"


    def accepted_formats(self):
        '''Returns a list of supported image file formats.'''
        return ['jpeg', 'jpg', 'png', 'gif', 'bmp', 'raw', 'tif', 'tiff', 'pdf']


    def max_rate(self):
        '''Returns the number of calls allowed per second.'''
        # https://cloud.google.com/vision/quotas
        return 30


    def max_size(self):
        '''Returns the maximum size of an acceptable image, in bytes.'''
        # https://cloud.google.com/vision/docs/supported-files
        # Google Cloud Vision API docs state that images can't exceed 20 MB
        # but the JSON request size limit is 10 MB.  We hit the 10 MB limit
        # even though we're using the Google API library, which I guess must
        # be transferring JSON under the hood.
        return 10*1024*1024


    def max_dimensions(self):
        '''Maximum image size as a tuple of pixel numbers: (width, height).'''
        # No max dimensions are given in the Google docs, so this returns
        # dimensions based on a square image of the max size.  This is not a
        # great approach because (a) an image that doesn't have a square
        # aspect ratio could legitimately have larger dimensions and (b) this
        # assumes 8-bit color, but for now let's take this easy way out.
        side = math.floor(math.sqrt(self.max_size()))
        return (side, side)


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
            text = 'File exceeds {} byte limit for Google service'.format(self.max_size())
            return TRResult(path = path, data = {}, text = '', error = text, boxes = [])

        try:
            if __debug__: log('Building Google vision API object')
            client  = gv.ImageAnnotatorClient()
            image   = gv.types.Image(content = image)
            context = gv.types.ImageContext(language_hints = ['en-t-i0-handwrit'])

            # Iterate over the known API calls and store each result.
            result = dict.fromkeys(self._known_features)
            for feature in self._known_features:
                if __debug__: log('Sending image to Google for {} ...', feature)
                response = getattr(client, feature)(image = image, image_context = context)
                if __debug__: log('Received result.')
                result[feature] = MessageToDict(response)
            full_text = ''

            # Extract text and bounding boxes into our format.
            # Their structure looks like this:
            #
            # result['document_text_detection']['fullTextAnnotation']['pages'][0]['blocks'][0].keys()
            #   --> dict_keys(['boundingBox', 'confidence', 'paragraphs', 'blockType'])
            #
            # result['document_text_detection']['fullTextAnnotation']['pages'][0]['blocks'][0]['paragraphs'][0].keys()
            #   --> dict_keys(['boundingBox', 'words', 'confidence'])
            #
            # https://cloud.google.com/vision/docs/reference/rest/v1/images/annotate#Block

            full_text = ''
            boxes = []
            if 'fullTextAnnotation' in result['document_text_detection']:
                fta = result['document_text_detection']['fullTextAnnotation']
                full_text = fta['text']
                for block in fta['pages'][0]['blocks']:
                    for para in block['paragraphs']:
                        for word in para['words']:
                            text = ''
                            for symbol in word['symbols']:
                                text += symbol['text']
                            bb = word['boundingBox']['vertices']
                            corners = corner_list(bb)
                            if corners:
                                boxes.append(TextBox(boundingBox = corners,
                                                     text = text))
                            else:
                                # Something is wrong with the vertex list.
                                # Skip it and continue.
                                if __debug__: log('Bad bb for {}: {}', text, bb)

            self._results[path] = TRResult(path = path, data = result,
                                           boxes = boxes, text = full_text,
                                           error = None)
            return self._results[path]
        except google.api_core.exceptions.PermissionDenied as ex:
            text = 'Authentication failure for Google service -- {}'.format(ex)
            raise AuthenticationFailure(text)
        except KeyboardInterrupt as ex:
            raise
        except Exception as ex:
            if isinstance(ex, KeyError):
                # Can happen if you control-C in the middle of the Google call.
                # Result is "Exception ignored in: 'grpc._cython.cygrpc._next'"
                # printed to the terminal and we end up here.
                raise KeyboardInterrupt
            else:
                text = 'Error: failed to convert "{}": {}'.format(path, ex)
                return TRResult(path = path, data = {}, boxes = [],
                                text = '', error = text)


# Miscellaenous utilities
# .............................................................................

# Grrrr.  The Google API can return incomplete vertices for a bounding box.
# In one of our sample images ("pbm-2421-PBM_3_1_1_0016"), I get this result:
# [{'x': 2493}, {'x': 2538, 'y': 1}, {'x': 2535, 'y': 154}, {'x': 2490, 'y': 153}]
# So, we have to test to make sure both 'x' and 'y' keys are in every vertex.

def corner_list(bb_json):
    '''Takes a boundingBox value from Google vision's JSON output and returns
    a condensed version, in the form [x y x y x y x y], with the first x, y
    pair representing the upper left corner.'''
    corners = []
    for index in [0, 1, 2, 3]:
        if 'x' in bb_json[index] and 'y' in bb_json[index]:
            corners.append(bb_json[index]['x'])
            corners.append(bb_json[index]['y'])
        else:
            return []
    return corners
