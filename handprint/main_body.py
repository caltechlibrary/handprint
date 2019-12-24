'''
main_body.py: main loop for Handprint

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018-2019 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import os
from   os import path
import sys

import handprint
from handprint import _OUTPUT_EXT, _OUTPUT_FORMAT
from handprint.debug import set_debug, log
from handprint.exceptions import *
from handprint.files import filename_extension, filename_basename
from handprint.files import files_in_directory, filter_by_extensions
from handprint.files import readable, writable, is_url
from handprint.manager import Manager
from handprint.network import network_available, disable_ssl_cert_check
from handprint.services import ACCEPTED_FORMATS, services_list
from handprint.styled import styled
from handprint.ui import inform, alert, warn


# Exported classes.
# .............................................................................

class MainBody(object):
    '''Main body for Handprint.'''

    def __init__(self, base_name, extended, from_file, output_dir, threads):
        '''Initialize internal state and prepare for running services.'''

        if not network_available():
            raise ServiceFailure('No network.')

        if from_file:
            if not path.exists(from_file):
                raise RuntimeError('File not found: {}'.format(from_file))
            if not readable(from_file):
                raise RuntimeError('File not readable: {}'.format(from_file))

        if output_dir:
            if path.isdir(output_dir):
                if not writable(output_dir):
                    raise RuntimeError('Directory not writable: {}'.format(output_dir))
            else:
                os.mkdir(output_dir)
                if __debug__: log('Created output_dir directory {}', output_dir)

        self._base_name  = base_name
        self._extended   = extended
        self._from_file  = from_file
        self._output_dir = output_dir
        self._threads    = threads


    def run(self, services, files, make_grid, compare):
        '''Run service(s) on files.'''

        # Set shortcut variables for better code readability below.
        base_name  = self._base_name
        extended   = self._extended
        from_file  = self._from_file
        output_dir = self._output_dir
        threads    = self._threads

        # Gather up some things and get prepared.
        targets = self.targets_from_arguments(files, from_file)
        if not targets:
            raise RuntimeError('No images to process; quitting.')
        num_targets = len(targets)

        inform('Will apply {} service{} ({}) to {} image{}.',
               len(services), 's' if len(services) > 1 else '',
               ', '.join(services), num_targets, 's' if num_targets > 1 else '')
        if self._extended:
            inform('Will save extended results.')
        inform('Will use up to {} process threads.', threads)

        # Get to work.
        if __debug__: log('initializing manager and starting processes')
        manager = Manager(services, threads, output_dir, make_grid, compare, extended)
        print_separators = num_targets > 1
        for index, item in enumerate(targets, start = 1):
            if print_separators:
                inform(styled('━'*70, 'dark'))
            manager.run_services(item, index, base_name)
        if print_separators:
            inform(styled('━'*70, 'dark'))


    def targets_from_arguments(self, files, from_file):
        targets = []
        if from_file:
            if __debug__: log('Opening {}', from_file)
            with open(from_file) as f:
                targets = f.readlines()
            targets = [line.rstrip('\n') for line in targets]
            if __debug__: log('Read {} lines from {}.', len(targets), from_file)
        else:
            for item in files:
                if is_url(item):
                    targets.append(item)
                elif path.isfile(item) and filename_extension(item) in ACCEPTED_FORMATS:
                    targets.append(item)
                elif path.isdir(item):
                    # It's a directory, so look for files within.
                    # Ignore files that appear to be the previous output of Handprint.
                    # (These are files that end in, e.g., ".google.png")
                    handprint_endings = ['.' + x + _OUTPUT_EXT for x in services_list()]
                    files = files_in_directory(item, extensions = ACCEPTED_FORMATS)
                    files = filter_by_extensions(files, handprint_endings)
                    targets += files
                else:
                    warn('"{}" not a file or directory', item)
        # Filter files we created in past runs.
        targets = [x for x in targets if '-reduced' not in x]
        targets = [x for x in targets if 'all-results' not in x]

        # If there is both a file in the format we generate and another
        # format of that file, ignore the other formats and just use ours.
        keep = []
        for item in targets:
            ext  = filename_extension(item)
            base = filename_basename(item)
            if ext != _OUTPUT_EXT and (base + _OUTPUT_EXT in targets):
                # png version of file is also present => skip this other version
                continue
            keep.append(item)
        return keep
