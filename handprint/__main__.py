'''Handprint: HANDwritten Page RecognitIoN Test for Caltech Archives.

This project uses alternative text recognition services on documents from the
Caltech Archives (http://archives.caltech.edu).  Tests include the use of
Google's OCR capabilities in their Google Cloud Vision API
(https://cloud.google.com/vision/docs/ocr), Microsoft's Azure, and others.

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018-2019 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from   halo import Halo
import io
import json
import os
from   os import path
import plac
import requests
import shutil
import sys
from   sys import exit as exit
try:
    from termcolor import colored
except:
    pass
import time
from   timeit import default_timer as timer
import traceback
from   urllib import request

import handprint
from handprint.constants import ON_WINDOWS, ACCEPTED_FORMATS, KNOWN_SERVICES
from handprint.credentials import Credentials
from handprint.debug import set_debug, log
from handprint.exceptions import *
from handprint.files import filename_extension, files_in_directory, is_url
from handprint.files import readable, writable
from handprint.manager import Manager
from handprint.messages import msg, color, MessageHandlerCLI
from handprint.network import network_available, disable_ssl_cert_check
from handprint.processes import available_cpus

# Disable certificate verification.  FIXME: probably shouldn't do this.
disable_ssl_cert_check()


# Main program.
# ......................................................................

@plac.annotations(
    add_creds  = ('add credentials file for service "A"',              'option', 'a'),
    base_name  = ('use base name "B" to name downloaded images',       'option', 'b'),
    no_color   = ('do not color-code terminal output',                 'flag',   'C'),
    extended   = ('produce extended results',                          'flag',   'e'),
    from_file  = ('read list of images or URLs from file "F"',         'option', 'f'),
    list       = ('print list of known services',                      'flag',   'l'),
    output_dir = ('write output to directory "O"',                     'option', 'o'),
    quiet      = ('do not print info messages while working',          'flag',   'q'),
    service    = ('process images using service "S" (default: "all")', 'option', 's'),
    threads    = ('num. threads to use (default: #cores/2)',           'option', 't'),
    version    = ('print version info and exit',                       'flag',   'V'),
    debug      = ('turn on debugging',                                 'flag',   'Z'),
    files      = 'file(s), directory(ies) of files, or URL(s)',
)

def main(add_creds = 'A', base_name = 'B', no_color = False, extended = False,
         from_file = 'F', list = False, output_dir = 'O', quiet = False,
         service = 'S', threads = 'T', version = False, debug = False, *files):
    '''Handprint (a loose acronym of "HANDwritten Page RecognitIoN Test") runs
alternative text recognition services on images of handwritten document pages.

If given the command-line flag -l (or /l on Windows), Handprint will print a
list of the known services, and exit.

Before a given service can be used, if it is cloud-based commercial OCR/HTR
service, Handprint needs to be supplied with user credentials for accessing
that service.  The credentials must be stored in a JSON file with a certain
format; see the Handprint user documentation for details about the formats
for each service.  To add a new credentials file, use the -a option (/a on
Windows) in combination with the name of a service and a single file path on
the command line.  The name given right after the -a option must be the name
of a recognized service (such as "google", "amazon", "microsoft"), and the
file argument must be a JSON file containing the credentials data in the
required format for that service.  Here is an example of adding credentials
for Google (assuming you created the JSON file as described in the docs):

  handprint -a google path/to/mygooglecreds.json

Run the command-line interface with the -a option multiple times to install
credentials for each different service.  Handprint will copy the credential
files to its own configuration directory and exit without doing anything
else.  The configuration directory is different on different operating
sytems; for example, it is ~/Library/Application Support/Handprint on macOS.

After credentials are installed, running Handprint without the -a option will
invoke one or more OCR/HTR services on files, directories of files, or URLs.
The default action is to run all known services; the option -s (/s on
Windows) can be used to select one specific service instead.  The image paths
or URLs can be supplied in any of the following ways:

 a) one or more directory paths or one or more image file paths, which will
    be interpreted as images (either individually or in directories) to be
    processed;

 b) one or more URLs, which will be interpreted as network locations of image
    files to be processed; or

 c) if given the -f option (/f on Windows), a file containing either image
    paths or image URLs.

If given URLs, Handprint will first download the images found at the URLs to
a local directory indicated by the option -o (/o on Windows).

When performing OCR/HTR on images, Handprint writes the results to new files
that it creates either in the same directories as the original files, or (if
given the -o option) the directory indicated by the -o option (/o on Windows).
The results will be written in files named after the original files with the
addition of a string that indicates the service used.  For example, a file
named "somefile.jpg" will produce

  somefile.jpg
  somefile.google.jpg
  somefile.microsoft.jpg
  somefile.amazon.jpg
  ...

and so on for each image and each service used.

By default, Handprint will produce only one type of output: an annotated JPEG
image files showing the recognized words superimposed over the original
image.  If given the -e option (/e on Windows), Handprint will produce
extended output that includes the complete response from the service
(converted to a JSON file by Handprint) and the text extracted (stored as a
.txt file).  The output of -e will be multiple files like this:

  somefile.jpg
  somefile.google.jpg
  somefile.google.json
  somefile.google.txt
  somefile.microsoft.jpg
  somefile.microsoft.json
  somefile.microsoft.txt
  somefile.amazon.jpg
  somefile.amazon.json
  somefile.amazon.txt
  ...

If images are too large for a service, then Handprint will resize them prior
to sending them.  It will write the reduced image to a file named
"FILENAME-reduced.EXT", where "FILENAME" is the original file name and "EXT"
is the file extension.  This means that if an image needs to be resized, the
results of applying the text recognition services will be, e.g.,

  somefile-reduced.jpg
  somefile-reduced.google.jpg
  somefile-reduced.google.json
  somefile-reduced.google.txt
  somefile-reduced.microsoft.jpg
  somefile-reduced.microsoft.json
  somefile-reduced.microsoft.txt
  somefile-reduced.amazon.json
  somefile-reduced.amazon.jpg
  somefile-reduced.amazon.txt
  ...

When the inputs are URLs, Handprint must download a copy of the image located
at the network address (because it is not possible to write the results in
the network locations represented by the URLs.).  This means the -o (/o on
Windows) option is required if any of the inputs are URLs.  The images and
other results will be stored files whose root names have the form
"document-N", where "N" is an integer.  The root name can be changed using
the -b option (/b on Windows).  The image at networked locations will be
converted to ordinary JPEG format for maximum compatibility with the
different OCR services and written to "document-N.jpg", and the URL
corresponding to each document will be written in a file named
"document-N.url" so that it is possible to connect each "document-N.jpg" to
the URL it came from.

Handprint will send files to the different services in parallel, using a
number of process threads equal to 1/2 of the number of cores on the computer
it is running on.  (E.g., if your computer has 4 cores, it will by default use
at most 2 threads.)  The option -t (/t on Windows) can be used to change this
number.

If given the -q option (/q on Windows), Handprint will not print its usual
informational messages while it is working.  It will only print messages
for warnings or errors.  By default messages printed by Handprint are also
color-coded.  If given the option -C (/C on Windows), Handprint will not color
the text of messages it prints.  (This latter option is useful when running
Handprint within subshells inside other environments such as Emacs.)

If given the -V option (/V on Windows), this program will print the version
and other information, and exit without doing anything else.
'''

    # Initial setup -----------------------------------------------------------

    say = MessageHandlerCLI(not no_color, quiet)
    prefix = '/' if ON_WINDOWS else '-'
    hint = '(Hint: use {}h for help.)'.format(prefix)

    # Process arguments -------------------------------------------------------

    if debug:
        set_debug(True)
    if version:
        print_version()
        exit()
    if list:
        say.info('Known services: {}'.format(services_list()))
        exit()

    if add_creds != 'A':
        service = add_creds.lower()
        if service not in KNOWN_SERVICES:
            exit(say.error_text('"{}" is not a known service. {}'.format(service, hint)))
        if not files or len(files) > 1:
            exit(say.error_text('Must supply a single file with {}a. {}'.format(prefix, hint)))
        creds_file = files[0]
        if not readable(creds_file):
            exit(say.error_text('File not readable: {}'.format(creds_file)))
        Credentials.save_credentials(service, creds_file)
        exit(say.info_text('Saved credentials file for service "{}".'.format(service)))

    if not network_available():
        exit(say.fatal_text('No network.'))

    if from_file == 'F':
        from_file = None
    else:
        if not path.exists(from_file):
            exit(say.error_text('File not found: {}'.format(from_file)))
        if not readable(from_file):
            exit(say.error_text('File not readable: {}'.format(from_file)))

    if not files and not from_file:
        exit(say.error_text('Need provide images or URLs. {}'.format(hint)))
    if any(item.startswith('-') for item in files):
        exit(say.error_text('Unrecognized option in arguments. {}'.format(hint)))

    service = service.lower() if service != 'S' else 'all'
    if service != 'all' and service not in KNOWN_SERVICES:
        exit(say.error_text('"{}" is not a known service. {}'.format(service, hint)))

    if output_dir == 'O':
        output_dir = None
    else:
        if path.isdir(output_dir):
            if not writable(output_dir):
                exit(say.error_text('Directory not writable: {}'.format(output_dir)))
        else:
            os.mkdir(output_dir)
            if __debug__: log('Created output_dir directory {}', output_dir)

    if base_name == 'B':
        base_name = 'document'

    # Do the real work --------------------------------------------------------

    targets = targets_from_arguments(files, from_file, say)
    if not targets:
        exit(say.warn_text('No images to process; quitting.'))

    try:
        num = len(targets)
        print_separators = num > 1 and not say.be_quiet()
        procs = int(max(1, available_cpus()/2 if threads == 'T' else int(threads)))

        if service == 'all':
            # Order doesn't really matter; just make it consistent run-to-run.
            services = sorted(KNOWN_SERVICES.values(), key = lambda x: str(x))
            say.info('Will apply all known services to {} image{}.'.format(
                num, 's' if num > 1 else ''))
        else:
            services = [KNOWN_SERVICES[service]]
            say.info('Will apply service "{}" to {} images.'.format(service, num))

        manager = Manager(services, procs, output_dir, extended, say)
        for index, item in enumerate(targets, start = 1):
            if print_separators:
                say.msg('='*70, 'dark')
            manager.process(item, index, base_name)
        if print_separators:
            say.msg('='*70, 'dark')
    except (KeyboardInterrupt, UserCancelled) as ex:
        exit(say.info_text('Quitting.'))
    except ServiceFailure as ex:
        exit(say.error_text(str(ex)))
    except Exception as ex:
        if debug:
            say.error('{}\n{}'.format(str(ex), traceback.format_exc()))
            import pdb; pdb.set_trace()
        else:
            exit(say.error_text('{}', str(ex)))

    say.info('Done.')


# If this is windows, we want the command-line args to use slash intead
# of hyphen.

if ON_WINDOWS:
    main.prefix_chars = '/'


# Helper functions.
# ......................................................................

def targets_from_arguments(files, from_file, say):
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
                # (These are files that end in, e.g., ".google.jpg")
                handprint_endings = ['.' + x + '.jpg' for x in KNOWN_SERVICES.keys()]
                files = files_in_directory(item, extensions = ACCEPTED_FORMATS)
                files = filter_endings(files, handprint_endings)
                targets += files
            else:
                say.warn('"{}" not a file or directory'.format(item))
    return targets


def filter_endings(item_list, endings):
    if not item_list:
        return []
    if not endings:
        return item_list
    results = item_list
    for ending in endings:
        results = list(filter(lambda name: ending not in name.lower(), results))
    return results


def print_version():
    print('{} version {}'.format(handprint.__title__, handprint.__version__))
    print('Author: {}'.format(handprint.__author__))
    print('URL: {}'.format(handprint.__url__))
    print('License: {}'.format(handprint.__license__))
    print('')
    print('Known services: {}'.format(services_list()))
    print('Credentials are stored in {}'.format(Credentials.credentials_dir()))


def services_list():
    return ', '.join(sorted(KNOWN_SERVICES.keys()))



# Main entry point.
# ......................................................................
# The following allows users to invoke this using "python3 -m handprint".

if __name__ == '__main__':
    plac.call(main)


# For Emacs users
# ......................................................................
# Local Variables:
# mode: python
# python-indent-offset: 4
# End:
