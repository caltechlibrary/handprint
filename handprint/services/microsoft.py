'''
microsoft.py: interface to Microsoft text recognition network service

This code was originally based on the sample provided by Microsoft at
https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/quickstarts/python-hand-text

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018-2020 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import os
from   os import path
import sys

if __debug__:
    from sidetrack import set_debug, log, logr

import handprint
from handprint.credentials.microsoft_auth import MicrosoftCredentials
from handprint.exceptions import *
from handprint.interruptions import interrupted, raise_for_interrupts, wait
from handprint.network import net
from handprint.services.base import TextRecognition, TRResult, TextBox


# Main class.
# .............................................................................

class MicrosoftTR(TextRecognition):

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
        return 'aquamarine1'


    def max_rate(self):
        '''Returns the number of calls allowed per second.'''
        # https://azure.microsoft.com/en-us/pricing/details/cognitive-services/computer-vision/
        return 0.333


    def max_size(self):
        '''Returns the maximum size of an acceptable image, in bytes.'''
        # Microsoft Azure documentation states the file size limit for
        # prediction is 4 MB in the free tier.
        # https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/concept-recognizing-text
        return 4*1024*1024


    def max_dimensions(self):
        '''Maximum image size as a tuple of pixel numbers: (width, height).'''
        # For OCR, max image dimensions are 4200 x 4200.
        # https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/home
        return (10000, 10000)


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
        # Read the image and proceed with contacting the service.
        (image, error) = self._image_from_file(path)
        if error:
            return error

        key = self._credentials['subscription_key']
        endpoint = self._credentials['endpoint']
        url = f'{endpoint}/vision/v3.0/read/analyze'
        headers = {'Ocp-Apim-Subscription-Key': key,
                   'Content-Type': 'application/octet-stream'}

        # The Microsoft API for extracting text requires two phases: one call
        # to submit the image for processing, then polling to wait until the
        # text is ready to be retrieved.

        if __debug__: log('sending file to MS cloud service')
        response, error = net('post', url, headers = headers, data = image)
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
            wait(sleep_time)
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
            raise_for_interrupts()
            # I never have seen results returned in 1 second, and meanwhile
            # the repeated polling counts against your rate limit.  So, wait
            # for 2 s to reduce the number of calls.
            wait(2)
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
                wait(sleep_time)
            elif error:
                raise error

            # Sometimes the response comes back without content.  I don't know
            # if that's a bug in the Azure system or not.  It's not clear what
            # else should be done except keep going.
            if response.text:
                analysis = response.json()
                if 'status' in analysis:
                    if analysis['status'] in ('notStarted', 'running'):
                        if __debug__: log('Microsoft still processing image')
                        poll = True
                    elif analysis['status'] == 'succeeded':
                        if __debug__: log('Microsoft returned success code')
                        poll = False
                    elif analysis['status'] == 'failed':
                        text = 'Microsoft analysis failed'
                        return TRResult(path = path, data = {}, text = '', error = text)
                    else:
                        text = 'Error: Microsoft returned unexpected result'
                        return TRResult(path = path, data = {}, text = '', error = text)
                else:
                    # No status key in JSON results means something's wrong.
                    text = 'Error: Microsoft results not in expected format'
                    return TRResult(path = path, data = {}, text = '', error = text)
            else:
                if __debug__: log('received empty result from Microsoft.')

        if __debug__: log('results received.')
        # Have to extract the text into a single string.
        full_text = ''
        if 'analyzeResult' in analysis:
            results = analysis['analyzeResult']
            if 'readResults' in results:
                # We only return the 1st page.  FIXME: should check if > 1.
                lines = results['readResults'][0]['lines']
                sorted_lines = sorted(lines, key = lambda x: (x['boundingBox'][1], x['boundingBox'][0]))
                full_text = '\n'.join(x['text'] for x in sorted_lines)

        # Create our particular box structure for annotations.  The Microsoft
        # structure is like this: data['recognitionResult']['lines'] contains
        # a list of dict with keys 'words', 'boundingBox', and 'text'.

        boxes = []
        for chunk in lines:
            for word in chunk['words']:
                boxes.append(TextBox(boundingBox = word['boundingBox'], text = word['text']))

        # Put it all together.
        return TRResult(path = path, data = analysis, text = full_text,
                        boxes = boxes, error = None)
