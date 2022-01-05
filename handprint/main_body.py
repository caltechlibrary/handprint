'''
main_body.py: main loop for Handprint

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018-2022 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from   bun import inform, alert, alert_fatal, warn
from   commonpy.interrupt import raise_for_interrupts
from   commonpy.data_utils import pluralized
from   commonpy.file_utils import filename_extension, filename_basename
from   commonpy.file_utils import files_in_directory, readable, writable
from   commonpy.string_utils import antiformat
import os
from   os.path import isfile, isdir, exists
import sys

if __debug__:
    from sidetrack import log

import handprint
from handprint import _OUTPUT_EXT, _OUTPUT_FORMAT
from handprint.credentials import Credentials
from handprint.exceptions import *
from handprint.exit_codes import ExitCode
from handprint.services import ACCEPTED_FORMATS, services_list


# Exported classes.
# .............................................................................

class MainBody(object):
    '''Main body for Handprint.'''

    def __init__(self, **kwargs):
        '''Initialize internal state.'''

        # Assign parameters to self to make them available within this object.
        for key, value in kwargs.items():
            if __debug__: log(f'parameter value self.{key} = {value}')
            setattr(self, key, value)

        # We expose an attribute "exception" that callers can use to find out
        # if the thread finished normally or with an exception.
        self.exception = None

        # The manager object manages the process of manipulating images and
        # sending them to the services.
        from handprint.manager import Manager
        self._manager = Manager(self.services, self.threads, self.output_dir,
                                self.make_grid, self.compare, self.extended,
                                self.text_size, self.text_color, self.text_shift,
                                self.display, self.confidence, self.reuse_json)


    def run(self):
        '''Run the main body.'''

        if __debug__: log('running MainBody')
        try:
            self._do_preflight()
            self._do_main_work()
        except Exception as ex:
            if __debug__: log(f'exception in main body: {antiformat(str(ex))}')
            self.exception = sys.exc_info()
        if __debug__: log('finished MainBody')


    def stop(self):
        if __debug__: log('stopping ...')
        self._manager.stop_services()


    def _do_preflight(self):
        '''Check the option values given by the user, and do other prep.'''

        from handprint.network import network_available
        if not network_available():
            alert_fatal('No network connection.')
            raise CannotProceed(ExitCode.no_network)

        if self.from_file:
            if not exists(self.from_file):
                alert_fatal(f'File not found: {self.from_file}')
                raise CannotProceed(ExitCode.bad_arg)
            if not readable(self.from_file):
                alert_fatal(f'File not readable: {self.from_file}')
                raise CannotProceed(ExitCode.file_error)

        if self.output_dir:
            if isdir(self.output_dir):
                if not writable(self.output_dir):
                    alert_fatal(f'Directory not writable: {self.output_dir}')
                    raise CannotProceed(ExitCode.file_error)
            else:
                os.mkdir(self.output_dir)
                if __debug__: log(f'created output_dir directory {self.output_dir}')


    def _do_main_work(self):
        # Gather up some things and get prepared.
        targets = self.targets_from_arguments()
        if not targets:
            alert_fatal('No images to process; quitting.')
            raise CannotProceed(ExitCode.bad_arg)
        num_targets = len(targets)

        inform(f'Given {pluralized("image", num_targets, True)} to work on.')
        inform('Will apply results of {}: {}'.format(
            pluralized('service', len(self.services), True),
            ', '.join(self.services), num_targets))
        inform(f'Will use credentials stored in {Credentials.credentials_dir()}/.')
        if self.extended:
            inform('Will save extended results.')
        num_threads = min(self.threads, len(self.services))
        inform(f'Will use up to {num_threads} process threads.')

        # Get to work.
        if __debug__: log('initializing manager and starting processes')
        import shutil
        print_separators = num_targets > 1
        rule = '─'*(shutil.get_terminal_size().columns or 80)
        for index, item in enumerate(targets, start = 1):
            # Check whether we've been interrupted before doing another item.
            raise_for_interrupts()
            # Process next item.
            if print_separators:
                inform(rule)
            self._manager.run_services(item, index, self.base_name)
        if print_separators:
            inform(rule)


    def targets_from_arguments(self):
        # Validator_collection takes a long time to load.  Delay loading it
        # until needed, so that overall application startup time is faster.
        from validator_collection.checkers import is_url

        targets = []
        if self.from_file:
            if __debug__: log(f'reading {self.from_file}')
            targets = filter(None, open(self.from_file).read().splitlines())
        else:
            for item in self.files:
                if is_url(item):
                    targets.append(item)
                elif isfile(item) and filename_extension(item) in ACCEPTED_FORMATS:
                    targets.append(item)
                elif isdir(item):
                    # It's a directory, so look for files within.
                    targets += files_in_directory(item, extensions = ACCEPTED_FORMATS)
                else:
                    warn(f'"{item}" not a file or directory')

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
