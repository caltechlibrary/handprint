'''
microsoft.py: interface to Microsoft text recognition network service

This code was originally based on the sample provided by Microsoft at
https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/quickstarts/python-hand-text

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018-2022 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from   commonpy.interrupt import raise_for_interrupts, wait
from   commonpy.file_utils import relative
import json
import os
import sys

if __debug__:
    from sidetrack import log

import handprint
from handprint.credentials.microsoft_auth import MicrosoftCredentials
from handprint.exceptions import *
from handprint.services.base import TextRecognition, TRResult, Box


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
        # prediction is 6 MB in the free tier, but the real limit is 4 MB,
        # which you will discover if you try to use something larger than 4 MB.
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

    def result(self, path, result = None):
        '''Returns the result from calling the service on the 'file_path'.
        The result is returned as an TRResult named tuple.
        '''
        if not result:
            result = self._result_from_api(path)
            if isinstance(result, tuple):
                return result

        lines = []
        full_text = ''
        if 'analyzeResult' in result:
            analysis = result['analyzeResult']
            if 'readResults' in analysis:
                # We only return the 1st page.  FIXME: should check if > 1.
                lines = analysis['readResults'][0]['lines']
                sorted_lines = sorted(lines, key = lambda x: (x['boundingBox'][1],
                                                              x['boundingBox'][0]))
                full_text = '\n'.join(x['text'] for x in sorted_lines)

        # Create our particular box structure for annotations.  The Microsoft
        # structure is like this: data['recognitionResult']['lines'] contains
        # a list of dict with keys 'words', 'boundingBox', and 'text'.

        boxes = []
        for line in lines:
            # Microsoft doesn't put confidence scores on the lines.
            boxes.append(Box(kind = 'line', bb = line['boundingBox'], text = '',
                             score = 1.0))
            for word in line['words']:
                boxes.append(Box(kind = 'word', bb = word['boundingBox'],
                                 text = word['text'], score = word['confidence']))

        # Put it all together.
        return TRResult(path = path, data = result, text = full_text,
                        boxes = boxes, error = None)


    def _result_from_api(self, path):
        # Read the image and proceed with contacting the service.
        (image, error) = self._image_from_file(path)
        if error:
            return error

        endpoint = self._credentials['endpoint']
        key = self._credentials['subscription_key']
        url = f'{endpoint}/vision/v3.2/read/analyze'
        headers = {'Ocp-Apim-Subscription-Key': key,
                   'Content-Type': 'application/octet-stream'}

        # The Microsoft API requires 2 phases: first submit the image for
        # processing, then wait & poll until the text is ready to be retrieved.

        if __debug__: log(f'contacting Microsoft for {relative(path)}')
        response = self._api('post', url, headers, image)
        if isinstance(response, tuple):
            return response             # If get back a tuple, it's an error.

        if 'Operation-Location' in response.headers:
            poll_url = response.headers['Operation-Location']
        else:
            if __debug__: log('no operation-location in response headers')
            raise ServiceFailure('Unexpected response from Microsoft server')
        if __debug__: log('polling MS for results ...')
        analysis = {}
        poll = True
        while poll:
            raise_for_interrupts()
            # Have never seen results returned in 1 s, and meanwhile, polling
            # still counts against our rate limit.  Wait 2 s to reduce calls.
            wait(2)
            response = self._api('get', poll_url, headers = headers, polling = True)
            if isinstance(response, tuple):
                return response         # If get back a tuple, it's an error.

            # Sometimes the response has no content.  I don't know why.
            # It's not clear what else can be done except to keep trying.
            if not response.text:
                if __debug__: log('received empty result from Microsoft.')
                continue

            analysis = response.json()
            if 'status' in analysis:
                if analysis['status'] in ('notStarted', 'running'):
                    if __debug__: log('Microsoft still processing image')
                    poll = True
                elif analysis['status'] == 'succeeded':
                    if __debug__: log('Microsoft returned success code')
                    poll = False
                else:
                    if analysis['status'] == 'failed':
                        text = 'Microsoft analysis failed'
                    else:
                        text = 'Error: Microsoft returned unexpected result'
                    return TRResult(path = path, data = {}, text = '',
                                    boxes = [], error = text)
            else:
                # No status key in JSON results means something's wrong.
                text = 'Error: Microsoft results not in expected format'
                return TRResult(path = path, data = {}, text = '',
                                boxes = [], error = text)

        if __debug__: log(f'results received from Microsoft for {relative(path)}')
        return analysis


    def _api(self, get_or_post, url, headers, data = None, polling = False):
        from handprint.network import net
        response, error = net(get_or_post, url, headers = headers,
                              data = data, polling = polling)
        if isinstance(error, NetworkFailure):
            if __debug__: log(f'network exception: {str(error)}')
            return TRResult(path = path, data = {}, text = '', error = str(error))
        elif isinstance(error, RateLimitExceeded):
            # https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-manager-request-limits
            # The headers have a Retry-After number in seconds in some cases
            # but not others, so we default to something just in case.
            sleep_time = 20
            if 'Retry-After' in response.headers:
                sleep_time = int(response.headers['Retry-After'])
            if __debug__: log(f'sleeping for {sleep_time} s and retrying')
            wait(sleep_time)
            return self._api(get_or_post, url, headers, data, polling) # Recurse
        elif error:
            if isinstance(error, ServiceFailure):
                # If it was an error generated by the Microsoft service, there
                # will be additional details in the response.  Check for it.
                try:
                    json_response = response.json()
                    if json_response and json_response.get('error', None):
                        error = json_response['error']
                        if 'code' in error:
                            code = error['code']
                            message = error['message']
                            raise ServiceFailure('Microsoft returned error code '
                                                 + code + ' -- ' + message)
                except:
                    pass
            raise error
        else:
            return response
