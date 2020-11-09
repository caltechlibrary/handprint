'''
main_body.py: main loop for Handprint

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
import shutil
import sys

if __debug__:
    from sidetrack import set_debug, log, logr

import handprint
from handprint import _OUTPUT_EXT, _OUTPUT_FORMAT
from handprint.credentials import Credentials
from handprint.exceptions import *
from handprint.files import filename_extension, filename_basename
from handprint.files import files_in_directory, filter_by_extensions
from handprint.files import readable, writable, is_url
from handprint.manager import Manager
from handprint.network import network_available, disable_ssl_cert_check
from handprint.services import ACCEPTED_FORMATS, services_list
from handprint.ui import inform, alert, alert_fatal, warn


# Exported classes.
# .............................................................................

class MainBody(object):
    '''Main body for Handprint.'''

    def __init__(self, **kwargs):
        '''Initialize internal state.'''

        # Assign parameters to self to make them available within this object.
        for key, value in kwargs.items():
            setattr(self, key, value)

        # Expose an attribute "exception" that callers can use to find out if
        # the thread finished normally or with an exception.
        self.exception = None


    def run(self):
        '''Run the main body.'''

        if __debug__: log('running MainBody')
        try:
            self._do_preflight()
            self._do_main_work()
        except Exception as ex:
            self.exception = ex
        if __debug__: log('finished MainBody')


    def stop(self):
        pass


    def _do_preflight(self):
        '''Check the option values given by the user, and do other prep.'''

        if not network_available():
            alert_fatal('No network connection.')
            raise CannotProceed(ExitCode.no_network)

        if self.from_file:
            if not path.exists(self.from_file):
                alert_fatal('File not found: {}'.format(self.from_file))
                raise CannotProceed(ExitCode.bad_arg)
            if not readable(self.from_file):
                alert_fatal('File not readable: {}'.format(self.from_file))
                raise CannotProceed(ExitCode.file_error)

        if self.output_dir:
            if path.isdir(self.output_dir):
                if not writable(self.output_dir):
                    alert_fatal('Directory not writable: {}'.format(self.output_dir))
                    raise CannotProceed(ExitCode.file_error)
            else:
                os.mkdir(self.output_dir)
                if __debug__: log('created output_dir directory {}', self.output_dir)


    def _do_main_work(self):
        # Gather up some things and get prepared.
        targets = self.targets_from_arguments()
        if not targets:
            alert_fatal('No images to process; quitting.')
            raise CannotProceed(ExitCode.bad_arg)
        num_targets = len(targets)

        inform('Will apply {} service{} ({}) to {} image{}.',
               len(self.services), 's' if len(self.services) > 1 else '',
               ', '.join(self.services), num_targets, 's' if num_targets > 1 else '')
        if self.extended:
            inform('Will save extended results.')
        inform('Will use up to {} process threads.', self.threads)
        inform(f'Will use credentials stored in {Credentials.credentials_dir()}/.')

        # Get to work.
        if __debug__: log('initializing manager and starting processes')
        manager = Manager(self.services, self.threads, self.output_dir,
                          self.make_grid, self.compare, self.extended)
        print_separators = num_targets > 1
        rule = '─'*(shutil.get_terminal_size().columns or 80)
        for index, item in enumerate(targets, start = 1):
            if print_separators:
                inform(rule)
            manager.run_services(item, index, self.base_name)
        if print_separators:
            inform(rule)


    def targets_from_arguments(self):
        targets = []
        if self.from_file:
            if __debug__: log('reading {}', self.from_file)
            targets = filter(None, open(self.from_file).read().splitlines())
        else:
            for item in self.files:
                if is_url(item):
                    targets.append(item)
                elif path.isfile(item) and filename_extension(item) in ACCEPTED_FORMATS:
                    targets.append(item)
                elif path.isdir(item):
                    # It's a directory, so look for files within.
                    targets += files_in_directory(item, extensions = ACCEPTED_FORMATS)
                else:
                    warn('"{}" not a file or directory', item)

        # Filter files created in past runs.
        targets = filter(lambda name: '.handprint' not in name, targets)

        # If there is both a file in the format we generate and another
        # format of that file, ignore the other formats and just use ours.
        # Note: the value of targets is an iterator, but b/c it's tested inside
        # the loop, a separate list is needed (else get unexpected results).
        targets = list(targets)
        keep = []
        for item in targets:
            ext  = filename_extension(item)
            base = filename_basename(item)
            if ext != _OUTPUT_EXT and (base + _OUTPUT_EXT in targets):
                # png version of file is also present => skip this other version
                continue
            keep.append(item)
        return keep
