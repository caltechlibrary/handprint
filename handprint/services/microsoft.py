'''
microsoft.py: interface to Microsoft text recognition network service

This code was originally based on the sample provided by Microsoft at
https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/quickstarts/python-hand-text
'''

import os
from   os import path
import sys
from   time import sleep

import handprint
from handprint.credentials.microsoft_auth import MicrosoftCredentials
from handprint.services.base import TextRecognition, TRResult, TextBox
from handprint.exceptions import *
from handprint.debug import log
from handprint.network import net


# Main class.
# .............................................................................

class MicrosoftTR(TextRecognition):
    def __init__(self):
        '''Initializes the credentials to use for accessing this service.'''
        self._results = {}


    def init_credentials(self):
        '''Initializes the credentials to use for accessing this service.'''
        try:
            if __debug__: log('initializing credentials')
            self._credentials = MicrosoftCredentials().creds()
        except Exception as ex:
            raise AuthFailure(str(ex))


    @classmethod
    def name(self):
        '''Returns the canonical internal name for this service.'''
        return "microsoft"


    @classmethod
    def name_color(self):
        '''Returns a color code for this service.  See the color definitions
        in messages.py.'''
        return 'lightBlue2'


    def max_rate(self):
        '''Returns the number of calls allowed per second.'''
        # https://azure.microsoft.com/en-us/pricing/details/cognitive-services/computer-vision/
        return 0.333


    def max_size(self):
        '''Returns the maximum size of an acceptable image, in bytes.'''
        # https://cloud.google.com/vision/docs/supported-files
        # Google Cloud Vision API docs state that images can't exceed 20 MB
        # but the JSON request size limit is 10 MB.  We hit the 10 MB limit
        # even though we're using the Google API library, which I guess must
        # be transferring JSON under the hood.
        return 4*1024*1024


    def max_dimensions(self):
        '''Maximum image size as a tuple of pixel numbers: (width, height).'''
        # For OCR, max image dimensions are 4200 x 4200.
        # https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/home
        return (4200, 4200)


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
        '''Returns all the results from calling the service on the 'path'. The
        results are returned as an TRResult named tuple.
        '''
        # Check if we already processed it.
        if path in self._results:
            if __debug__: log('returning already-known result for {}', path)
            return self._results[path]

        # Read the image and proceed with contacting the service.
        (image, error) = self._image_from_file(path)
        if error:
            return error

        base_url = 'https://westus.api.cognitive.microsoft.com/vision/v2.0/'
        url = base_url + 'recognizeText'
        params  = {'mode': 'Handwritten'}
        headers = {'Ocp-Apim-Subscription-Key': self._credentials,
                   'Content-Type': 'application/octet-stream'}

        # The Microsoft API for extracting text requires two phases: one call
        # to submit the image for processing, then polling to wait until the
        # text is ready to be retrieved.

        if __debug__: log('sending file to MS cloud service')
        response, error = net('post', url, headers = headers, params = params, data = image)
        if isinstance(error, NetworkFailure):
            if __debug__: log('network exception: {}', str(error))
            return TRResult(path = path, data = {}, text = '', error = str(error))
        elif isinstance(error, RateLimitExceeded):
            # https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-manager-request-limits
            # The headers should have a Retry-After number in seconds.
            sleep_time = 30
            if 'Retry-After' in response.headers:
                sleep_time = int(response.headers['Retry-After'])
            if __debug__: log('sleeping for {} s and retrying', sleep_time)
            sleep(sleep_time)
            return self.result(path)    # Recursive invocation
        elif error:
            raise error

        if 'Operation-Location' in response.headers:
            polling_url = response.headers['Operation-Location']
        else:
            if __debug__: log('no operation-location in response headers')
            raise ServiceFailure('Unexpected response from Microsoft server')

        if __debug__: log('polling MS for results ...')
        analysis = {}
        poll = True
        while poll:
            # I never have seen results returned in 1 second, and meanwhile
            # the repeated polling counts against your rate limit.  So, wait
            # for 2 s to reduce the number of calls.
            sleep(2)
            response, error = net('get', polling_url, polling = True, headers = headers)
            if isinstance(error, NetworkFailure):
                if __debug__: log('network exception: {}', str(error))
                return TRResult(path = path, data = {}, text = '', error = str(error))
            elif isinstance(error, RateLimitExceeded):
                # Pause to let the server reset its timers.  It seems that MS
                # doesn't send back a Retry-After header when rated limited
                # during polling, but I'm going to check it anyway, in case.
                sleep_time = 30
                if 'Retry-After' in response.headers:
                    sleep_time = int(response.headers['Retry-After'])
                if __debug__: log('sleeping for {} s and retrying', sleep_time)
                sleep(sleep_time)
            elif error:
                raise error

            # Sometimes the response comes back without content.  I don't know
            # if that's a bug in the Azure system or not.  It's not clear what
            # else should be done except keep going.
            if response.text:
                analysis = response.json()
                if 'recognitionResult' in analysis:
                    poll = False
                if 'status' in analysis and analysis['status'] == 'Failed':
                    poll = False
            else:
                if __debug__: log('received empty result from Microsoft.')
        if __debug__: log('results received.')

        # Have to extract the text into a single string.
        full_text = ''
        if 'recognitionResult' in analysis:
            lines = analysis['recognitionResult']['lines']
            sorted_lines = sorted(lines, key = lambda x: (x['boundingBox'][1], x['boundingBox'][0]))
            full_text = '\n'.join(x['text'] for x in sorted_lines)

        # Create our particular box structure for annotations.  The Microsoft
        # structure is like this: data['recognitionResult']['lines'] contains
        # a list of dict with keys 'words', 'boundingBox', and 'text'.

        boxes = []
        for chunk in lines:
            boxes.append(TextBox(boundingBox = chunk['boundingBox'], text = chunk['text']))

        # Put it all together.
        self._results[path] = TRResult(path = path, data = analysis,
                                       text = full_text, boxes = boxes,
                                       error = None)
        return self._results[path]
