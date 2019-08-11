Handprint<img width="100px" align="right" src=".graphics/noun_Hand_733265.svg">
=========

Apply different handwritten text recognition services and algorithms to handwritten documents.

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg?style=flat-square)](https://choosealicense.com/licenses/bsd-3-clause)
[![Python](https://img.shields.io/badge/Python-3.4+-brightgreen.svg?style=flat-square)](http://shields.io)
[![Latest release](https://img.shields.io/badge/Latest_release-1.0.0-b44e88.svg?style=flat-square)](http://shields.io)

🏁 Log of recent changes
-----------------------

_Version 1.0.0_: This release features changes to behavior and internal implementation, and marks the first sufficiently complete version of Handprint that I feel can be called a proper version 1.0.  Changes include: new way to specify credential files, new default output (where the results of multiple services are placed onto a single large image for easier comparison), new command-line arguments, support for parallel thread execution, and more.

The file [CHANGES](CHANGES.md) contains a more complete change log that includes information about previous releases.


Table of Contents
-----------------

* [Introduction](#-introduction)
* [Installation](#-installation)
   * [Install Handprint on your computer](#-install-handprint-on-your-computer)
   * [Obtain cloud service credentials](#-obtain-cloud-service-credentials)
* [Usage](#︎-usage)
   * [File formats recognized](#file-formats-recognized)
   * [Data returned](#data-returned)
   * [Supported HTR/OCR services](#supported-htrocr-services)
   * [Service account credentials](#service-account-credentials)
   * [Files versus URLs](#files-versus-urls)
   * [Command line options](#command-line-options)
* [Known issues and limitations](#known-issues-and-limitations)
* [Getting help](#-getting-help)
* [Contributing](#-contributing)
* [License](#-license)
* [Authors and history](#-authors-and-history)
* [Acknowledgments](#︎-acknowledgments)


☀ Introduction
-------------

Handprint (_**Hand**written **P**age **R**ecognit**i**o**n** **T**est_) is a small project to examine the use of alternative optical character recognition (OCR) and handwritten text recognition (HTR) services on documents from the [Caltech Archives](http://archives.caltech.edu).  Tests include the use of Google's [Google Cloud Vision API](https://cloud.google.com/vision/docs/ocr), Microsoft's Azure [Computer Vision API](https://azure.microsoft.com/en-us/services/cognitive-services/computer-vision/), and others.

Among other features, Handprint can generate versions of the input images with recognized text overlaid over them, for easier visualization of the results.  The following is an example:

<p align="center">
    <img width="700px" src=".graphics/sample-annotated-image.png">
</p>


✺ Installation
-------------

Handprint is a program written in Python 3 that works by invoking cloud-based services.  Installation requires both obtaining a copy of Handprint itself, and also signing up for access to the cloud service providers.

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

### ⓶&nbsp;&nbsp; _Obtain cloud service credentials_

Credentials for different services need to be provided to Handprint in the form of JSON files.  Each service needs a separate JSON file named after the service (e.g., `microsoft.json`) and placed in a directory that Handprint searches.  By default, Handprint searches for the files in a subdirectory named `creds` where Handprint is installed, but an alternative diretory can be indicated at run-time using the `-c` command-line option (or `/c` on Windows).

The specific contents and forms of the files differ depending on the particular service, as described below.

#### Microsoft

Microsoft's approach to credentials in Azure involves the use of [subscription keys](https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/vision-api-how-to-topics/howtosubscribe).  The credentials file for Handprint just needs to contain a single field:

```json
{
 "subscription_key": "YOURKEYHERE"
}
```

The value of "YOURKEYHERE" will be a string such as `"18de248475134eb49ae4a4e94b93461c"`.  To sign up for Azure and obtain a key, visit [https://portal.azure.com](https://portal.azure.com) and sign in using your Caltech Access email address/login.  (Note: you will need to turn off browser security plugins such as Ad&nbsp;Block and uMatrix if you have them, or else the site will not work.)  It will redirect you to the regular Caltech Access login page and then (after you log in) back to the Dashboard [https://portal.azure.com](https://portal.azure.com), from where you can create credentials.  Some notes about this can be found in the [project Wiki pages](https://github.com/caltechlibrary/handprint/wiki/Getting-Microsoft-Azure-credentials).

When signing up for an Azure cloud service account, make sure to choose "Western US" as the region so that the service URL begins with "https://westus.api.cognitive.microsoft.com".

#### Google

Credentials for using a Google service account are stored in a JSON file containing many fields.  The overall form looks like this:

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

Getting one of these files is unfortunately a complicated process.  It's summarized in the Google Cloud documentation for [Creating a service account](https://cloud.google.com/docs/authentication/), but some more explicit instructions can be found in our Handprint [project Wiki pages](https://github.com/caltechlibrary/handprint/wiki/Getting-Google-Cloud-credentials).


#### Amazon

Amazon credentials for AWS take the form of two alphanumeric strings: a _key id_ string and a _secret access key_ string.  In addition, the service needs to be invoked with a region identifier.  For the purposes of Handprint, these should be stored in a JSON file with the following format:

```json
{
    "aws_access_key_id": "YOUR_KEY_ID_HERE",
    "aws_secret_access_key": "YOUR_ACCESS_KEY_HERE",
    "region_name": "YOUR_REGION_NAME_HERE"
}
```

Getting this information is a simple process for Amazon's services. Instructions can be found in our Handprint [project Wiki pages](https://github.com/caltechlibrary/handprint/wiki/Creating-credentials-for-use-with-Amazon-Rekognition).


▶︎ Usage
-------

Handprint comes with a single command-line interface program called `handprint`.  Here is a screen cast to give a sense for what it's like to run Handprint. Click on the following image:

<p align="center">
  <a href="https://asciinema.org/a/hDWutEH69LrbzcSAxfLwQWFhI"><img src=".graphics/handprint-asciinema.png" alt="Screencast of simple Handprint demo"></a>
</p>

The `handprint` command-line program should end up installed in a location where software is normally installed on your computer, if the installation steps described in the previous section proceed successfully.  Running Handprint from a terminal shell then should be as simple as running any other shell command on your system:

```bash
handprint -h
```

If that fails for some reason, you can try instead to `cd` to the directory where you installed Handprint and then run `bin/handprint` from there.  For example:

```bash
bin/handprint -h
```

Finally, as a third alternative, you should be able to run Handprint from anywhere using the normal approach for running Python modules:

```bash
python3 -m handprint -h
```

The `-h` option (`/h` on Windows) will make `handprint` display some help information and exit immediately.  To make Handprint do more, you can supply other arguments that instruct Handprint to process image files (or alternatively, URLs pointing to image files at a network location) and run text recognition algorithms on them, as explained below.


### _File formats recognized_

Whether the images are stored locally or accessed via URLs, each image should be a single page of a document in which text should be recognized.  Handprint will read a number of different formats, and if the files are not already in the most common formats accepted by the cloud services (which at this time are JPEG, PNG, GIF, and BMP), Handprint will convert them automatically to JPEG before proceeding.


### _Data returned_

Handprint tries to gather all the data that each service returns for text recognition, and outputs the results in two forms: a `.json` file containing all the results, and a `.txt` file containing just the document text.  The exact content of the `.json` file differs for each service.


### _Supported HTR/OCR services_

Handprint can contact more than one cloud service for OCR and HTR.  You can use the `-l` option (`/l` on Windows) to make Handprint display a list of the services currently implemented:

```
# handprint -l
Known services (for use as values for option -m):
   amazon-rekognition
   amazon-textract
   microsoft
   google
```

By default, Handprint will run each known service in turn.  To invoke only one specific service, use the `-m` option (`/m` on Windows) followed by a service name:

```bash
handprint -m microsoft /path/to/images
```


### _Service account credentials_

Handprint looks for credentials files in the directory where it is installed, but you can put credentials in another directory and then tell Handprint where to find it using the `-c` option (`/c` on Windows).  Example of use:

```bash
handprint -c ~/handprint-credentials /path/to/images
```


### _Files versus URLs_

Handprint can work both with files and with URLs.  By default, arguments are interpreted as being files or directories of files, but if given the `-u` option (`/u` on Windows), the arguments are interpreted instead as URLs pointing to images located on a network server.

A challenge with using URLs is how to name the files that Handprint writes for the results.  Some CMS systems store content using opaque schemes that provide no clear names in the URLs, making it impossible for a software tool such as Handprint to guess what file name would make sense to use for local storage.  Worse, some systems create extremely long URLs, making it impractical to use the full URL itself as the file name.  For example, the following is a real URL pointing to an image in Caltech Archives today:

```
https://hale.archives.caltech.edu/adore-djatoka//resolver?rft_id=https%3A%2F%2Fhale.archives.caltech.edu%2Fislandora%2Fobject%2Fhale%253A85240%2Fdatastream%2FJP2%2Fview%3Ftoken%3D7997253eb6195d89b2615e8fa60708a97204a4cdefe527a5ab593395ac7d4327&url_ver=Z39.88-2004&svc_id=info%3Alanl-repo%2Fsvc%2FgetRegion&svc_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Ajpeg2000&svc.format=image%2Fjpeg&svc.level=4&svc.rotate=0
```

To deal with this situation, Handprint manufactures its own file names when the `-u` option is used.  The scheme is simple: by default, Handprint will use a base name of `document-N`, where `N` is an integer.  The integers start from `1` for every run of Handprint, and the integers count the URLs found either on the command line or in the file indicated by the `-f` option.  The image found at a given URL is stored in a file named `document-N.E` where `E` is the format extension (e.g., `document-1.jpeg`, `document-1.png`, etc.).  The URL itself is stored in another file named `document-1.url`.  Thus, the files produced by Handprint will look like this when the `-u` option is used:

```
document-1.jpeg
document-1.url
document-1.google.txt
document-1.google.jpg
document-1.google.json
document-1.microsoft.txt
document-1.microsoft.jpg
document-1.microsoft.json

document-2.jpeg
document-2.url
document-2.google.txt
document-2.google.jpg
document-2.google.json
document-2.microsoft.txt
document-2.microsoft.jpg
document-2.microsoft.json

document-3.jpeg
document-3.url
document-3.google.txt
document-3.google.jpg
document-3.google.json
document-3.microsoft.txt
document-3.microsoft.jpg
document-3.microsoft.json

...
```

The base name `document` can be changed using the `-b` option (`/b` on Windows).  For example, running Handprint with the option `-b einstein` will cause the outputs to be named `einstein-1.jpeg`, `einstein-1.url`, etc. (assuming, for the sake of this example, that the image file format is `jpeg`).

The use of the `-u` option also **requires the use of the `-o` option** (`/o` on Windows) to tell Handprint where to store the results.  This is a consequence of the fact that, without being provided with files or directories on the local disk, Handprint can't infer where to write its output.

Example of use:

```bash
handprint -u -f /tmp/urls-to-read.txt -o /tmp/results/
```

Finally, note that providing URLs on the command line can be problematic due to how terminal shells interpret certain characters, and so when supplying URLs, it's usually better to list the URLs in a file in combination with the `-f` option (`/f` on Windows).


### _Annotated images_

By default, Handprint will create copies of the images in files named with the service extension (e.g., `document-1.microsoft.jpg`) and write overlays of the text and bounding boxes extracted by the services.  This makes it possible to see the text extracted directly over the source image.  Generating these annotated images takes a little bit of time and if they are not necessary for your purposes, you can turn off annotation with the `-A` option (`/A` on Windows).


### _Command line options_

The following table summarizes all the command line options available. (Note: on Windows computers, `/` must be usedas the prefix character instead of `-`):

| Short    | Long&nbsp;form&nbsp;opt | Meaning | Default |  |
|----------|-------------------|----------------------|---------|---|
| `-b`_B_  | `--base-name`_B_  | Write outputs to files named _B_-n | Use the base names of the image files | ✦ |
| `-c`_C_  | `--creds-dir`_C_  | Look for credentials in directory _C_ | `creds` |
| `-f`_F_  | `--from-file`_F_  | Read file names or URLs from file _F_ | Use names or URLs given on command line |
| `-l`     | `--list`          | Display list of known services | |
| `-o`_O_  | `--output`_O_     | Write outputs to directory _O_ | Same directories where images are found |  ⚑ |
| `-s`_S_  | `--service`_S_    | Use recognition service _S_ | "all" |
| `-u`     | `--given-urls`    | Inputs are URLs, not files or dirs | Assume files and/or directories of files |
| `-q`     | `--quiet`         | Don't print messages while working | Be chatty while working |
| `-A`     | `--no-annot`      | Don't produce annotated image files | Produce annotated images |
| `-C`     | `--no-color`      | Don't color-code the output | Use colors in the terminal output |
| `-D`     | `--debug`         | Debugging mode | Normal mode |
| `-V`     | `--version`       | Print program version info and exit | Do other actions instead |

 ⚑ &nbsp; The `o` option (`/o` on Windows) **must be provided** if the `-u` option (`/u` on Windows) is used: the results must be written to the local disk somewhere, because it is not possible to write the results in the network locations represented by the URLs.

✦ &nbsp; If `-u` is used (meaning, the inputs are URLs and not files or directories), then the outputs will be written by default to names of the form `document-n`, where n is an integer.  Examples: `document-1.jpeg`, `document-1.google.txt`, etc.  This is because images located in network content management systems may not have any clear names in their URLs.


⚑ Known issues and limitations
-------------------------------

Here are some known limitations in the current version of Handprint:

* The Amazon Rekognition and Textract APIs will return [at most 50 words in an image](https://docs.aws.amazon.com/rekognition/latest/dg/limits.html).
* Some services have different file size restrictions depending on the format of the file, but Handprint always uses the same limit for all files for a given service.  This is a code simplification.


⁇ Getting help
-------------

If you find an issue, please submit it in [the GitHub issue tracker](https://github.com/caltechlibrary/handprint/issues) for this repository.


♬ Contributing
-------------

I would be happy to receive your help and participation with enhancing Handprint!  Please visit the [guidelines for contributing](CONTRIBUTING.md) for some tips on getting started.


☮︎ License
---------

Copyright (C) 2019, Caltech.  This software is freely distributed under a BSD/MIT type license.  Please see the [LICENSE](LICENSE) file for more information.


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
