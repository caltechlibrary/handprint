Handprint<img width="100px" align="right" src=".graphics/noun_Hand_733265.svg">
=========

A program to apply different handwritten text recognition services and algorithms to images of handwritten text pages, and produce an annotated image (and optionally more) showing the results.

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg?style=flat-square)](https://choosealicense.com/licenses/bsd-3-clause)
[![Python](https://img.shields.io/badge/Python-3.4+-brightgreen.svg?style=flat-square)](http://shields.io)
[![Latest release](https://img.shields.io/badge/Latest_release-1.0.0-b44e88.svg?style=flat-square)](http://shields.io)

🏁 Log of recent changes
-----------------------

_Version 1.0.0_: This is a sufficiently complete version of Handprint that, perhaps, can finally be called a version 1.0.  Changes include: new way to provide credential files, new default output (in which results from different services are placed side-by-side in a single large image), new command-line arguments, parallel execution, and more.

The file [CHANGES](CHANGES.md) contains a more complete change log that includes information about previous releases.

Table of Contents
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
   * [Command line options](#command-line-options)
* [Known issues and limitations](#known-issues-and-limitations)
* [Getting help](#-getting-help)
* [Contributing](#-contributing)
* [License](#-license)
* [Authors and history](#-authors-and-history)
* [Acknowledgments](#︎-acknowledgments)

☀ Introduction
-------------

<img align="right" width="550px" src=".graphics/glaser-example-google.jpg">

Handprint (_**Hand**written **P**age **R**ecognit**i**o**n** **T**est_) is a small project to examine the performance of alternative services for [handwritten text recognition (HTR)](https://en.wikipedia.org/wiki/Handwriting_recognition).  It was developed for use with documents from the [Caltech Archives](http://archives.caltech.edu), but it is completely independent and can be applied to any images of text documents.  Services supported include Google's [Google Cloud Vision API](https://cloud.google.com/vision/docs/ocr), Microsoft's Azure [Computer Vision API](https://azure.microsoft.com/en-us/services/cognitive-services/computer-vision/), Amazon's [Textract](https://aws.amazon.com/textract/) and [Rekognition](https://aws.amazon.com/rekognition/), and more.  Among other features, Handprint can generate versions of the input images with recognized text overlaid over them, to visualize the results.  The image at right shows an example.

Handprint can work with individual images, directories of images, and URLs pointing to images on remote servers.  In addition to producing annotated images as output, it can output the raw results from an HTR service as JSON and text files.    Handprint is written in Python and can use multiple processor threads for parallel execution.

✺ Installation and configuration
-------------------------------

Handprint includes several adapters for working with cloud-based HTR services from Amazon, Google, and Microsoft.  Installing Handprint requires both installing a copy of Handprint on your computer and supplying your copy with credentials for accessing the cloud services you want to use.

### ⓵&nbsp;&nbsp; _Install Handprint on your computer_

The following is probably the simplest and most direct way to install this software on your computer:
```sh
sudo python3 -m pip install git+https://github.com/caltechlibrary/handprint.git --upgrade
```

Alternatively, you can instead clone this GitHub repository and then run `setup.py` manually.  First, create a directory somewhere on your computer where you want to store the files, and cd to it from a terminal shell.  Next, execute the following commands:
```sh
git clone https://github.com/caltechlibrary/handprint.git
cd handprint
sudo python3 -m pip install . --upgrade
```

### ⓶&nbsp;&nbsp; _Add cloud service credentials_

A one-time configuration step is needed for each cloud-based HTR service after you install Handprint on a computer.  This step supplies Handprint with credentials to access the services.  In each case, the same command format is used:
```sh
handprint -a SERVICENAME CREDENTIALSFILE.json
```

_SERVICENAME_ must be one of the service names printed by running `handprint -l`, and `CREDENTIALSFILE.json` must have one of the formats discussed below.  When you run this command, Handprint will copy `CREDENTIALSFILE.json` to a private location, and thereafter uses the credentials to access _SERVICENAME_.  (The private location is different on different sytems; for example, on macOS it is `~/Library/Application Support/Handprint/`.)  Examples are given below.


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

```
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
  <a href=".graphics/handprint-screencast.gif"><img src=".graphics/handprint-preview-image.png" alt="Screencast of simple Handprint demo"></a>
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

Handprint can contact more than one cloud service for HTR.  You can use the `-l` option (`/l` on Windows) to make Handprint display a list of the services currently implemented:

```
# handprint -l
Known services: amazon-rekognition, amazon-textract, google, microsoft
```

By default, Handprint will run every known service in turn.  To invoke only specific services, use the `-s` option (`/s` on Windows) followed by a service name or a list of names separated by commas (e.g.,
`google,microsoft`).  For example, to use only Microsoft, invoke Handprint like this:
```bash
handprint -s microsoft /path/to/images
```


### _Input files and URLs_

After credentials are installed, running Handprint _without_ the `-a` option will invoke one or more services on files, directories of files, or URLs pointing to files.  More specifically, inputs can be supplied in any of the following ways:

* One or more directory paths or one or more image file paths on the local disk, which will be interpreted as images (either individually or in directories) to be processed
* One or more URLs, which will be interpreted as network locations of image files to be processed
* If given the `-f` option (`/f` on Windows), a file containing either image paths or image URLs to be processed

Handprint considers each input path individually, and determines when an input is a URL based on whether the given path begins with letters followed by the characters `:/` followed by the rest of the path (e.g., `http://some/other/characters`).  If any of the input images are URLs, Handprint will first download the images found at the URLs to a directory indicated by the option `-o` (`/o` on Windows).  If a destination directory is not provided via `-o`, the current working directory where Handprint is running is used instead.

No matter whether files or URLs, each input should be a single image of a document page in which text should be recognized.  Handprint reads a number of common formats: JP2, JPEG, PNG, GIF, BMP, and TIFF.  However, for simplicity and maximum compatibility with all cloud services, **Handprint always converts all input files to JPEG** if they are not already in that format, before sending them to a service.  Handprint also resizes images if necessary, to the smallest size accepted by any of the services invoked if an image exceeds that size.  (For example, if service A accepts files up to 10 MB in size and service B accepts files up to 5 MB, all input images will be resized to 5 MB before sending them to A and B, even if A could accept a higher-resolution image.)

Note that providing URLs on the command line can be problematic due to how terminal shells interpret certain characters, and so when supplying URLs, it's usually better to store the URLs in a file in combination with the `-f` option (`/f` on Windows).


### _Annotated output images_

By default, Handprint will create one output file for each input file.  This file will be have the suffix `.all-results.jpg` and contain an annotated version of the input file for each service invoked, tiled in a _N_&times;_N_ grid fashion to produce one (big) output image.  Here is a sample image to illustrate:

<p align="center">
<img src=".graphics/all-results-example.jpg" alt="Example annotated results output image">
</p>

The individual results, as well as individual annotated images corresponding to the results from each service, will not be retained unless the `-e` extended results option (`/e` on Windows) is invoked.  The production of the overview grid image can be skipped by using the `-G` option (`/G` on Windows).


### Extended results

If the `-e` option `-e` (`/e` on Windows) is used, Handprint saves not only the overview image containing all the results, but also, individual annotated images for each service's results, the raw data (converted to a JSON file by Handprint), and the text extracted by the service.  These additional outputs will be written in files named after the original files with the addition of a string that indicates the service used.  For example, a file named `somefile.jpg` will produce

```
somefile.jpg
somefile.amazon-textract.jpg
somefile.amazon-textract.json
somefile.amazon-textract.txt
somefile.google.jpg
somefile.google.json
somefile.google.txt
...
```

A complication arises with using URLs in combination with the `-e` option: how should Handprint name the files that it writes?  Some CMS systems store content using opaque schemes that provide no clear names in the URLs, making it impossible for a software tool such as Handprint to guess what file name would make sense to use for local storage.  Worse, some systems create extremely long URLs, making it impractical to use the URL itself as the file name.  For example, the following is a real URL pointing to an image in Caltech Archives:

```
https://hale.archives.caltech.edu/adore-djatoka//resolver?rft_id=https%3A%2F%2Fhale.archives.caltech.edu%2Fislandora%2Fobject%2Fhale%253A85240%2Fdatastream%2FJP2%2Fview%3Ftoken%3D7997253eb6195d89b2615e8fa60708a97204a4cdefe527a5ab593395ac7d4327&url_ver=Z39.88-2004&svc_id=info%3Alanl-repo%2Fsvc%2FgetRegion&svc_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Ajpeg2000&svc.format=image%2Fjpeg&svc.level=4&svc.rotate=0
```

To deal with this situation, Handprint manufactures its own file names when a URL is encountered.  The scheme is simple: by default, Handprint will use a base name of `document-N`, where `N` is an integer.  The integers start from `1` for every run of Handprint, and the integers count the URLs found either on the command line or in the file indicated by the `-f` option.  The image found at a given URL is stored in a file named `document-N.E` where `E` is the format extension (e.g., `document-1.jpeg`, `document-1.png`, etc.).  The URL itself is stored in another file named `document-1.url`.  Thus, the files produced by Handprint will look like this when the `-e` option is used:

```
document-1.jpeg
document-1.url
document-1.google.jpg
document-1.google.json
document-1.google.txt
document-1.microsoft.jpg
document-1.microsoft.json
document-1.microsoft.txt
...
document-2.jpeg
document-2.url
document-2.google.jpg
document-2.google.json
document-2.google.txt
document-2.microsoft.jpg
document-2.microsoft.json
document-2.microsoft.txt
...
document-3.jpeg
document-3.url
document-3.google.jpg
document-3.google.json
document-3.google.txt
document-3.microsoft.jpg
document-3.microsoft.json
document-3.microsoft.txt
...
```

The base name `document` can be changed using the `-b` option (`/b` on Windows).  For example, running Handprint with the option `-b einstein` will cause the outputs to be named `einstein-1.jpeg`, `einstein-1.url`, etc.

Finally, if an image is too large for any of the services invoked, then Handprint will resize it prior to sending the image to any of the services (as noted above).  It will write the reduced image to a file named `FILENAME-reduced.EXT`, where `FILENAME` is the original file name and `EXT` is the file extension.  This means that if an image needs to be resized, the results of applying the text recognition services will be, e.g.,

```
document-1-reduced.jpg
document-1-reduced.google.jpg
document-1-reduced.google.json
document-1-reduced.google.txt
document-1-reduced.microsoft.jpg
document-1-reduced.microsoft.json
document-1-reduced.microsoft.txt
...
```

### _Command line options_

The following table summarizes all the command line options available. (Note: on Windows computers, `/` must be used as the prefix character instead of the `-` dash character):

| Short    | Long&nbsp;form&nbsp;opt&nbsp;&nbsp;&nbsp; | Meaning | Default |  |
|----------|-------------------|----------------------|---------|---|
| `-a`_A_  | `--add-creds`_A_  | Add credentials for service _A_ and exit | | |
| `-b`_B_  | `--base-name`_B_  | Write outputs to files named _B_-n | Use the base names of the image files | ⚑ |
| `-C`     | `--no-color`      | Don't color-code the output | Use colors in the terminal output |
| `-e`     | `--extended`      | Produce extended results | Produce only results overview image | |
| `-f`_F_  | `--from-file`_F_  | Read file names or URLs from file _F_ | Use names or URLs on command line |
| `-G`     | `--no-grid`       | Do not produce results overview image | Produce an _N_&times;_N_ grid image| |
| `-h`     | `--help`          | Display help text and exit | | |
| `-l`     | `--list`          | Display list of known services and exit | | | 
| `-o`_O_  | `--output`_O_     | Write outputs to directory _O_ | Directories where images are found | |
| `-q`     | `--quiet`         | Don't print messages while working | Be chatty while working |
| `-s`_S_  | `--service`_S_    | Use recognition service _S_ | "all" | |
| `-t`_T_  | `--threads`_T_    | Use _T_ number of threads | Use #cores/2 threads | |
| `-V`     | `--version`       | Display program version info and exit | | |
| `-@`     | `--debug`         | Debugging mode | Normal mode | |

⚑ &nbsp; If URLs are given, then the outputs will be written by default to names of the form `document-n`, where n is an integer.  Examples: `document-1.jpeg`, `document-1.google.txt`, etc.  This is because images located in network content management systems may not have any clear names in their URLs.


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


☮︎ License
---------

Copyright (C) 2018&ndash;2019, Caltech.  This software is freely distributed under a BSD/MIT type license.  Please see the [LICENSE](LICENSE) file for more information.


❡ Authors and history
--------------------

[Mike Hucka](https://github.com/mhucka) designed and implemented Handprint beginning in mid-2018.


☺︎ Acknowledgments
-----------------------

The [vector artwork](https://thenounproject.com/search/?q=hand&i=733265) of a hand used as a logo for Handprint was created by [Kevin](https://thenounproject.com/kevn/) from the Noun Project.  It is licensed under the Creative Commons [CC-BY 3.0](https://creativecommons.org/licenses/by/3.0/) license.

Handprint benefitted from feedback from several people, notably from Tommy Keswick, Mariella Soprano, Peter Collopy and Stephen Davison.

Handprint makes use of numerous open-source packages, without which it would have been effectively impossible to develop Turf with the resources we had.  I want to acknowledge this debt.  In alphabetical order, the packages are:

* [boto3](https://github.com/boto/boto3) &ndash; Amazon AWS SDK for Python
* [colorama](https://github.com/tartley/colorama) &ndash; makes ANSI escape character sequences work under MS Windows terminals
* [google-api-core, google-api-python-client, google-auth, google-auth-httplib2, google-cloud, google-cloud-vision, googleapis-common-protos, google_api_python_client](https://github.com/googleapis/google-cloud-python) &ndash; Google API libraries 
* [halo](https://github.com/ManrajGrover/halo) &ndash; busy-spinners for Python command-line programs
* [httplib2](https://github.com/httplib2/httplib2) &ndash; a comprehensive HTTP client library
* [imagesize](https://github.com/shibukawa/imagesize_py) &ndash; determine the dimensions of an image
* [ipdb](https://github.com/gotcha/ipdb) &ndash; the IPython debugger
* [matplotlib](https://matplotlib.org) &ndash; a Python 2-D plotting library
* [oauth2client](https://github.com/googleapis/oauth2client) &ndash; Google OAuth 2.0 library
* [Pillow](https://github.com/python-pillow/Pillow) &ndash; a fork of the Python Imaging Library
* [plac](http://micheles.github.io/plac/) &ndash; a command line argument parser
* [requests](http://docs.python-requests.org) &ndash; an HTTP library for Python
* [setuptools](https://github.com/pypa/setuptools) &ndash; library for `setup.py`
* [termcolor](https://pypi.org/project/termcolor/) &ndash; ANSI color formatting for output in terminal

Finally, I am grateful for computing &amp; institutional resources made available by the California Institute of Technology.
    
<div align="center">
  <a href="https://www.caltech.edu">
    <img width="100" height="100" src=".graphics/caltech-round.svg">
  </a>
</div>
