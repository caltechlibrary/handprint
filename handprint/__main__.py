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

Copyright (c) 2018-2022 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import sys
from   sys import exit as exit
if sys.version_info <= (3, 8):
    print('Handprint requires Python version 3.8 or higher,')
    print('but the current version of Python is ' +
          str(sys.version_info.major) + '.' + str(sys.version_info.minor) + '.')
    exit(6)

from   boltons.debugutils import pdb_on_signal
from   bun import UI, inform, alert, alert_fatal, warn
from   commonpy.data_utils import timestamp
from   commonpy.file_utils import filename_extension, files_in_directory
from   commonpy.file_utils import readable, writable
from   commonpy.interrupt import config_interrupt, interrupt, interrupted
from   commonpy.string_utils import antiformat
from   fastnumbers import fast_real, isreal, isint
import os
from   os import path, cpu_count
import plac
import signal

if __debug__:
    from sidetrack import set_debug, log

import handprint
from handprint import print_version
from handprint.credentials import Credentials
from handprint.exceptions import *
from handprint.exit_codes import ExitCode
from handprint.main_body import MainBody
from handprint.services import services_list


# Main program.
# .............................................................................

@plac.annotations(
    add_creds  = ('add credentials file for service "A"',                  'option', 'a'),
    base_name  = ('use base name "B" to name downloaded images',           'option', 'b'),
    no_color   = ('do not colorize output printed to the terminal',        'flag',   'C'),
    compare    = ('compare text results to ground truth files',            'flag',   'c'),
    display    = ('annotations to display (default: text)',                'option', 'd'),
    extended   = ('produce extended results (text file, JSON data)',       'flag',   'e'),
    from_file  = ('read list of images or URLs from file "F"',             'option', 'f'),
    no_grid    = ('do not create an all-results grid image',               'flag',   'G'),
    reuse_json = ('look for prior JSON results for the inputs & use them', 'flag',   'j'),
    list       = ('print list of known services',                          'flag',   'l'),
    text_move  = ('move position of text annotations by x,y (see help)',   'option', 'm'),
    confidence = ('only keep results with confidence scores >= N',         'option', 'n'),
    output_dir = ('write output to directory "O"',                         'option', 'o'),
    quiet      = ('only print important messages while working',           'flag',   'q'),
    relaxed    = ('make --compare use more relaxed criteria',              'flag',   'r'),
    services   = ('invoke HTR/OCR service "S" (default: "all")',           'option', 's'),
    threads    = ('number of threads to use (default: #cores/2)',          'option', 't'),
    version    = ('print version info and exit',                           'flag',   'V'),
    text_color = ('use color "X" for text annotations (default: red)',     'option', 'x'),
    text_size  = ('use font size "Z" for text annotations (default: 10)',  'option', 'z'),
    debug      = ('write detailed trace to "OUT" ("-" means console)',     'option', '@'),
    files      = 'file(s), directory(ies) of files, or URL(s)',
)

def main(add_creds = 'A', base_name = 'B', no_color = False, compare = False,
         display = 'D', extended = False, from_file = 'F', no_grid = False,
         list = False, reuse_json = False, text_move = 'M', confidence = 'N',
         output_dir = 'O', quiet = False, relaxed = False, services = 'S',
         threads = 'T', version = False, text_color = 'X', text_size = 'Z',
         debug = 'OUT', *files):
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
Here is an example of running Handprint on a directory containing images:

  handprint tests/data/caltech-archives/glaser/

Image paths or URLs can be supplied to Handprint in any of the following ways:

 a) one or more directory paths or one or more image file paths, which will
    be interpreted as images (either individually or in directories) to be
    processed;

 b) one or more URLs, which will be interpreted as network locations of image
    files to be processed; or

 c) if given the -f option (/f on Windows), a file containing either image
    paths or image URLs.

Note that providing URLs on the command line can be problematic due to how
terminal shells interpret certain characters, and so when supplying URLs,
it's usually better to store the URLs in a file and use the -f option.
Regardless, when given URLs, Handprint will first download the images to a
local directory indicated by the option -o (/o on Windows), or the current
directory if option -o is not used.

No matter whether files or URLs, each input should be a single image of a
document page in which text should be recognized.  Handprint can accept input
images in JP2, JPEG, PDF, PNG, GIF, BMP, and TIFF formats. To make the
results from different services more easily comparable, Handprint will always
convert all input images to the same format (PNG) no matter if some services
may accept other formats; it will also downsize input images to the smallest
size accepted by any of the services invoked if an image exceeds that size.
(For example, if service A accepts files up to 10 MB in size and service B
accepts files up to 4 MB, all input images will be resized to 4 MB before
sending them to both A and B, even if A could accept a higher- resolution
image.)  Finally, if the input contains more than one page (e.g., in a PDF
file), Handprint will only use the first page and ignore the rest.

Be aware that resizing images to the lowest common size means that the text
recognition results returned by some services may be different than if the
original full-size input image had been sent to that service.  If your images
are larger (when converted to PNG) than the size threshold for some services
(which is currently 4 MB when Microsoft is one of the destinations), then you
may wish to compare the results of using multiple services at once versus
using the services one at a time.

Selecting destination services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The default action is to run all known services.  The option -s (/s on
Windows) can be used to select only one service or a list of services
instead.  Lists of services should be separated by commas; e.g.,
"google,microsoft".  To find out which services are supported by Handprint, run
it with the command-line flag -l (or /l on Windows), which will make Handprint
print a list of the known services and exit immediately.

Visual display of recognition results
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After gathering the results of each service for a given input, Handprint will
create a single compound image consisting of the results for each service
arranged in a grid.  This is intended to make it easier to compare the results
of multiple services against each other.  To skip the creation of the results
grid, use the -G option (/G on Windows).  The grid image have a name with
the following pattern:

  somefile.handprint-all.png

If given the -e option (/e on Windows), Handprint will produce extended
output that includes the complete response from the service (converted to a
JSON file by Handprint) and the text extracted (stored as a .txt file).  The
output of -e will be multiple files like this:

  somefile.handprint-amazon-rekognition.json
  somefile.handprint-amazon-rekognition.png
  somefile.handprint-amazon-rekognition.txt
  somefile.handprint-amazon-textract.json
  somefile.handprint-amazon-textract.png
  somefile.handprint-amazon-textract.txt
  somefile.handprint-google.json
  somefile.handprint-google.png
  somefile.handprint-google.txt
  somefile.handprint-microsoft.json
  somefile.handprint-microsoft.png
  somefile.handprint-microsoft.txt
  ...

The files will be written to the directory indicated by -o, or (if -o is not
used) the directory where "somefile" is located.  When -o is not used and
the input images are given as URLs, then the files are written to the current
working directory instead.

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

Type of annotations
~~~~~~~~~~~~~~~~~~~

Handprint produces copies of the input images overlayed with the recognition
results received from the different services.  By default, it shows only the
recognized text.  The option -d (/d on Windows) can be used to tell Handprint
to display other results.  The recognized values are as follows:

  text    -- display the text recognized in the image (default)
  bb      -- display all bounding boxes returned by the service
  bb-word -- display only the bounding boxes for words (in red)
  bb-line -- display only the bounding boxes for lines (in blue)
  bb-para -- display only the bounding boxes for paragraphs (in green)

Separate multiple values with a comma.  The option "bb" is a shorthand for the
value "bb-word,bb-line,bb-para".  As an example, the following command will
show both the recognized text and the bounding boxes around words:

  handprint -d text,bb-word  somefile.png

Note that as of June 2021, the main services (Amazon, Google, Microsoft) do not
all provide the same bounding box information in their results.  The following
table summarizes what is available:

               Bounding boxes available
  Service      Word    Line   Paragraph
  ---------    ----    ----   ---------
  Amazon         Y       Y        -
  Google         Y       -        Y
  Microsoft      Y       Y        -

If a service does not provide a particular kind of bounding box, Handprint will
not display that kind of bounding box in the annotated output for that service.

Thresholding by confidence
~~~~~~~~~~~~~~~~~~~~~~~~~~

All of the services return confidence scores for items recognized in the input.
By default, Handprint will show all results in the annotated image, no matter
how low the score.  The option -n (/n on Windows) can be used to threshold the
results based on the confidence value for each item (text or bounding boxes).
The value provided as the argument to -n must be a floating point number
between 0 and 1.0.  For example, the following command will make Handprint only
show text that is rated with least 99.5% confidence:

  handprint -n 0.995  somefile.png

Note that the confidence values returned by the different services are not
normalized against each other.  What one service considers to be 80% confidence
may not be what another service considers 80% confidence.  Handprint performs
the thresholding against the raw scores returned by each service individually.

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

The option -j (/j on Windows) tells Handprint to look for and reuse preexisting
results for each input instead of contacting the services.  This makes it look
for JSON files produced in a previous run with the -e option,

  somefile.handprint-amazon-rekognition.json
  somefile.handprint-amazon-textract.json
  somefile.handprint-google.json
  somefile.handprint-microsoft.json

and use those instead of getting results from the services.  This can be useful
to save repeated invocations of the services if all you want is to draw the
results differently or perform some testing/debugging on the same inputs.

To move the position of the text annotations overlayed over the input image,
you can use the option -m (or /m on Windows).  This takes two numbers separated
by a comma in the form x,y.  Positive numbers move the text rightward and
upward, respectively, relative to the default position.  The default position
of each text annotation in the annotated output is such that the left edge of
the word starts at the location of the upper left corner of the bounding box
returned by the service; this has the effect of putting the annotation near,
but above, the location of the (actual) word in the input image by default.
Using the text-move option allows you to move the annotation if desired.

To change the color of the text annotations overlayed over the input image,
you can use the option -x (or /x on Windows).  You can use hex color codes
such as "#ff0000" or X11/CSS4 color names with no spaces such as "purple"
or "darkgreen".  If you use a hex value, make sure to enclose the value with
quotes, or the shell will interpret the pound sign as a comment character.

To change the size of the text annotations overlayed over the input image,
you can use the option -z (or /z on Windows).  The value is in units of points.
The default size is 12 points.

Handprint will send files to the different services in parallel, using a
number of process threads at most equal to 1/2 of the number of cores on the
computer it is running on.  (E.g., if your computer has 4 cores, it will by
default use at most 2 threads.)  The option -t (/t on Windows) can be used to
change this number.

If given the -q option (/q on Windows), Handprint will not print its usual
informational messages while it is working.  It will only print messages
for warnings or errors.  By default messages printed by Handprint are also
color-coded.  If given the option -Z (/Z on Windows), Handprint will not color
the text of messages it prints.  (This latter option is useful when running
Handprint within subshells inside other environments such as Emacs.)

If given the -@ argument (/@ on Windows), this program will output a detailed
trace of what it is doing.  The debug trace will be sent to the given
destination, which can be '-' to indicate console output, or a file path to
send the output to a file.

When -@ (or /@ on Windows) has been given, Handprint installs a signal handler
on signal SIGUSR1 that will drop Handprint into the pdb debugger if the signal
is sent to the running process.  It's best to use -t 1 when attempting to use
a debugger because the subthreads will not stop running if the signal is sent.

If given the -V option (/V on Windows), this program will print the version
and other information, and exit without doing anything else.

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

    pref = '/' if sys.platform.startswith('win') else '-'
    hint = f'(Hint: use {pref}h for help.)'
    ui = UI('Handprint', 'HANDwritten Page RecognitIoN Test',
            use_color = not no_color, be_quiet = quiet,
            show_banner = not (version or list or add_creds != 'A'))
    ui.start()

    if debug != 'OUT':
        if __debug__: set_debug(True, debug, extra = '%(threadName)s')
        import faulthandler
        faulthandler.enable()
        if not sys.platform.startswith('win'):
            # Even with a different signal, I can't get this to work on Win.
            pdb_on_signal(signal.SIGUSR1)

    # Preprocess arguments and handle early exits -----------------------------

    if version:
        print_version()
        exit(int(ExitCode.success))
    if list:
        inform('Known services: [bold]{}[/]', ', '.join(services_list()))
        exit(int(ExitCode.success))
    if add_creds != 'A':
        service = add_creds.lower()
        if service not in services_list():
            alert(f'Unknown service: "{service}". {hint}')
            exit(int(ExitCode.bad_arg))
        if not files or len(files) > 1:
            alert(f'Option {pref}a requires one file. {hint}')
            exit(int(ExitCode.bad_arg))
        creds_file = files[0]
        if not readable(creds_file):
            alert(f'File not readable: {creds_file}')
            exit(int(ExitCode.file_error))
        Credentials.save_credentials(service, creds_file)
        inform(f'Saved credentials for service "{service}".')
        exit(int(ExitCode.success))
    services = services_list() if services == 'S' else services.lower().split(',')
    if services != 'S' and not all(s in services_list() for s in services):
        alert_fatal(f'"{services}" is/are not known services. {hint}')
        exit(int(ExitCode.bad_arg))
    display_given = display
    display = ['text'] if display == 'D' else display.lower().split(',')
    possible_displays = ['text', 'bb', 'bb-word', 'bb-words', 'bb-line',
                         'bb-lines', 'bb-para', 'bb-paragraph', 'bb-paragraphs']
    if not all(d in possible_displays for d in display):
        alert_fatal(f'Unrecognized value for {pref}d: {display_given}. {hint}')
        exit(int(ExitCode.bad_arg))
    if no_grid and not extended and not compare:
        alert_fatal(f'{pref}G without {pref}e or {pref}c produces no output. {hint}')
        exit(int(ExitCode.bad_arg))
    if any(item.startswith('-') for item in files):
        bad = next(item for item in files if item.startswith('-'))
        alert_fatal(f'Unrecognized option "{bad}" in arguments. {hint}')
        exit(int(ExitCode.bad_arg))
    if not files and from_file == 'F':
        alert_fatal(f'Need images or URLs to have something to do. {hint}')
        exit(int(ExitCode.bad_arg))
    if relaxed and not compare:
        warn(f'Option {pref}r without {pref}c has no effect. {hint}')
    if text_move != 'M' and ',' not in text_move:
        alert_fatal(f'Option {pref}m requires an argument of the form x,y. {hint}')
        exit(int(ExitCode.bad_arg))
    if text_size != 'Z' and not isint(text_size):
        alert_fatal(f'Option {pref}z requires an integer as an argument. {hint}')
        exit(int(ExitCode.bad_arg))
    if confidence != 'N':
        if not isreal(confidence):
            alert_fatal(f'Option {pref}n requires a real number as an argument. {hint}')
            exit(int(ExitCode.bad_arg))
        confidence = fast_real(confidence)
        if not (0 <= confidence <= 1.0):
            alert_fatal(f'Option {pref}n requires a real number between 0 and 1.0. {hint}')
            exit(int(ExitCode.bad_arg))

    # Do the real work --------------------------------------------------------

    if __debug__: log('='*8 + f' started {timestamp()} ' + '='*8)
    body = exception = None
    try:
        body = MainBody(files      = files,
                        from_file  = None if from_file == 'F' else from_file,
                        output_dir = None if output_dir == 'O' else output_dir,
                        add_creds  = None if add_creds == 'A' else add_creds,
                        base_name  = 'document' if base_name == 'B' else base_name,
                        confidence = 0 if confidence == 'N' else confidence,
                        text_color = 'red' if text_color == 'X' else text_color.lower(),
                        text_shift = '0,0' if text_move == 'M' else text_move,
                        text_size  = '12' if text_size == 'Z' else int(text_size),
                        display    = display,
                        make_grid  = not no_grid,
                        extended   = extended,
                        reuse_json = reuse_json,
                        services   = services,
                        threads    = max(1, cpu_count()//2 if threads == 'T' else int(threads)),
                        compare    = 'relaxed' if (compare and relaxed) else compare)
        config_interrupt(body.stop, UserCancelled(ExitCode.user_interrupt))
        body.run()
        exception = body.exception
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
            ex_class = exception[0]
            ex = exception[1]
            alert_fatal(f'An error occurred ({ex_class.__name__}): {antiformat(str(ex))}')
            # Return a better error code for some common cases.
            if ex_class in [FileNotFoundError, FileExistsError, PermissionError]:
                exit_code = ExitCode.file_error
            else:
                exit_code = ExitCode.exception
            if __debug__:
                from traceback import format_exception
                details = antiformat(''.join(format_exception(*exception)))
                log(f'Exception: {antiformat(str(ex))}\n{details}')
    else:
        inform('Done.')

    # And exit ----------------------------------------------------------------

    if __debug__: log('_'*8 + f' stopped {timestamp()} ' + '_'*8)
    if exit_code == ExitCode.user_interrupt:
        # This is a sledgehammer, but it kills everything, including ongoing
        # network get/post. I have not found a more reliable way to interrupt.
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
