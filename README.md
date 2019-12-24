Handprint<img width="15%" align="right" src="https://raw.githubusercontent.com/caltechlibrary/handprint/master/.graphics/noun_Hand_733265.png">
=========

The _**Hand**written **P**age **R**ecognit**i**o**n** **T**est_ program applies HTR services to images of handwritten text and produces an annotated image (and optionally more) showing the text recognized.

[![Latest release](https://img.shields.io/github/v/release/caltechlibrary/handprint.svg?style=flat-square&color=b44e88&label=Latest%20release)](https://github.com/caltechlibrary/handprint/releases)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg?style=flat-square)](https://choosealicense.com/licenses/bsd-3-clause)
[![Python](https://img.shields.io/badge/Python-3.5+-brightgreen.svg?style=flat-square)](http://shields.io)
[![GitHub stars](https://img.shields.io/github/stars/caltechlibrary/handprint.svg?style=flat-square&color=lightgray&label=Stars)](https://github.com/caltechlibrary/handprint/stargazers)
[![DOI](https://img.shields.io/badge/dynamic/json.svg?label=DOI&style=flat-square&colorA=gray&colorB=navy&query=$.metadata.doi&uri=https://data.caltech.edu/api/record/1330)](https://data.caltech.edu/records/1330)
[![PyPI](https://img.shields.io/pypi/v/handprint.svg?style=flat-square&color=orange)](https://pypi.org/project/handprint/)


❡ Log of recent changes
-----------------------

_Version 1.1.0_: New options `-c` and `-r` added, allowing comparison of extracted text to expected (ground truth) text; see [the relevant section in this README file](#comparison-to-ground-truth-text) for more information. Also, the debug option `-@` now accepts an argument for where to send the debug output trace; the behavior change of `-@` is not backward compatible.  Finally, there are internal architectural and organizational changes.

The file [CHANGES](CHANGES.md) contains a more complete change log, and includes information about previous releases.

§ Table of Contents
-----------------

* [Introduction](#-introduction)
* [Installation](#-installation)
   * [Install Handprint on your computer](#-install-handprint-on-your-computer)
   * [Add cloud service credentials](#-add-cloud-service-credentials)
* [Usage](#︎-usage)
   * [Supported HTR/OCR services](#supported-htrocr-services)
   * [Input files and URLs](#input-files-and-urls)
   * [Annotated output images](#annotated-output-images)
   * [Extended results](#extended-results)
   * [Comparison to ground truth text](#comparison-to-ground-truth-text)
   * [Other options](#other-options)
   * [Command line options summary](#command-line-options-summary)
* [Known issues and limitations](#known-issues-and-limitations)
* [Getting help](#-getting-help)
* [Contributing](#-contributing)
* [License](#-license)
* [Authors and history](#-authors-and-history)
* [Acknowledgments](#︎-acknowledgments)

☞ Introduction
-------------

<img align="right" width="550px" src="https://raw.githubusercontent.com/caltechlibrary/handprint/master/.graphics/glaser-example-google.jpg">

Handprint (_**Hand**written **P**age **R**ecognit**i**o**n** **T**est_) is a small project to examine the performance of alternative services for [handwritten text recognition (HTR)](https://en.wikipedia.org/wiki/Handwriting_recognition).  It was developed for use with documents from the [Caltech Archives](http://archives.caltech.edu), but it is completely independent and can be applied to any images of text documents.  Services supported include Google's [Google Cloud Vision API](https://cloud.google.com/vision/docs/ocr), Microsoft's Azure [Computer Vision API](https://azure.microsoft.com/en-us/services/cognitive-services/computer-vision/), Amazon's [Textract](https://aws.amazon.com/textract/) and [Rekognition](https://aws.amazon.com/rekognition/), and more.  Among other features, Handprint can generate versions of the input images with recognized text overlaid over them, to visualize the results.  The image at right shows an example.

Handprint can work with individual images, directories of images, and URLs pointing to images on remote servers.  In addition to producing annotated images as output, it can output the raw results from an HTR service as JSON and text files.  Handprint can use multiple processor threads for parallel execution.

✎ Installation and configuration
-------------------------------

The instructions below assume you have a Python interpreter installed on your computer; if that's not the case, please first install Python and familiarize yourself with running Python programs on your system.

Handprint includes several adapters for working with cloud-based HTR services from Amazon, Google, and Microsoft.  Installing Handprint requires a both installing a copy of Handprint on your computer and supplying your copy with credentials for accessing the cloud services you want to use.


### ⓵&nbsp;&nbsp; _Install Handprint on your computer_

On **Linux**, **macOS**, and **Windows** operating systems, you should be able to install Handprint with [pip](https://pip.pypa.io/en/stable/installing/).  If you don't have the `pip` package or are uncertain if you do, first run the following command in a terminal command line interpreter: 
```
sudo python3 -m ensurepip
```

Then, to install Handprint from the Python package repository, run the following command:
```
python3 -m pip install handprint --user --upgrade
```

As an alternative to getting it from PyPI, you can instruct `pip` to install Handprint directly from the GitHub repository:
```sh
python3 -m pip install git+https@github.com:caltechlibrary/handprint.git --user --upgrade
```


### ⓶&nbsp;&nbsp; _Add cloud service credentials_

A one-time configuration step is needed for each cloud-based HTR service after you install Handprint on a computer.  This step supplies Handprint with credentials to access the services.  In each case, the same command format is used:
```sh
handprint -a SERVICENAME CREDENTIALSFILE.json
```

_SERVICENAME_ must be one of the service names printed by running `handprint -l`, and `CREDENTIALSFILE.json` must have one of the formats discussed below.  When you run this command, Handprint will copy `CREDENTIALSFILE.json` to a private location, and thereafter uses the credentials to access _SERVICENAME_.  (The private location is different on different systems; for example, on macOS it is `~/Library/Application Support/Handprint/`.)  Examples are given below.


#### Microsoft

Microsoft's approach to credentials in Azure involves the use of [subscription keys](https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/vision-api-how-to-topics/howtosubscribe).  The format of the credentials file for Handprint just needs to contain a single field:

```json
{
 "subscription_key": "YOURKEYHERE"
}
```

The value of "YOURKEYHERE" will be a string such as `"18de248475134eb49ae4a4e94b93461c"`.  To obtain a key, visit [https://portal.azure.com](https://portal.azure.com) and sign in using your account login.  (Note: you will need to turn off browser security plugins such as Ad&nbsp;Block and uMatrix if you have them, or else the site will not work.)  Once you are authenticated to the Azure portal, you can create credentials for using Azure's machine-learning services. Some notes about this can be found in the [Handprint project Wiki pages on GitHub](https://github.com/caltechlibrary/handprint/wiki/Getting-Microsoft-Azure-credentials).  Once you have obtained a key, use a text editor to create a JSON file in the simple format shown above, save that file somewhere on your computer (for the sake of this example, assume it is `myazurecredentials.json`), and use the command discussed above to make Handprint copy the credentials file:
```sh
handprint -a microsoft myazurecredentials.json
```

#### Google

Credentials for using a Google service account need to be stored in a JSON file that contains many fields.  The overall format looks like this:

```json
{
  "type": "service_account",
  "project_id": "theid",
  "private_key_id": "thekey",
  "private_key": "-----BEGIN PRIVATE KEY-----anotherkey-----END PRIVATE KEY-----\n",
  "client_email": "emailaddress",
  "client_id": "id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "someurl"
}
```

Getting one of these is summarized in the Google Cloud docs for [Creating a service account](https://cloud.google.com/docs/authentication/), but more explicit instructions can be found in the [Handprint project Wiki pages on GitHub](https://github.com/caltechlibrary/handprint/wiki/Getting-Google-Cloud-credentials).  Once you have downloaded a Google credentials file from Google, save the file somewhere on your computer (for the sake of this example, assume it is `mygooglecredentials.json`), and use the command discussed above to make Handprint copy the credentials file:
```sh
handprint -a google mygooglecredentials.json
```


#### Amazon

Amazon credentials for AWS take the form of two alphanumeric strings: a _key id_ string and a _secret access key_ string.  In addition, the service needs to be invoked with a region identifier.  For the purposes of Handprint, these should be stored in a JSON file with the following format:

```json
{
    "aws_access_key_id": "YOUR_KEY_ID_HERE",
    "aws_secret_access_key": "YOUR_ACCESS_KEY_HERE",
    "region_name": "YOUR_REGION_NAME_HERE"
}
```

Getting this information is, thankfully, a relatively simple process for Amazon's services. Instructions can be found in the [Handprint project Wiki pages on GitHub](https://github.com/caltechlibrary/handprint/wiki/Creating-credentials-for-use-with-Amazon-Rekognition).  Once you have obtained the two alphanumeric keys and a region identifier string, use a text editor to create a JSON file in the simple format shown above, save that file somewhere on your computer (for the sake of this example, assume it is `myamazoncredentials.json`), and use _two_ commands to make Handprint copy the credentials file for the two different Amazon services currently supported by Handprint:
```sh
handprint -a amazon-textract myamazoncredentials.json
handprint -a amazon-rekognition myamazoncredentials.json
```


▶︎ Usage
-------

Handprint comes with a single command-line interface program called `handprint`.  Here is a screen cast to give a sense for what it's like to run Handprint. Click on the following image:

<p align="center">
  <a href="https://raw.githubusercontent.com/caltechlibrary/handprint/master/.graphics/handprint-screencast.gif"><img src="https://raw.githubusercontent.com/caltechlibrary/handprint/master/.graphics/handprint-preview-image.png" alt="Screencast of simple Handprint demo"></a>
</p>

The `handprint` command-line program should end up installed in a location where software is normally installed on your computer, if the installation steps described in the previous section proceed successfully.  Running Handprint from a terminal shell then should be as simple as running any other shell command on your system:

```bash
handprint -h
```

If that fails for some reason, you should be able to run Handprint from anywhere using the normal approach for running Python modules:

```bash
python3 -m handprint -h
```

The `-h` option (`/h` on Windows) will make `handprint` display some help information and exit immediately.  To make Handprint do more, you can supply other arguments that instruct Handprint to process image files (or alternatively, URLs pointing to image files at a network location) and run text recognition algorithms on them, as explained below.


### _Supported HTR/OCR services_

Handprint can contact more than one cloud service for HTR.  You can use the `-l` option (`/l` on Windows) to make it display a list of the services currently implemented:

```
# handprint -l
Known services: amazon-rekognition, amazon-textract, google, microsoft
```

By default, Handprint will run every known service in turn, creating annotated images to represent the results of each individual service.  To invoke only specific services, use the `-s` option (`/s` on Windows) followed by a service name or a list of names separated by commas (e.g., `google,microsoft`).  For example, the following command will save the results of invoking only Microsoft's text recognition service on a page from [Clara Barton's unpublished draft book "The Life of My Childhood"](https://picryl.com/media/clara-barton-papers-speeches-and-writings-file-1849-1947-books-the-life-of-71), available in Handprint's source directory:
```csh
handprint -s microsoft tests/images/public-domain/clara-barton-life-of-my-childhood-p90.jpg
```

Here is what that result looks like:
<img src="https://raw.githubusercontent.com/caltechlibrary/handprint/master/.graphics/clara-barton-page.png" alt="Example of running Microsoft's service on a page from Clara Barton's unpublished draft book, The Life of My Childhood.">


### _Input files and URLs_

After credentials are installed, running Handprint _without_ the `-a` option will invoke one or more services on files, directories of files, or URLs pointing to files.  More specifically, inputs can be supplied in any of the following ways:

* One or more directory paths or one or more image file paths on the local disk, which will be interpreted as images (either individually or in directories) to be processed
* One or more URLs, which will be interpreted as network locations of image files to be processed
* If given the `-f` option (`/f` on Windows), a file containing either image paths or image URLs to be processed

Handprint considers each input path individually, and determines when an input is a URL based on whether the given path begins with letters followed by the characters `:/` followed by the rest of the path (e.g., `http://some/other/characters`).  If any of the input images are URLs, Handprint will first download the images found at the URLs to a directory indicated by the option `-o` (`/o` on Windows).  If a destination directory is not provided via `-o`, the current working directory where Handprint is running is used instead.

No matter whether files or URLs, each input should be a single image of a document page in which text should be recognized.  Handprint reads a number of common formats: JP2, JPEG, PNG, GIF, BMP, and TIFF.  However, for simplicity and maximum compatibility with all cloud services, **Handprint always converts all input files to PNG** if they are not already in that format, before sending them to a service.  Handprint also resizes images if necessary, to the smallest size accepted by any of the services invoked if an image exceeds that size.  (For example, if service A accepts files up to 10 MB in size and service B accepts files up to 5 MB, all input images will be resized to 5 MB before sending them to A and B, even if A could accept a higher-resolution image.)

Note that providing URLs on the command line can be problematic due to how terminal shells interpret certain characters, and so when supplying URLs, it's usually better to store the URLs in a file in combination with the `-f` option (`/f` on Windows).


### _Annotated output images_

By default, Handprint will create a single output file for each input file.  This file will be have the suffix `.all-results.png` and contain an annotated version of the results for each service invoked, tiled in a _N_&times;_N_ grid fashion to produce one (big) output image.  Here is a sample output image to illustrate:

<p align="center">
<img src="https://raw.githubusercontent.com/caltechlibrary/handprint/master/.graphics/all-results-example.jpg" alt="Example annotated results output image">
</p>

The 2&times;2 image above was produced by running the following command from the Handprint source directory:
```csh
handprint tests/images/public-domain/H96566k.jpg
```

The individual results, as well as individual annotated images corresponding to the results from each service, will not be retained unless the `-e` extended results option (`/e` on Windows) is invoked.  The production of the overview grid image can be skipped by using the `-G` option (`/G` on Windows).


### _Comparison to ground truth text_

Handprint supports comparing the output of HTR services to expected output (i.e., ground truth) using the option `-c` (or `/c` on Windows).  This facility requires that the user provides text files that contain the expected text for each input image.  The ground-truth text files must have the following characteristics:

* The file containing the expected results should be named `.gt.txt`, with a base name identical to the image file.  For example, an image file named `somefile.jpg` should have a corresponding text file `somefile.gt.txt`.
* The ground-truth text file should be located in the same directory as the input image file.
* The text should be line oriented, with each line representing a line of text in the image.
* The text should be plain text only.  No Unicode or binary encodings.  (This limitation comes from the HTR services, which &ndash; as of this writing &ndash; return results in plain text format.)

Handprint will write the comparison results to a tab-delimited file named after the input image and service but with the extension `.tsv`.  For example, for an input image `somefile.jpg` and results received from Google, the comparison results will be written to `somefile.google.tsv`.  The use of a tab-delimited format rather than comma-delimited format avoids the need to quote commas and other characters in the text.  The output file will have one row for each line of text in the input, plus an additional row at the end for total number of errors found.  Each row will have the following columns:

1. number of errors on that line of text (computed as [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance)),
2. the _character error rate_ (CER) for the line (see below)
3. the expected text on that line
4. the text received from the service for that line

The character error rate (CER) is computed as
<p align="center">
 100&nbsp;&times;&nbsp;(<i>i</i> + <i>s</i> + <i>d</i>)/<i>n</i>
</p>

where _i_ is the number of inserted characters, _s_ the number of substituted characters, and _d_ the number of deleted characters needed to transform the the text received into the expected text, and _n_ is the number of characters in the expected text line.  This approach to normalizing the CER value is conventional but note that it **can lead to values greater than 100%**.

By default, scoring is done by Handprint on an exact basis; character case is not changed, punctuation is not removed, and stop words are not removed.  However, multiple contiguous spaces are converted to one space, and leading spaces are removed from text lines.

If given the option `-r` (`/r` on Windows), Handprint will relax the comparison algorithm further, as follows: it will convert all text to lower case, and it will ignore certain sentence punctuation characters, namely `,`, `.`, `:`, and `;`.  The rationale for these particular choices comes from experience with actual texts and HTR services.  For example, a difference sometimes seen between HTR services is how they handle seemingly large spaces between a word and a subsequent comma or period: sometimes the HTR service will add a space before the comma or period, but inspection of the input document will reveal sloppiness in the author's handwriting and neither the addition nor the omission of a space is provably right or wrong.  To avoid biasing the results one way or another, it is better to omit the punctuation.  On the other hand, this may not always be desirable, and thus needs to be a user-controlled option.

Handprint attempts to cope with possibly-missing text in the HTR results by matching up likely corresponding lines in the expected and received results.  It does this by comparing each line of ground-truth text to each line of the HTR results using [longest common subsequence similarity](https://en.wikipedia.org/wiki/Longest_common_subsequence_problem) as implemented by the LCSSEQ function in the [textdistance](https://github.com/life4/textdistance) package.  If the lines do not pass a threshold score, Handprint looks at subsequent lines of the HTR results and tries to reestablish correspondence to ground truth.  If nothing else in the HTR results appear close enough to the expected ground-truth line, the line is assumed to be missing from the HTR results and scored appropriately.

The following is an example of a tab-separated file produced using `-c`.  This example shows a case where two lines were missing entirely from the HTR results; for those lines, the number of errors equals the length of the ground-truth text lines and the CER is 100%.

<p align="center">
<img width="60%" src="https://raw.githubusercontent.com/caltechlibrary/handprint/master/.graphics/example-tsv-file.png">
</p>


### _Extended results_

If the option `-e` (`/e` on Windows) is used, Handprint saves not only the overview image containing all the results, but also, individual annotated images for each service's results, the raw data (converted to a JSON file by Handprint), and the text extracted by the service.  These additional outputs will be written in files named after the original files with the addition of a string that indicates the service used.  For example, a file named `somefile.jpg` will produce

```
somefile.png
somefile.amazon-textract.png
somefile.amazon-textract.json
somefile.amazon-textract.txt
somefile.google.png
somefile.google.json
somefile.google.txt
...
```

A complication arises with using URLs in combination with the `-e` option: how should Handprint name the files that it writes?  Some CMS systems store content using opaque schemes that provide no clear names in the URLs, making it impossible for a software tool such as Handprint to guess what file name would make sense to use for local storage.  Worse, some systems create extremely long URLs, making it impractical to use the URL itself as the file name.  For example, the following is a real URL pointing to an image in Caltech Archives:

```
https://hale.archives.caltech.edu/adore-djatoka//resolver?rft_id=https%3A%2F%2Fhale.archives.caltech.edu%2Fislandora%2Fobject%2Fhale%253A85240%2Fdatastream%2FJP2%2Fview%3Ftoken%3D7997253eb6195d89b2615e8fa60708a97204a4cdefe527a5ab593395ac7d4327&url_ver=Z39.88-2004&svc_id=info%3Alanl-repo%2Fsvc%2FgetRegion&svc_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Ajpeg2000&svc.format=image%2Fjpeg&svc.level=4&svc.rotate=0
```

To deal with this situation, Handprint manufactures its own file names when a URL is encountered.  The scheme is simple: by default, Handprint will use a base name of `document-N`, where `N` is an integer.  The integers start from `1` for every run of Handprint, and the integers count the URLs found either on the command line or in the file indicated by the `-f` option.  The image found at a given URL is stored in a file named `document-N.E` where `E` is the format extension (e.g., `document-1.jpg`, `document-1.png`, etc.).  The URL itself is stored in another file named `document-1.url`.  Thus, the files produced by Handprint will look like this when the `-e` option is used (assuming, for this example, that the files at the source URLs are in JPEG format):

```
document-1.jpg
document-1.url
document-1.google.png
document-1.google.json
document-1.google.txt
document-1.microsoft.png
document-1.microsoft.json
document-1.microsoft.txt
...
document-2.jpg
document-2.url
document-2.google.png
document-2.google.json
document-2.google.txt
document-2.microsoft.png
document-2.microsoft.json
document-2.microsoft.txt
...
document-3.jpg
document-3.url
document-3.google.png
document-3.google.json
document-3.google.txt
document-3.microsoft.png
document-3.microsoft.json
document-3.microsoft.txt
...
```

The base name `document` can be changed using the `-b` option (`/b` on Windows).  For example, running Handprint with the option `-b einstein` will cause the outputs to be named `einstein-1.jpg`, `einstein-1.url`, etc.

Finally, if an image is too large for any of the services invoked, then Handprint will resize it prior to sending the image to any of the services (as noted above).  It will write the reduced image to a file named `FILENAME-reduced.EXT`, where `FILENAME` is the original file name and `EXT` is the file extension.  This means that if an image needs to be resized, the results of applying the text recognition services will be, e.g.,

```
document-1-reduced.png
document-1-reduced.google.png
document-1-reduced.google.json
document-1-reduced.google.txt
document-1-reduced.microsoft.png
document-1-reduced.microsoft.json
document-1-reduced.microsoft.txt
...
```

### _Other options_

Handprint produces color-coded diagnostic output as it runs, by default.  However, some terminals or terminal configurations may make it hard to read the text with colors, so Handprint offers the `-C` option (`/C` on Windows) to turn off colored output.

Handprint will send files to the different services in parallel, using a number of process threads equal to 1/2 of the number of cores on the computer it is running on.  (E.g., if your computer has 4 cores, it will by default use at most 2 threads.)  The `-t` option (`/t` on Windows) can be used to change this number.

If given the `-@` argument (`/@` on Windows), this program will output a detailed trace of what it is doing, and will also invoke [`pdb`](https://docs.python.org/library/pdb.html) upon the occurrence of any errors.  The trace will be written to the given destination, which can be a dash character (`-`) to indicate console output, or a file path.  *Important*: some Python version/platform combinations crash if `pdb` is invoked in a process thread &ndash; which is likely to happen if you are debugging the execution of Handprint. Consequently, to avoid this risk, **always use `-t 1` when debugging** to make Handprint use only one thread.

If given the `-V` option (`/V` on Windows), this program will print the version and other information, and exit without doing anything else.


### _Command line options summary_

The following table summarizes all the command line options available. (Note: on Windows computers, `/` must be used as the prefix character instead of the `-` dash character):

| Short&nbsp;&nbsp;&nbsp;&nbsp; | Long&nbsp;form | Meaning | Default |  |
|------------------------------ |----------------|---------|---------|--|
| `-a`_A_   | `--add-creds`_A_  | Add credentials for service _A_ and exit | | |
| `-b`_B_   | `--base-name`_B_  | Write outputs to files named _B_-n | Use base names of image files | ⚑ |
| `-c`      | `--compare`       | Compare to ground truth; also see `-r` | |
| `-C`      | `--no-color`      | Don't color-code the output | Use colors in the terminal output |
| `-e`      | `--extended`      | Produce extended results | Produce only results overview image | |
| `-f`_F_   | `--from-file`_F_  | Read file names or URLs from file _F_ | Use names or URLs on command line |
| `-G`      | `--no-grid`       | Don't produce results summary image | Produce an _N_&times;_N_ grid image| |
| `-h`      | `--help`          | Display help text and exit | | |
| `-l`      | `--list`          | Display known services and exit | | | 
| `-o`_O_   | `--output`_O_     | Write outputs to directory _O_ | Directories where images are found | |
| `-q`      | `--quiet`         | Don't print messages while working | Be chatty while working |
| `-r`      | `--relaxed`       | Use looser criteria for `--compare` | |
| `-s`_S_   | `--service`_S_    | Use recognition service _S_ | "all" | |
| `-t`_T_   | `--threads`_T_    | Use _T_ number of threads | Use (#cores)/2 threads | |
| `-V`      | `--version`       | Display program version info and exit | | |
| `-@`_OUT_ | `--debug`_OUT_    | Debugging mode; write trace to _OUT_ | Normal mode | ⬥ |

⚑ &nbsp; If URLs are given, then the outputs will be written by default to names of the form `document-n`, where n is an integer.  Examples: `document-1.jpg`, `document-1.google.txt`, etc.  This is because images located in network content management systems may not have any clear names in their URLs.<br>
⬥ &nbsp; To write to the console, use the character `-` as the value of _OUT_; otherwise, _OUT_ must be the name of a file where the output should be written.


⚑ Known issues and limitations
-------------------------------

Here are some known limitations in the current version of Handprint:

* The Amazon Rekognition API will return [at most 50 words in an image](https://docs.aws.amazon.com/rekognition/latest/dg/limits.html).
* Some services have different file size restrictions depending on the format of the file, but Handprint always uses the same limit for all files for a given service.  This is a code simplification.


⁇ Getting help
-------------

If you find an issue, please submit it in [the GitHub issue tracker](https://github.com/caltechlibrary/handprint/issues) for this repository.


♬ Contributing
-------------

I would be happy to receive your help and participation with enhancing Handprint!  Please visit the [guidelines for contributing](CONTRIBUTING.md) for some tips on getting started.


⧴ License
---------

Copyright (C) 2018&ndash;2019, Caltech.  This software is freely distributed under a BSD/MIT type license.  Please see the [LICENSE](LICENSE) file for more information.


☺︎ Authors and history
--------------------

[Mike Hucka](https://github.com/mhucka) designed and implemented Handprint beginning in mid-2018.


♡ Acknowledgments
-----------------------

The [vector artwork](https://thenounproject.com/search/?q=hand&i=733265) of a hand used as a logo for Handprint was created by [Kevin](https://thenounproject.com/kevn/) from the Noun Project.  It is licensed under the Creative Commons [CC-BY 3.0](https://creativecommons.org/licenses/by/3.0/) license.

Handprint benefitted from feedback from several people, notably from Tommy Keswick, Mariella Soprano, Peter Collopy and Stephen Davison.

Handprint makes use of numerous open-source packages, without which it would have been effectively impossible to develop Handprint with the resources we had.  I want to acknowledge this debt.  In alphabetical order, the packages are:

* [appdirs](https://github.com/ActiveState/appdirs) &ndash; module for determining appropriate platform-specific directories
* [boto3](https://github.com/boto/boto3) &ndash; Amazon AWS SDK for Python
* [colorama](https://github.com/tartley/colorama) &ndash; makes ANSI escape character sequences work under MS Windows terminals
* [colored](https://gitlab.com/dslackw/colored) &ndash; library for color and formatting in terminal
* [google-api-core, google-api-python-client, google-auth, google-auth-httplib2, google-cloud, google-cloud-vision, googleapis-common-protos, google_api_python_client](https://github.com/googleapis/google-cloud-python) &ndash; Google API libraries 
* [halo](https://github.com/ManrajGrover/halo) &ndash; busy-spinners for Python command-line programs
* [humanize](https://github.com/jmoiron/humanize) &ndash; make numbers more easily readable by humans
* [httplib2](https://github.com/httplib2/httplib2) &ndash; a comprehensive HTTP client library
* [imagesize](https://github.com/shibukawa/imagesize_py) &ndash; determine the dimensions of an image
* [ipdb](https://github.com/gotcha/ipdb) &ndash; the IPython debugger
* [matplotlib](https://matplotlib.org) &ndash; a Python 2-D plotting library
* [numpy](https://numpy.org) &ndash; package for scientific computing in Python
* [oauth2client](https://github.com/googleapis/oauth2client) &ndash; Google OAuth 2.0 library
* [Pillow](https://github.com/python-pillow/Pillow) &ndash; a fork of the Python Imaging Library
* [plac](http://micheles.github.io/plac/) &ndash; a command line argument parser
* [psutil](https://github.com/giampaolo/psutil) &ndash; cross-platform package for process and system monitoring in Python
* [requests](http://docs.python-requests.org) &ndash; an HTTP library for Python
* [setuptools](https://github.com/pypa/setuptools) &ndash; library for `setup.py`
* [StringDist](https://github.com/obulkin/string-dist) &ndash; library for calculating string distances
* [textdistance](https://github.com/orsinium/textdistance) &ndash; compute distances between text sequences
* [termcolor](https://pypi.org/project/termcolor/) &ndash; ANSI color formatting for output in terminal

Finally, I am grateful for computing &amp; institutional resources made available by the California Institute of Technology.
    
<div align="center">
  <a href="https://www.caltech.edu">
    <img width="120px" src="https://raw.githubusercontent.com/caltechlibrary/handprint/master/.graphics/caltech-round.png">
  </a>
</div>
