'''
google.py: interface to Google text recognition network service

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018-2020 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import io
import math
import os
from os import path
import google
from google.cloud import vision_v1p3beta1 as gv
from google.api_core.exceptions import PermissionDenied
from google.protobuf.json_format import MessageToDict
import json

if __debug__:
    from sidetrack import set_debug, log, logr

import handprint
from handprint.credentials.google_auth import GoogleCredentials
from handprint.exceptions import *
from handprint.interruptions import interrupted, raise_for_interrupts
from handprint.services.base import TextRecognition, TRResult, TextBox


# Main class.
# .............................................................................

class GoogleTR(TextRecognition):
    # The following is based on the table of Google Cloud Vision features at
    # https://cloud.google.com/vision/docs/reference/rpc/google.cloud.vision.v1p3beta1#type_1
    # as of 2018-10-25.
    _known_features = ['document_text_detection']


    def init_credentials(self):
        '''Initializes the credentials to use for accessing this service.'''
        try:
            if __debug__: log('initializing credentials')
            GoogleCredentials()
        except Exception as ex:
            raise AuthFailure(str(ex))


    @classmethod
    def name(self):
        '''Returns the canonical internal name for this service.'''
        return "google"


    @classmethod
    def name_color(self):
        '''Returns a color code for this service.  See the color definitions
        in messages.py.'''
        return 'deep_sky_blue1'


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
        # No max dimensions are given in the Google docs.
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

    def result(self, path):
        '''Returns the results from calling the service on the 'path'.  The
        results are returned as an TRResult named tuple.
        '''
        # Read the image and proceed with contacting the service.
        (image, error) = self._image_from_file(path)
        if error:
            return error

        try:
            if __debug__: log('building Google vision API object')
            client  = gv.ImageAnnotatorClient()
            image   = gv.types.Image(content = image)
            context = gv.types.ImageContext(language_hints = ['en-t-i0-handwrit'])

            # Iterate over the known API calls and store each result.
            result = dict.fromkeys(self._known_features)
            for feature in self._known_features:
                raise_for_interrupts()
                if __debug__: log('sending image to Google for {} ...', feature)
                response = getattr(client, feature)(image = image, image_context = context)
                if __debug__: log('received result.')
                result[feature] = MessageToDict(response)

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

            raise_for_interrupts()
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
                                if __debug__: log('bad bb for {}: {}', text, bb)

            return TRResult(path = path, data = result, boxes = boxes,
                            text = full_text, error = None)
        except google.api_core.exceptions.PermissionDenied as ex:
            text = 'Authentication failure for Google service -- {}'.format(ex)
            raise AuthFailure(text)
        except KeyboardInterrupt as ex:
            raise
        except Exception as ex:
            if isinstance(ex, KeyError):
                # Can happen if you control-C in the middle of the Google call.
                # Result is "Exception ignored in: 'grpc._cython.cygrpc._next'"
                # printed to the terminal and we end up here.
                raise KeyboardInterrupt
            else:
                text = 'Error: {} -- {}'.format(str(ex), path)
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
