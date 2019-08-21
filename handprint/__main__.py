'''Handprint: HANDwritten Page RecognitIoN Test

This project uses alternative text recognition services on images of
documents containing handwritten text.  The services currently supported are
the following, but additional services could be supported by adding suitable
wrappers:

* Microsoft Azure
  https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision

* Google Cloud Vision API
  https://cloud.google.com/vision/docs/ocr

* Amazon Textract and Rekognition
  https://docs.aws.amazon.com/textract
  https://docs.aws.amazon.com/rekognition

Handprint can be given image files, or directories of image files, or URLs
pointing to image files.  It will download images if necessary, resize them
if necessary, send them to the services, wait for the results, and finally,
create annotated versions of the images with the recognized text overlayed
on top of the image.

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
import plac
import sys
from   sys import exit as exit

import handprint
from handprint.credentials import Credentials
from handprint.debug import set_debug, log
from handprint.exceptions import *
from handprint.files import filename_extension, files_in_directory, is_url
from handprint.files import readable, writable
from handprint.main_body import MainBody
from handprint.manager import Manager
from handprint.messages import MessageHandlerCLI, styled
from handprint.network import disable_ssl_cert_check
from handprint.services import services_list

# Disable certificate verification.  FIXME: probably shouldn't do this.
disable_ssl_cert_check()


# Main program.
# .............................................................................

@plac.annotations(
    add_creds  = ('add credentials file for service "A"',            'option', 'a'),
    base_name  = ('use base name "B" to name downloaded images',     'option', 'b'),
    no_color   = ('do not color-code terminal output',               'flag',   'C'),
    extended   = ('produce extended results (text file, JSON data)', 'flag',   'e'),
    from_file  = ('read list of images or URLs from file "F"',       'option', 'f'),
    no_grid    = ('do not create all-results grid image',            'flag',   'G'),
    list       = ('print list of known services',                    'flag',   'l'),
    output_dir = ('write output to directory "O"',                   'option', 'o'),
    quiet      = ('only print important messages while working',     'flag',   'q'),
    services   = ('invoke HTR/OCR service "S" (default: "all")',     'option', 's'),
    threads    = ('number of threads to use (default: #cores/2)',    'option', 't'),
    version    = ('print version info and exit',                     'flag',   'V'),
    debug      = ('turn on debug tracing & exception catching',      'flag',   '@'),
    files      = 'file(s), directory(ies) of files, or URL(s)',
)

def main(add_creds = 'A', base_name = 'B', no_color = False, extended = False,
         from_file = 'F', no_grid = False, list = False, output_dir = 'O',
         quiet = False, services = 'S', threads = 'T', version = False,
         debug = False, *files):
    '''Handprint (a loose acronym of "HANDwritten Page RecognitIoN Test") runs
alternative text recognition services on images of handwritten document pages.

Installing credentials for cloud-based services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If given the command-line flag -l (or /l on Windows), Handprint will print a
list of the known services, and exit.

Before a given service can be used, if it is cloud-based commercial OCR/HTR
service, Handprint needs to be supplied with user credentials for accessing
that service.  The credentials must be stored in a JSON file with a certain
format; see the Handprint user documentation for details about the formats
for each service.  To add a new credentials file, use the -a option (/a on
Windows) in combination with the name of a service and a single file path on
the command line.  The name supplied right after the -a option must be the
name of a recognized service (such as "google", "amazon", "microsoft"), and
the file argument must be a JSON file containing the credentials data in the
required format for that service.  Here is an example of adding credentials
for Google (assuming you created the JSON file as described in the docs):

  handprint -a google mygooglecreds.json

Run Handprint with the -a option multiple times to install credentials for
each different service.  Handprint will copy the credential files to its own
configuration directory and exit without doing anything else.  The directory
is different on different operating sytems; for example, on macOS it
is ~/Library/Application Support/Handprint/.

Basic usage
~~~~~~~~~~~

After credentials are installed, running Handprint without the -a option will
invoke one or more OCR/HTR services on files, directories of files, or URLs.
The image paths or URLs can be supplied in any of the following ways:

 a) one or more directory paths or one or more image file paths, which will
    be interpreted as images (either individually or in directories) to be
    processed;

 b) one or more URLs, which will be interpreted as network locations of image
    files to be processed; or

 c) if given the -f option (/f on Windows), a file containing either image
    paths or image URLs.

If given URLs, Handprint will first download the images found at the URLs to
a local directory indicated by the option -o (/o on Windows).  Handprint can
accept input images in JPEG, PNG, GIF, BMP, and TIFF formats.  To make the
results from different services more easily comparable, Handprint will always
convert all input images to the same format (PNG) no matter if some services
may accept other formats; it will also resize input images to the smallest
size accepted by any of the services invoked if an image exceeds that size.
(For example, if service A accepts files up to 10 MB in size and service B
accepts files up to 5 MB, all input images will be resized to 5 MB before
sending them to A and B, even if A could accept a higher-resolution image.)

The default action is to run all known services; the option -s (/s on
Windows) can be used to select only one service or a list of services
instead.  Lists of services should be separated by commas; e.g.,
"google,microsoft".

When performing OCR/HTR on images, Handprint temporarily (unless the -e
option is given -- see below) writes the results to new files that it creates
either in the same directories as the original files, or (if given the -o
option) the directory indicated by the -o option (/o on Windows).  The
results will be written in files named after the original files with the
addition of a string that indicates the service used.  For example, a file
named "somefile.jpg" will result in

  somefile.google.png
  somefile.microsoft.png
  somefile.amazon.png
  ...

and so on for each image and each service used.  These files are deleted
after the final results grid image is created, unless the -e option (/e on
Windows) is used to indicate that extended results should be produced; in that
case, these individual annotated image files are kept.

After gathering the results of each service for a given input, Handprint will
create a single compound image consisting of all the annotated results images
arranged in a grid.  This is intended to make it easier to compare the
results of multiple services against each other.  To skip the creation of the
results grid, use the -G option (/G on Windows).  The grid image will be named

  somefile.all-results.png

If given the -e option (/e on Windows), Handprint will produce extended
output that includes the complete response from the service (converted to a
JSON file by Handprint) and the text extracted (stored as a .txt file).  The
output of -e will be multiple files like this:

  somefile.google.png
  somefile.google.json
  somefile.google.txt
  somefile.microsoft.png
  somefile.microsoft.json
  somefile.microsoft.txt
  somefile.amazon.png
  somefile.amazon.json
  somefile.amazon.txt
  ...

The files will written to the directory indicated by -o, or (if -o is not
used) the directory where "somefile" is located.  When -o is not used and
the input images are given as URLs, then the files are written to the current
working directory instead.

If an image is too large for any of the services invoked, then Handprint will
resize it prior to sending the image to any of the services (as noted above).
It will write the reduced image to a file named "FILENAME-reduced.EXT", where
"FILENAME" is the original file name and "EXT" is the file extension.  This
means that if an image needs to be resized, the results of applying the text
recognition services will be, e.g.,

  somefile-reduced.png
  somefile-reduced.google.png
  somefile-reduced.google.json
  somefile-reduced.google.txt
  somefile-reduced.microsoft.png
  somefile-reduced.microsoft.json
  somefile-reduced.microsoft.txt
  somefile-reduced.amazon.json
  somefile-reduced.amazon.png
  somefile-reduced.amazon.txt
  ...

When the inputs are URLs, Handprint must download a copy of the image located
at the network address (because it is not possible to write the results in
the network locations represented by the URLs.).  The images and other
results will be stored files whose root names have the form "document-N",
where "N" is an integer.  The root name can be changed using the -b option
(/b on Windows).  The image at networked locations will be converted to
ordinary PNG format for maximum compatibility with the different OCR
services and written to "document-N.png", and the URL corresponding to each
document will be written in a file named "document-N.url" so that it is
possible to connect each "document-N.png" to the URL it came from.

Finally, note that the use of the -G option (/G on Windows) WITHOUT the -e
option is an error because it means no output would be produced.

Additional command-line arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

If given the -@ option (/@ on Windows), this program will print additional
diagnostic output as it runs; in addition, it will start the Python debugger
(pdb) when an exception occurs, instead of simply exiting.

Command-line arguments summary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

    # Initial setup -----------------------------------------------------------

    say = MessageHandlerCLI(not no_color, quiet)
    prefix = '/' if sys.platform.startswith('win') else '-'
    hint = '(Hint: use {}h for help.)'.format(prefix)
    make_grid = not no_grid

    # Preprocess arguments and handle early exits -----------------------------

    if debug:
        set_debug(True)
    if version:
        print_version()
        exit()
    if list:
        say.info('Known services: {}'.format(', '.join(services_list())))
        exit()

    if add_creds != 'A':
        service = add_creds.lower()
        if service not in services_list():
            exit(say.error_text('Unknown service: "{}". {}'.format(service, hint)))
        if not files or len(files) > 1:
            exit(say.error_text('Option {}a requires one file. {}'.format(prefix, hint)))
        creds_file = files[0]
        if not readable(creds_file):
            exit(say.error_text('File not readable: {}'.format(creds_file)))
        Credentials.save_credentials(service, creds_file)
        exit(say.info_text('Saved credentials for service "{}".'.format(service)))

    if no_grid and not extended:
        exit(say.error_text('{}G without {}e produces no output. {}'.format(
            prefix, prefix, hint)))
    if any(item.startswith('-') for item in files):
        exit(say.error_text('Unrecognized option in arguments. {}'.format(hint)))
    if not files and from_file == 'F':
        exit(say.error_text('Need provide images or URLs. {}'.format(hint)))

    services = services_list() if services == 'S' else services.lower().split(',')
    if not all(s in services_list() for s in services):
        exit(say.error_text('"{}" is not a known services. {}'.format(services, hint)))

    base_name  = 'document' if base_name == 'B' else base_name
    from_file  = None if from_file == 'F' else from_file
    output_dir = None if output_dir == 'O' else output_dir

    # Do the real work --------------------------------------------------------

    try:
        print_intro(say)
        body = MainBody(base_name, extended, from_file, output_dir, threads, say)
        body.run(services, files, make_grid)
    except (KeyboardInterrupt, UserCancelled) as ex:
        if __debug__: log('received {}', sys.exc_info()[0].__name__)
        exit(say.info_text('Quitting.'))
    except Exception as ex:
        if debug:
            import traceback
            say.error('{}\n{}'.format(str(ex), traceback.format_exc()))
            import pdb; pdb.set_trace()
        else:
            exit(say.error_text(str(ex)))
    say.info('Done.')


# Helper functions.
# .............................................................................

def print_version():
    print('{} version {}'.format(handprint.__title__, handprint.__version__))
    print('Author: {}'.format(handprint.__author__))
    print('URL: {}'.format(handprint.__url__))
    print('License: {}'.format(handprint.__license__))
    print('')
    print('Known services: {}'.format(', '.join(services_list())))
    print('Credentials are stored in {}'.format(Credentials.credentials_dir()))


def print_intro(say):
    if say.use_color():
        cb = ['chartreuse', 'bold']
        name = styled('Handprint', cb)
        acronym = '{}written {}age {}ecognit{}o{} {}est'.format(
            styled('Hand', cb), styled('p', cb), styled('r', cb),
            styled('i', cb), styled('n', cb), styled('t', cb))
    else:
        name = 'Handprint'
        acronym = 'HANDwritten Page RecognItioN Test'
    say.info('┏' + '━'*68 + '┓')
    say.info('┃    Welcome to {}, the {}!    ┃'.format(name, acronym))
    say.info('┗' + '━'*68 + '┛')


# Main entry point.
# .............................................................................

# On windows, we want plac to use slash intead of hyphen for cmd-line options.
if sys.platform.startswith('win'):
    main.prefix_chars = '/'

# The following allows users to invoke this using "python3 -m handprint".
if __name__ == '__main__':
    plac.call(main)
