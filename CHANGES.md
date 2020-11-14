Change log for Handprint
========================

Version 1.4.0
--------------

This release does not change the user interface or functionality, but this is more than a patch release because it changes the minimum required versions of many Python packages and uses newer Google API libraries.

* Fixed compatibility between Handprint and more recent versions of the Google API libraries.  **The previous versions of the Google API are no longer supported by Handprint**.
* Fixed a bug in the main routine causing an error when trying to print exceptions.
* Fixed a bug in catching errors in the Microsoft interface.
* Update [`requirements.txt`](requirements.txt) to remove no-longer used packages and update minimum version numbers.
* Update [`README.md`](README.md) to acknowledge the Python dependencies actually being used now.


Version 1.3.0
--------------

* Handprint now requires Python version 3.6 or later.
* Fixed issue [#19](https://github.com/caltechlibrary/handprint/issues/19), which caused Handprint to fail to produce any output images if both `-e` and `-G` were given.
* Fixed warning about Matlplotlib GUIs and threading in `images.py`.
* Fixed macOS Mojave compatibility (issue [#16](https://github.com/caltechlibrary/handprint/issues/16).
* Updated `handprint/services/microsoft.py` to work with Azure API v. 3.0.
* Updated Microsoft credentials code to allow the endpoint URI to be supplied.
* Changed and expanded the possible exit codes returned by Handprint. (Please see the docs for more info.)
* Changed Google interface to retrieve _only_ document text results instead of all possible results, for better efficiency.
* Improved handling of `^C` interrupts from the command line.
* Added signal catcher to drop Handprint into `pdb` upon receiving `SIGUSER`.
* Switched to the use of [Sidetrack](https://github.com/caltechlibrary/sidetrack) for debug logging.
* Switched to the use of [Rich](https://github.com/willmcgugan/rich) for terminal output
* Various internal code updates and refactoring.


Version 1.2.2
--------------

* Updated copyright year in various source files.


Version 1.2.1
--------------

* Fixed Microsoft output in the annotated images to be word-based, rather than line-based, to be the same as for the other services.


Version 1.2.0
--------------

* Two bugs related to running with multiple threads (the default) are hopefully fixed in this version:
  * Sometimes the annotated image generated from a given service would have the results from another service also written over it.  This was inconsistent and intermittent, and the exact cause is still unclear, but this version of Handprint implements a workaround that hopefully stops this from happening.
  * The Amazon service interface would sometimes fail with an error related to `endpoint_resolver`.  This was due to the previous code not following recommendations about using a different connection session object in each separate thread. This is now fixed.
* This version changes the way output files are named.  The new scheme always includes the string `handprint` in the file name for easier recognition and to help reduce the chances of file name collisions.  The scheme uses the naming pattern `somefile.handprint.png` for
the rescaled input image, `somefile.handprint-service.ext` for the
various service output results, and `somefile.handprint-all.png` for the
summary grid image.  (Issue #10.)
* PDF files are now accepted as input. (Issue #11.)  Note, however, that
Handprint will only extract the first image in the PDF file.
* The order in which resizing and rescaling is done has been swapped: if a file is too large, Handprint will first rescale it, and then if it is still too big (in byte size), it will resize the file.  This appears to result in images that have higher resolution than the previous approach, which did the steps in the opposite order.
* The URLs in the file of example URLs, `tests/urls/caltech-archives-urls.txt`, have become invalid. They have been replaced with other URLs that are valid (as of right now, anyway).
* A few more bugs have been fixed.


Version 1.1.0
--------------

* Improve installation instructions and avoid telling people to use `sudo`.
* Add facility to compare extracted text to a ground truth file. This is enabled using the command-line option `-c`. See the README file or help text for more details.
* Add command-line option `-r` to adjust some of the behavior of `-c`. See the README file or help text for more details.
* Change the debug option `-@` to accept an argument for where to send the debug output trace. The behavior change of `-@` is not backward compatible.
* Internally, package metadata is now stored in `setup.cfg`.  Also, there is no `handprint/__version__.py` anymore, and instead, some special code in `handprint/__init__.py` extracts package-level variables directly from the installation created by `pip`.
* Most test images have been removed from `tests/images` and put instead in a more organized fashion in a separate repository, [htr-test-cases](https://github.com/caltechlibrary/htr-test-cases/).
* Add some missing package imports.


Version 1.0.3
--------------

* Fix an internal bug getting the credentials file for Amazon services.


Version 1.0.2
--------------

* Fix [issue #9](https://github.com/caltechlibrary/handprint/issues/9): credentials files are not saved in expected location.
* Edit the `README.md` file.


Version 1.0.1
--------------

This version adds instructions for installing from PyPI and fixes a bug writing files downloaded from URLs.


Version 1.0.0
--------------

This release provides a great many changes over the previous versions of Handprint.  The behavior and implementation have all changed in various ways, and collectively this marks the first version that can fairly be called version 1.0.0.

The following are some of the notable changes in this release:

* Credentials are now stored in a separate user directory; in additional, the process for installing credentials files is different, and involves invoking Handprint with the `-a` option.
* Handprint now calls services in parallel threads, to speed up processing.  The number of threads can be set via the `-t` option.
* To display the results of text recognition, Handprint now creates a summary image showing all service's results in an _N&nbsp;x&nbsp;N_ grid, thus allowing easy inspection and comparison of results across services.  By default, this is now the _only_ output that Handprint produces unless given the `-e` option.  With `-e`, Handprint also stores the raw data from the services and the pure text output.
* Images are now always sent to HTR services in PNG format, even when a service accepts other formats.  Source images will be converted to PNG if they are not already in that format.  (This simplifies processing and code flow.)
* Intermediate results files are now deleted unless the `-e` flag is given, reducing clutter and confusion.
* Some additional command-line arguments have been changed in backwards-incompatible ways.
* The [tests/images](tests/images) subdirectory has been reorganized, some previous images have been deleted, and some new ones have been added
* Internal code such as [network.py](handprint/network.py) has been updated to versions developed for other projects such as [Microarchiver](https://github/caltechlibrary/microarchiver).
* There are new command-line options.
* More bugs have been fixed in the code.
* More error checking has been added throughout.
* Much of the internal code has been refactored and rewritten.
* The repository now uses [READMINE](https://github.com/mhucka/readmine) structure for [README](README.md) file.
* Added code of conduct and contributor guidelines to the repository.


Version 0.9.0
-------------

* **Backward-incompatible change**: command-line option `-m` is now `-s` and "methods" are now known as "services", to avoid conflicting interpretations of what a "method" is in the context of software.  Internal object classes have likewise been changed.
* Refactor some internal network code.
* Add a number of additional images for testing.


Version 0.8.2
-------------

* Fix internal bug in file download code.
* Start separate file [CHANGES](https://github.com/caltechlibrary/handprint/blob/master/CHANGES.md) for the change log.


Version 0.8.1
-------------

* Detect and handle when the Google API returns a badly-formed bounding box.
* Skip files previously generated by the annotation feature of Handprint.


Version 0.8.0
-------------

Handprint now generates annotated images by default; they display the extracted text overlaid on the input images.


Version 0.7.5
-------------

Separate chunks of text in Microsoft output using newlines, rather than spaces, to make the results more comparable to what Google produces.


Version 0.7.4
-------------

This version improves efficiency by iterating over files/URLs first and then over methods, so that files do not get repeatedly downloaded each time a different method is used.  It also works around some network compatibility problems in different environments, and finally, adds a number of fixes.
