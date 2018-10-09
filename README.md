Handprint<img width="100px" align="right" src=".graphics/noun_Hand_733265.svg">
=========

An experiment with handwritten text optical recognition on Caltech Archives materials.

*Authors*:      [Michael Hucka](http://github.com/mhucka)<br>
*Repository*:   [https://github.com/caltechlibrary/handprint](https://github.com/caltechlibrary/handprint)<br>
*License*:      BSD/MIT derivative &ndash; see the [LICENSE](LICENSE) file for more information

☀ Introduction
-----------------------------

Handprint (_**Hand**written **P**age **R**ecognit**i**o**n** **T**est_) is a small project to examine the use of alternative optical character recognition (OCR) and handwritten text recognition (HTR) methods on documents from the [Caltech Archives](http://archives.caltech.edu).  Tests include the use of Google's OCR/HTR capabilities in their [Google Cloud Vision API](https://cloud.google.com/vision/docs/ocr) and [Tesseract](https://en.wikipedia.org/wiki/Tesseract_(software)).

✺ Installation instructions
---------------------------

Handprint is a program written in Python 3 that works by invoking cloud-based services.  Installation requires both obtaining a copy of Handprint itself, and also signing up for access to the cloud service providers.

### ⓵&nbsp;&nbsp; _Install Handprint on your computer_

The following is probably the simplest and most direct way to install this software on your computer:
```sh
sudo pip3 install git+https://github.com/caltechlibrary/handprint.git
```

Alternatively, you can instead clone this GitHub repository and then run `setup.py` manually.  First, create a directory somewhere on your computer where you want to store the files, and cd to it from a terminal shell.  Next, execute the following commands:
```sh
git clone https://github.com/caltechlibrary/handprint.git
cd handprint
sudo python3 -m pip install .
```

### ⓶&nbsp;&nbsp; _Obtain cloud service credentials_

Credentials for different services need to be provided to Handprint in the form of JSON files.  Each service needs a separate JSON file named after the service (e.g., `microsoft.json`) and placed in a directory that Handprint searches.  By default, Handprint searches for the files in a subdirectory named `creds` where Handprint is installed, but an alternative diretory can be indicated at run-time using the `-c` command-line option.

The specific contents and forms of the files differ depending on the particular service, as described below.

### _Microsoft_

Microsoft's approach to credentials in Azure involves the use of [subscription keys](https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/vision-api-how-to-topics/howtosubscribe).  The credentials file for Handprint just needs to contain a single field:

```json
{
 "subscription_key": "YOURKEYHERE"
}
```

The value of "YOURKEYHERE" will be a string such as `"18de248475134eb49ae4a4e94b93461c"`.  To sign up for Azure and obtain a key, visit [https://portal.azure.com](https://portal.azure.com) and sign in using your Caltech Access email address/login.  (Note: you will need to turn off browser security plugins such as Ad&nbsp;Block and uMatrix if you have them, or else the site will not work.)  It will redirect you to the regular Caltech Access login page and then (after you log in) back to the Dashboard [https://portal.azure.com](https://portal.azure.com), from where you can create credentials.  Some notes about this can be found in the [project Wiki pages](https://github.com/caltechlibrary/handprint/wiki/Getting-Microsoft-Azure-credentials).

When signing up for an Azure cloud service account, make sure to choose "Western US" as the region so that the service URL begins with "https://westus.api.cognitive.microsoft.com".

### _Google_

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

Some notes about creating these credentials can be found in the [project Wiki pages](https://github.com/caltechlibrary/handprint/wiki/Getting-Google-Cloud-credentials).


▶︎ Running Handprint
------------------

Handprint is a command-line driven program.  There is a single command-line interface program called `handprint`.  You can run it by starting a terminal shell and `cd`'ing to the directory where you installed Handprint, and then running the program `bin/handprint` from there.  For example:

```bash
bin/handprint -h
```

Alternatively, you should be able to run Handprint from anywhere using the normal approach to running Python modules:

```bash
python3 -m handprint -h
```

The `-h` option will make `handprint` display some help information and exit immediately.  To make Handprint do something more useful, you can supply arguments that are a set of file names, or one or more directories containing images.  Each image should be a single page of a document in which handwritten text should be recognized.  The images must the least common denominator among the formats accepted by the cloud services, which at this time, is JPEG, PNG, GIF, and BMP.

<!--
* Google: [JPEG, PNG8, PNG24, GIF, Animated GIF (first frame only), BMP, WEBP, RAW, ICO, PDF, TIFF](https://cloud.google.com/vision/docs/supported-files)
* Microsoft: [JPEG, PNG, GIF, or BMP format](https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/home)
-->

Handprint can contact more than one cloud service for OCR and HTR.  You can use the `-l` option to make Handprint display a list of the methods currently implemented:

```
# bin/handprint -l
Known methods (for use as values for option -m):
   microsoft
   google
```

To invoke a particular method, use the `-m` option followed by a method name:

```bash
bin/handprint -m microsoft /path/to/images
```


⁇ Getting help and support
--------------------------

If you find an issue, please submit it in [the GitHub issue tracker](https://github.com/caltechlibrary/handprint/issues) for this repository.


☺︎ Acknowledgments
-----------------------

The [vector artwork](https://thenounproject.com/search/?q=hand&i=733265) of a hand used as a logo for Handprint was created by [Kevin](https://thenounproject.com/kevn/) from the Noun Project.  It is licensed under the Creative Commons [CC-BY 3.0](https://creativecommons.org/licenses/by/3.0/) license.


☮︎ Copyright and license
---------------------

Copyright (C) 2018, Caltech.  This software is freely distributed under a BSD/MIT type license.  Please see the [LICENSE](LICENSE) file for more information.
    
<div align="center">
  <a href="https://www.caltech.edu">
    <img width="100" height="100" src=".graphics/caltech-round.svg">
  </a>
</div>
