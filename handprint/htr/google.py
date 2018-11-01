'''
google.py: interface to Google HTR network service
'''

import io
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
from handprint.exceptions import ServiceFailure
from handprint.debug import log

from .base import HTR, HTRResult


# Main class.
# -----------------------------------------------------------------------------

# Google Cloud Vision API docs state that images cannot exceed 20 MB according
# to https://cloud.google.com/vision/docs/supported-files but if you try to
# send more than 10 MB, you'll get an error back.

_FILE_SIZE_LIMIT = 10*1024*1024


# Main class.
# -----------------------------------------------------------------------------
# The self._results property is a dictionary used to cache the results for
# a given file.  This is to avoid using API calls to get the different
# subelements of the results.

class GoogleHTR(HTR):
    # The following is based on the table of Google Cloud Vision features at
    # https://cloud.google.com/vision/docs/reference/rpc/google.cloud.vision.v1p3beta1#type_1
    # as of 2018-10-25.
    _known_features = ['face_detection', 'landmark_detection', 'crop_hints',
                       'label_detection', 'text_detection',
                       'document_text_detection', 'image_properties']


    def __init__(self):
        '''Initializes the credentials to use for accessing this service.'''
        # Dictionary where the keys are the paths and values are an HTRResult.
        self._results = {}


    def init_credentials(self, credentials_dir = None):
        '''Initializes the credentials to use for accessing this service.'''
        # Haven't been able to get this to work by reading the credentials:
        # self.credentials = GoogleCredentials(credentials_dir).creds()
        if __debug__: log('Getting credentials from {}', credentials_dir)
        GoogleCredentials(credentials_dir)


    def name(self):
        '''Returns the canonical internal name for this service.'''
        return "google"


    def result(self, path):
        '''Returns the results from calling the service on the 'path'.  The
        results are returned as an HTRResult named tuple.
        '''
        # Check if we already processed it.
        if path in self._results:
            return self._results[path]

        if __debug__: log('Reading {}', path)
        with io.open(path, 'rb') as image_file:
            image_data = image_file.read()

        if len(image_data) > _FILE_SIZE_LIMIT:
            text = 'Error: file "{}" is too large for Google service'.format(path)
            return HTRResult(path = path, data = {}, text = '', error = text)
        try:
            if __debug__: log('Building Google vision API object')
            client  = gv.ImageAnnotatorClient()
            image   = gv.types.Image(content = image_data)
            context = gv.types.ImageContext(language_hints = ['en-t-i0-handwrit'])

            # Iterate over the known API calls and store each result.
            result = dict.fromkeys(self._known_features)
            for feature in self._known_features:
                if __debug__: log('Sending image to Google for {} ...', feature)
                response = getattr(client, feature)(image = image, image_context = context)
                if __debug__: log('Received result.')
                result[feature] = MessageToDict(response)
            full_text = ''
            if 'fullTextAnnotation' in result['document_text_detection']:
                full_text = result['document_text_detection']['fullTextAnnotation']['text']
            self._results[path] = HTRResult(path = path, data = result,
                                            text = full_text, error = None)
            return self._results[path]
        except google.api_core.exceptions.PermissionDenied as err:
            text = 'Authentication failure for Google service -- {}'.format(err)
            raise ServiceFailure(text)
        except KeyboardInterrupt:
            raise
        except Exception as err:
            if isinstance(err, KeyError):
                # Can happen if you control-C in the middle of the Google call.
                # Result is "Exception ignored in: 'grpc._cython.cygrpc._next'"
                # printed to the terminal and we end up here.
                raise KeyboardInterrupt
            else:
                text = 'Error: failed to convert "{}": {}'.format(path, err)
                return HTRResult(path = path, data = {}, text = '', error = text)
