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

Copyright (c) 2018-2020 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from   boltons.debugutils import pdb_on_signal
import os
from   os import path, cpu_count
import plac
import signal
import sys
from   sys import exit as exit

if __debug__:
    from sidetrack import set_debug, log, logr

import handprint
from handprint import print_version
from handprint.credentials import Credentials
from handprint.data_utils import timestamp, plural
from handprint.exceptions import *
from handprint.exit_codes import ExitCode
from handprint.files import filename_extension, files_in_directory, is_url
from handprint.files import readable, writable
from handprint.interruptions import interrupt, interrupted
from handprint.main_body import MainBody
from handprint.network import disable_ssl_cert_check
from handprint.services import services_list
from handprint.ui import UI, inform, alert, alert_fatal, warn

# Disable certificate verification.  FIXME: probably shouldn't do this.
disable_ssl_cert_check()


# Main program.
# .............................................................................

@plac.annotations(
    add_creds  = ('add credentials file for service "A"',              'option', 'a'),
    base_name  = ('use base name "B" to name downloaded images',       'option', 'b'),
    compare    = ('compare text results to ground truth files',        'flag',   'c'),
    no_color   = ('do not color-code terminal output',                 'flag',   'C'),
    extended   = ('produce extended results (text file, JSON data)',   'flag',   'e'),
    from_file  = ('read list of images or URLs from file "F"',         'option', 'f'),
    no_grid    = ('do not create all-results grid image',              'flag',   'G'),
    list       = ('print list of known services',                      'flag',   'l'),
    output_dir = ('write output to directory "O"',                     'option', 'o'),
    quiet      = ('only print important messages while working',       'flag',   'q'),
    relaxed    = ('make --compare use more relaxed criteria',          'flag',   'r'),
    services   = ('invoke HTR/OCR service "S" (default: "all")',       'option', 's'),
    threads    = ('number of threads to use (default: #cores/2)',      'option', 't'),
    version    = ('print version info and exit',                       'flag',   'V'),
    debug      = ('write detailed trace to "OUT" ("-" means console)', 'option', '@'),
    files      = 'file(s), directory(ies) of files, or URL(s)',
)

def main(add_creds = 'A', base_name = 'B', compare = False, no_color = False,
         extended = False, from_file = 'F', no_grid = False, list = False,
         output_dir = 'O', quiet = False, relaxed = False, services = 'S',
         threads = 'T', version = False, debug = 'OUT', *files):
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
accept input images in JP2, JPEG, PDF, PNG, GIF, BMP, and TIFF formats.  To
make the results from different services more easily comparable, Handprint
will always convert all input images to the same format (PNG) no matter if
some services may accept other formats; it will also resize input images to
the smallest size accepted by any of the services invoked if an image exceeds
that size.  (For example, if service A accepts files up to 10 MB in size and
service B accepts files up to 5 MB, all input images will be resized to 5 MB
before sending them to A and B, even if A could accept a higher-resolution
image.)  In addition, a limitation of Handprint's current PDF support is that
only the first image in a PDF file is read -- if a PDF file contains
more than one image, the remaining images are ignored.

The default action is to run all known services.  The option -s (/s on
Windows) can be used to select only one service or a list of services
instead.  Lists of services should be separated by commas; e.g.,
"google,microsoft".  To find out which services are supported by Handprint, run
it with the command-line flag -l (or /l on Windows), which will make Handprint
print a list of the known services and exit immediately.

When performing OCR/HTR on images, Handprint temporarily (unless the -e
option is given -- see below) writes the results to new files that it creates
either in the same directories as the original files, or (if given the -o
option) the directory indicated by the -o option (/o on Windows).  The
results will be written in files named after the original files with the
addition of a string that indicates the service used.  For example, a file
named "somefile.jpg" will result in

  somefile.handprint-google.png
  somefile.handprint-microsoft.png
  somefile.handprint-amazon.png
  ...

and so on for each image and each service used.  THESE FILES ARE DELETED
after the final results grid image is created, UNLESS the -e option (/e on
Windows) is used to indicate that extended results should be produced; in that
case, these individual annotated image files are kept.

Visual display of recognition results
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After gathering the results of each service for a given input, Handprint will
create a single compound image consisting of all the annotated results images
arranged in a grid.  This is intended to make it easier to compare the
results of multiple services against each other.  To skip the creation of the
results grid, use the -G option (/G on Windows).  The grid image will be named

  somefile.handprint-all.png

If given the -e option (/e on Windows), Handprint will produce extended
output that includes the complete response from the service (converted to a
JSON file by Handprint) and the text extracted (stored as a .txt file).  The
output of -e will be multiple files like this:

  somefile.handprint-google.png
  somefile.handprint-google.json
  somefile.handprint-google.txt
  somefile.handprint-microsoft.png
  somefile.handprint-microsoft.json
  somefile.handprint-microsoft.txt
  somefile.handprint-amazon.png
  somefile.handprint-amazon.json
  somefile.handprint-amazon.txt
  ...

The files will written to the directory indicated by -o, or (if -o is not
used) the directory where "somefile" is located.  When -o is not used and
the input images are given as URLs, then the files are written to the current
working directory instead.

If an image is too large for any of the services invoked, then Handprint will
resize it prior to sending the image to any of the services (as noted above).
It will write the reduced image to a file named "FILENAME.handprint.EXT", where
"FILENAME" is the original file name and "EXT" is the file extension.  This
file is normally deleted, unless you use the -e option (/e on Windows)
mentioned above, in which case you will find this additional file in the same
location as the others:

  somefile.handprint.png

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

Finally, note that the use of the -G option (/G on Windows) WITHOUT either
the -e or -c option is an error because it means no output would be produced.

Comparing results to expected output
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Handprint supports comparing the output of HTR services to expected output
(i.e., ground truth) using the option -c (or /c on Windows).  This facility
requires that the user provides text files that contain the expected text
for each input image.  The ground-truth text files must have the following
characteristics:

 a) The file containing the expected results should be named ".gt.txt", with
    a base name identical to the image file.  For example, an image file named
    "somefile.jpg" should have a corresponding text file "somefile.gt.txt".

 b) The ground-truth text file should be located in the same directory as the
    input image file.

 c) The text should be line oriented, with each line representing a line of
    text in the image.

 d) The text should be plain text only.  No Unicode or binary encodings.
    (This limitation comes from the HTR services, which -- as of this
    writing -- return results in plain text format.)

Handprint will write the comparison results to a tab-delimited file named
after the input image and service but with the extension ".tsv".  For
example, for an input image "somefile.jpg" and results received from Google,
the comparison results will be written to "somefile.handprint-google.tsv".
(The use of a tab-delimited format rather than comma-delimited format avoids
the need to quote commas and other characters in the text.)

Handprint reports, for each text line, the number of errors (the Levenshtein
edit distance) and the character error rate (CER), and at the end it also
reports a sum total of errors.  The CER is computed as the Levenshtein edit
distance of each line divided by the number of characters in the expected
line text, multiplied by 100; this approach to normalizing the CER value is
conventional but note that it can lead to values greater than 100%.

By default, comparisons are done on an exact basis; character case is not
changed, punctuation is not removed, and stop words are not removed.
However, multiple contiguous spaces are converted to one space, and leading
spaces are removed from text lines.  If given the option -r (/r on Windows),
Handprint will relax the comparison algorithm as follows:

 i) convert all text to lower case
 ii) ignore certain sentence punctuation characters, namely , . : ;

Handprint attempts to cope with possibly-missing text in the HTR results by
matching up likely corresponding lines in the expected and received results.
It does this by comparing each line of ground-truth text to each line of the
HTR results using longest common subsequence similarity, as implemented by
the LCSSEQ function in the Python "textdistance" package.  If the lines do
not pass a threshold score, Handprint looks at subsequent lines of the HTR
results and tries to reestablish correspondence to ground truth.  If nothing
else in the HTR results appear close enough to the expected ground-truth
line, the line is assumed to be missing from the HTR results and scored
appropriately.

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

If given the -@ argument (/@ on Windows), this program will output a detailed
trace of what it is doing.  The debug trace will be sent to the given
destination, which can be '-' to indicate console output, or a file path to
send the output to a file.

When -@ (or /@ on Windows) has been given, Handprint installs a signal handler
on signal SIGUSR1 that will drop Handprint into the pdb debugger if the signal
is sent to the running process.  It's best to use -t 1 when attempting to use
a debugger because the subthreads will not stop running if the signal is sent.


Return values
~~~~~~~~~~~~~

This program exits with a return code of 0 if no problems are encountered.
It returns a nonzero value otherwise. The following table lists the possible
return values:

    0 = success -- program completed normally
    1 = the user interrupted the program's execution
    2 = encountered a bad or missing value for an option
    3 = no network detected -- cannot proceed
    4 = file error -- encountered a problem with a file
    5 = server error -- encountered a problem with a server
    6 = an exception or fatal error occurred

Command-line arguments summary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

    # Initial setup -----------------------------------------------------------

    prefix = '/' if sys.platform.startswith('win') else '-'
    hint = f'(Hint: use {prefix}h for help.)'
    ui = UI('Handprint', 'HANDwritten Page RecognitIoN Test',
            use_color = not no_color, be_quiet = quiet)
    ui.start()

    # Preprocess arguments and handle early exits -----------------------------

    if debug != 'OUT':
        if __debug__: set_debug(True, debug, extra = '%(threadName)s')
        import faulthandler
        faulthandler.enable()
        if not sys.platform.startswith('win'):
            # Even with a different signal, I can't get this to work on Win.
            pdb_on_signal(signal.SIGUSR1)

    # Handle arguments that involve deliberate exits.

    if version:
        print_version()
        exit(int(ExitCode.success))
    if list:
        inform('Known services: {}', ', '.join(services_list()))
        exit(int(ExitCode.success))
    if add_creds != 'A':
        service = add_creds.lower()
        if service not in services_list():
            alert(f'Unknown service: "{service}". {hint}')
            exit(int(ExitCode.bad_arg))
        if not files or len(files) > 1:
            alert(f'Option {prefix}a requires one file. {thing}')
            exit(int(ExitCode.bad_arg))
        creds_file = files[0]
        if not readable(creds_file):
            alert(f'File not readable: {creds_file}')
            exit(int(ExitCode.file_error))
        Credentials.save_credentials(service, creds_file)
        inform(f'Saved credentials for service "{service}".')
        exit(int(ExitCode.success))

    # Do sanity checks on some other arguments.

    services = services_list() if services == 'S' else services.lower().split(',')
    if services != 'S' and not all(s in services_list() for s in services):
        alert_fatal(f'"{services}" is not a known services. {hint}')
        exit(int(ExitCode.bad_arg))
    if no_grid and not extended and not compare:
        alert_fatal(f'{prefix}G without {prefix}e or {prefix}c produces no output. {hint}')
        exit(int(ExitCode.bad_arg))
    if any(item.startswith('-') for item in files):
        alert_fatal(f'Unrecognized option in arguments. {hint}')
        exit(int(ExitCode.bad_arg))
    if not files and from_file == 'F':
        alert_fatal(f'Need images or URLs to have something to do. {hint}')
        exit(int(ExitCode.bad_arg))
    if relaxed and not compare:
        warn(f'Option {prefix}r without {prefix}c has no effect. {hint}')

    # Do the real work --------------------------------------------------------

    if __debug__: log('='*8 + f' started {timestamp()} ' + '='*8)
    body = exception = None
    try:
        body = MainBody(files      = files,
                        from_file  = None if from_file == 'F' else from_file,
                        output_dir = None if output_dir == 'O' else output_dir,
                        add_creds  = None if add_creds == 'A' else add_creds,
                        base_name  = 'document' if base_name == 'B' else base_name,
                        make_grid  = not no_grid,
                        extended   = extended,
                        services   = services,
                        threads    = max(1, cpu_count()//2 if threads == 'T' else int(threads)),
                        compare    = 'relaxed' if (compare and relaxed) else compare)
        body.run()
        exception = body.exception
    except (KeyboardInterrupt, UserCancelled) as ex:
        if __debug__: log('received {}', sys.exc_info()[0].__name__)
        alert('Quit received; shutting down ...')
        interrupt()
        body.stop()
        exception = sys.exc_info()
    except Exception as ex:
        exception = sys.exc_info()

    # Try to deal with exceptions gracefully ----------------------------------

    exit_code = ExitCode.success
    if exception:
        if exception[0] == CannotProceed:
            exit_code = exception[1].args[0]
        elif exception[0] in [KeyboardInterrupt, UserCancelled]:
            if __debug__: log(f'received {exception.__class__.__name__}')
            warn('Interrupted.')
            exit_code = ExitCode.user_interrupt
        else:
            msg = str(exception[1])
            alert_fatal(f'Encountered error {exception[0].__name__}: {msg}')
            exit_code = ExitCode.exception
            if __debug__:
                from traceback import format_exception
                details = ''.join(format_exception(exception))
                logr(f'Exception: {msg}\n{details}')
    else:
        inform('Done.')
    if __debug__: log('_'*8 + f' stopped {timestamp()} ' + '_'*8)
    if exit_code == ExitCode.user_interrupt:
        os._exit(int(exit_code))
    else:
        exit(int(exit_code))


# Main entry point.
# .............................................................................

# On windows, we want plac to use slash intead of hyphen for cmd-line options.
if sys.platform.startswith('win'):
    main.prefix_chars = '/'

# The following entry point definition is for the console_scripts keyword
# option to setuptools.  The entry point for console_scripts has to be a
# function that takes zero arguments.
def console_scripts_main():
    plac.call(main)

# The following allows users to invoke this using "python3 -m handprint".
if __name__ == '__main__':
    plac.call(main)
