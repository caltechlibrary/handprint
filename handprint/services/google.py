'''
google.py: interface to Google text recognition network service

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018-2022 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from   commonpy.file_utils import relative
from   commonpy.interrupt import raise_for_interrupts
import io
import json
import math
import os
import json

if __debug__:
    from sidetrack import log

import handprint
from handprint.credentials.google_auth import GoogleCredentials
from handprint.exceptions import *
from handprint.services.base import TextRecognition, TRResult, Box


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

    def result(self, path, result = None):
        '''Returns the result from calling the service on the 'file_path'.
        The result is returned as an TRResult named tuple.
        '''

        # Delay loading the API packages until needed because they take time to
        # load.  Doing this speeds up overall application start time.
        import google
        from google.cloud import vision_v1 as gv
        from google.api_core.exceptions import PermissionDenied
        from google.protobuf.json_format import MessageToDict

        if not result:
            # Read the image and proceed with contacting the service.
            (image, error) = self._image_from_file(path)
            if error:
                return error

            if __debug__: log(f'building Google API object for {relative(path)}')
            try:
                client  = gv.ImageAnnotatorClient()
                params  = gv.TextDetectionParams(
                    mapping = { 'enable_text_detection_confidence_score': True })
                context = gv.ImageContext(language_hints = ['en-t-i0-handwrit'],
                                          text_detection_params = params)
                img     = gv.Image(content = image)
                if __debug__: log(f'sending image to Google for {relative(path)} ...')
                response = client.document_text_detection(image = img,
                                                          image_context = context)
                if __debug__: log(f'received result from Google for {relative(path)}')
                result = dict_from_response(response)
            except google.api_core.exceptions.PermissionDenied as ex:
                text = 'Authentication failure for Google service -- {}'.format(ex)
                raise AuthFailure(text)
            except google.auth.exceptions.DefaultCredentialsError as ex:
                text = 'Credentials file error for Google service -- {}'.format(ex)
                raise AuthFailure(text)
            except google.api_core.exceptions.ServiceUnavailable as ex:
                text = 'Network, service, or Google configuration error -- {}'.format(ex)
                raise ServiceFailure(text)
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

        raise_for_interrupts()
        boxes = []
        # See this page for more information about the structure:
        # https://cloud.google.com/vision/docs/handwriting#python
        if len(result['full_text_annotation']['pages']) > 1:
            warn('More than one page received from Google; using only first.')
        for block in result['full_text_annotation']['pages'][0]['blocks']:
            for para in block['paragraphs']:
                corners = corner_list(para['bounding_box']['vertices'])
                boxes.append(Box(bb = corners, kind = 'para', text = '',
                                 score = para['confidence']))
                for word in para['words']:
                    text = ''
                    for symbol in word['symbols']:
                        text += symbol['text']
                    corners = corner_list(word['bounding_box']['vertices'])
                    if corners:
                        boxes.append(Box(bb = corners, kind = 'word',
                                         text = text, score = para['confidence']))
                    else:
                        # Something is wrong with the vertex list.
                        # Skip it and continue.
                        if __debug__: log(f'bad bb for {text}: {bb}')
        full_text = result['full_text_annotation']['text']
        return TRResult(path = path, data = result,
                        boxes = boxes, text = full_text, error = None)


# Miscellaenous utilities
# .............................................................................

# Grrrr.  The Google API can return incomplete vertices for a bounding box.
# In one of our sample images ("pbm-2421-PBM_3_1_1_0016"), I get this result:
# [{'x': 2493}, {'x': 2538, 'y': 1}, {'x': 2535, 'y': 154}, {'x': 2490, 'y': 153}]
# So, we have to test to make sure both 'x' and 'y' keys are in every vertex.

def corner_list(vertices):
    '''Takes a boundingBox value from Google Vision's output and returns
    a condensed version, in the form [x y x y x y x y], with the first x, y
    pair representing the upper left corner.'''
    corners = []
    if len(vertices) < 4:
        return []
    for vertex in vertices:
        corners.append(vertex['x'])
        corners.append(vertex['y'])
    return corners


# In more recent versions of googleapis-common-protos, MessageToDict is no
# longer directly available as it was before.  See this GitHub issue answer:
# https://github.com/googleapis/python-memcache/issues/19#issuecomment-708516816
# The following builds on an answer by user Tobiasz Kędzierski given at
# https://github.com/googleapis/python-memcache/issues/19#issuecomment-709628506

def dict_from_response(response):
    import google
    if isinstance(response, google.cloud.vision_v1.types.image_annotator.AnnotateImageResponse):
        return response.__class__.to_dict(response)
    else:
        return MessageToDict(response)


def json_from_response(response):
    return json.dumps(dict_from_response(response))
