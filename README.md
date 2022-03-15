# Handprint<img width="12%" align="right" src="https://raw.githubusercontent.com/caltechlibrary/handprint/develop/.graphics/noun_Hand_733265.png">

The _**Hand**written **P**age **R**ecognit**i**o**n** **T**est_ is a command-line program that invokes HTR (handwritten text recognition) services on images of document pages.  It can produce annotated images showing the results, compare the recognized text to expected text, save the HTR service results as JSON and text files, and more.

[![Latest release](https://img.shields.io/github/v/release/caltechlibrary/handprint.svg?style=flat-square&color=b44e88&label=Latest%20release)](https://github.com/caltechlibrary/handprint/releases)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg?style=flat-square)](https://choosealicense.com/licenses/bsd-3-clause)
[![Python](https://img.shields.io/badge/Python-3.8+-brightgreen.svg?style=flat-square)](http://shields.io)
[![GitHub stars](https://img.shields.io/github/stars/caltechlibrary/handprint.svg?style=flat-square&color=lightgray&label=Stars)](https://github.com/caltechlibrary/handprint/stargazers)
[![DOI](https://img.shields.io/badge/dynamic/json.svg?label=DOI&style=flat-square&colorA=gray&colorB=navy&query=$.metadata.doi&uri=https://data.caltech.edu/api/record/20059)](https://data.caltech.edu/records/20059)
[![PyPI](https://img.shields.io/pypi/v/handprint.svg?style=flat-square&color=orange&label=PyPI)](https://pypi.org/project/handprint/)


## Log of recent changes

_Version 1.5.6_: This release updates dependency versions in `requirements.txt` and `Pipfile`, to address a security issue in Pillow. It also removes the internal copy of network utilities in favor of using the `network_utils` module from [CommonPy](https://github.com/caltechlibrary/commonpy). There are no functional or API changes in this release.


## Table of Contents

* [Introduction](#introduction)
* [Installation and configuration](#installation-and-configuration)
   * [Install Handprint on your computer](#-install-handprint-on-your-computer)
   * [Add cloud service credentials](#-add-cloud-service-credentials)
* [Usage](#︎usage)
* [Getting help](#getting-help)
* [Contributing](#contributing)
* [License](#license)
* [Authors and history](#authors-and-history)
* [Acknowledgments](#︎acknowledgments)

<img align="right" width="480px" src="https://raw.githubusercontent.com/caltechlibrary/handprint/develop/.graphics/glaser-example-google.jpg">

## Introduction

Handprint (_**Hand**written **P**age **R**ecognit**i**o**n** **T**est_) is a tool for comparing alternative services for offline [handwritten text recognition (HTR)](https://en.wikipedia.org/wiki/Handwriting_recognition).  It was developed for use with documents from the [Caltech Archives](http://archives.caltech.edu), but it is completely independent and can be applied to any images of text documents.

Handprint can generate images with recognized text overlaid over them to visualize the results.  The image at right shows an example.  Among other features, the software can also display bounding boxes, threshold results by confidence values, compare full-text results to expected/ground-truth results, and output the raw results from an HTR service as JSON and text files. It can work with individual images, directories of images, and URLs pointing to images on remote servers. Finally, Handprint can use multiple processor threads for parallel execution.

Services supported include Google's [Google Cloud Vision API](https://cloud.google.com/vision/docs/ocr), Microsoft's Azure [Computer Vision API](https://azure.microsoft.com/en-us/services/cognitive-services/computer-vision/), and Amazon's [Textract](https://aws.amazon.com/textract/) and [Rekognition](https://aws.amazon.com/rekognition/).  The framework for connecting to services could be expanded to support others as well (and contributions are welcome!).


## Installation and configuration

The instructions below assume you have a Python interpreter version 3.8 or higher installed on your computer; if that's not the case, please first install Python and familiarize yourself with running Python programs on your system. If you are unsure of which version of Python you have, you can find out by running the following command in a terminal and inspecting the results:
```sh
# Note: on Windows, you may have to use "python" instead of "python3"
python3 --version
```

Note for Mac users: if you are using macOS Catalina (10.15) or later and have never run `python3`, then the first time you do, macOS will ask you if you want to install the macOS command-line developer tools.  Go ahead and do so, as this is the easiest way to get a recent-enough Python&nbsp;3 on those systems.

Handprint includes several adapters for working with cloud-based HTR services from Amazon, Google, and Microsoft, but does not include credentials for using the services.  To be able to use Handprint, you must **both** install a copy of Handprint on your computer **and** supply your copy with credentials for accessing the cloud services you want to use.  See below for more.


### ⓵&nbsp; _Install Handprint on your computer_

#### Approach 1: using the standalone Handprint executables

Beginning with version 1.5.1, runnable self-contained single-file executables are available for select operating system and Python version combinations &ndash; to use them, you **only** need a Python&nbsp;3 interpreter and a copy of Handprint, but **do not** need to run `pip install` or other steps. Please click on the relevant heading below to learn more.

<details><summary><img alt="macOS" align="bottom" height="26px" src="https://github.com/caltechlibrary/handprint/raw/main/.graphics/mac-os-32.png">&nbsp;<strong>macOS</strong></summary>

Visit the [Handprint releases page](https://github.com/caltechlibrary/handprint/releases) and look for the ZIP files with names such as (e.g.) `handprint-1.5.4-macos-python3.8.zip`. Then:
1. Download the one matching your version of Python
2. Unzip the file (if your browser did not automatically unzip it for you)
3. Open the folder thus created (it will have a name like `handprint-1.5.4-macos-python3.8`)
4. Look inside for `handprint` and move it to a location where you put other command-line programs (e.g., `/usr/local/bin`)

</details><details><summary><img alt="Linux" align="bottom" height="26px" src="https://github.com/caltechlibrary/handprint/raw/main/.graphics/linux-32.png">&nbsp;<strong>Linux</strong></summary>

Visit the [Handprint releases page](https://github.com/caltechlibrary/handprint/releases) and look for the ZIP files with names such as (e.g.) `handprint-1.5.4-linux-python3.8.zip`. Then:
1. Download the one matching your version of Python
2. Unzip the file (if your browser did not automatically unzip it for you)
3. Open the folder thus created (it will have a name like `handprint-1.5.4-linux-python3.8`)
4. Look inside for `handprint` and move it to a location where you put other command-line programs (e.g., `/usr/local/bin`)

</details><details><summary><img alt="Windows" align="bottom" height="26px" src="https://github.com/caltechlibrary/handprint/raw/main/.graphics/os-windows-32.png">&nbsp;<strong>Windows</strong></summary>

Standalone executables for Windows are not available at this time. If you are running Windows, please use one of the other methods described below.

</details>


#### Approach 2: using `pipx`

You can use [pipx](https://pypa.github.io/pipx/) to install Handprint. Pipx will install it into a separate Python environment that isolates the dependencies needed by Handprint from other Python programs on your system, and yet the resulting `handprint` command wil be executable from any shell &ndash; like any normal application on your computer. If you do not already have `pipx` on your system, it can be installed in a variety of easy ways and it is best to consult [Pipx's installation guide](https://pypa.github.io/pipx/installation/) for instructions. Once you have pipx on your system, you can install Handprint with the following command:
```sh
pipx install handprint
```

Pipx can also let you run Handprint directly using `pipx run handprint`, although in that case, you must always prefix every Handprint command with `pipx run`.  Consult the [documentation for `pipx run`](https://github.com/pypa/pipx#walkthrough-running-an-application-in-a-temporary-virtual-environment) for more information.


#### Approach 3: using `pip`

If you prefer, you can install Handprint with [pip](https://pip.pypa.io/en/stable/installing/).  If you don't have `pip` package or are uncertain if you do, please consult the [pip installation instructions](https://pip.pypa.io/en/stable/installation/). Then, to install or upgrade Handprint from the Python package repository, run the following command:
```sh
python3 -m pip install handprint --upgrade
```


### ⓶&nbsp; _Add cloud service credentials_

A one-time configuration step is needed for each cloud-based HTR service after you install Handprint on a computer.  This step supplies Handprint with credentials to access the services.  In each case, the same command format is used:
```sh
handprint -a SERVICENAME CREDENTIALSFILE.json
```

_SERVICENAME_ must be one of the service names printed by running `handprint -l`, and `CREDENTIALSFILE.json` must have one of the formats discussed below.  When you run this command, Handprint copies `CREDENTIALSFILE.json` to a private location, and thereafter uses the credentials to access _SERVICENAME_.  (The private location is different on different systems; for example, on macOS it is `~/Library/Application Support/Handprint/`.)  Examples are given below.


#### Microsoft

Microsoft's approach to credentials in Azure involves the use of [subscription keys](https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/vision-api-how-to-topics/howtosubscribe).  The format of the credentials file for Handprint needs to contain two fields:

```json
{
 "subscription_key": "YOURKEYHERE",
 "endpoint": "https://ENDPOINT"
}
```

The value `"YOURKEYHERE"` will be a string such as `"18de248475134eb49ae4a4e94b93461c"`, and it will be associated with an endpoint URI such as `"https://westus.api.cognitive.microsoft.com"`.  To obtain a key and the corresponding endpoint URI, visit [https://portal.azure.com](https://portal.azure.com) and sign in using your account login.  (Note: you will need to turn off browser security plugins such as Ad&nbsp;Block and uMatrix if you have them, or else the site will not work.)  Once you are authenticated to the Azure portal, you can create credentials for using Azure's machine-learning services.  Some notes all about this can be found in the [Handprint project Wiki pages on GitHub](https://github.com/caltechlibrary/handprint/wiki/Getting-Microsoft-Azure-credentials).

Once you have obtained both a key and an endpoint URI, use a text editor to create a JSON file in the simple format shown above, save that file somewhere on your computer (for the sake of this example, assume it is `myazurecredentials.json`), and use the command discussed above to make Handprint copy the credentials file:
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


##  Usage

Please see the [documentation site](https://caltechlibrary.github.io/handprint) for detailed documentation for Handprint.


## Getting help

If you find an issue, please submit it in [the GitHub issue tracker](https://github.com/caltechlibrary/handprint/issues) for this repository.


## Contributing

I would be happy to receive your help and participation with enhancing Handprint!  Please visit the [guidelines for contributing](CONTRIBUTING.md) for some tips on getting started.

If you plan on doing any development on Handprint, you may want to install the package dependencies listed in [`requirements-dev.txt`](requirements-dev.txt), e.g., using a command such as the following. This will install dependencies necessary to run `pytest`.
```
python3 -m pip install -r requirements-dev.txt
```


## License

Software produced by the Caltech Library is Copyright © 2021&ndash;2022 California Institute of Technology.  This software is freely distributed under a BSD/MIT type license.  Please see the [LICENSE](LICENSE) file for more information.


## Authors and history

[Mike Hucka](https://github.com/mhucka) designed and implemented Handprint beginning in mid-2018.


## Acknowledgments

The [vector artwork](https://thenounproject.com/search/?q=hand&i=733265) of a hand used as a logo for Handprint was created by [Kevin](https://thenounproject.com/kevn/) for the [Noun Project](https://thenounproject.com).  It is licensed under the Creative Commons [CC-BY 3.0](https://creativecommons.org/licenses/by/3.0/) license.

Handprint benefitted from feedback from several people, notably from Tommy Keswick, Mariella Soprano, Peter Collopy and Stephen Davison.

Handprint makes use of numerous open-source packages, without which it would have been effectively impossible to develop Handprint with the resources we had.  I want to acknowledge this debt.  In alphabetical order, the packages are:

* [aenum](https://pypi.org/project/aenum/) &ndash; advanced enumerations for Python
* [appdirs](https://github.com/ActiveState/appdirs) &ndash; module for determining appropriate platform-specific directories
* [boltons](https://github.com/mahmoud/boltons/) &ndash; package of miscellaneous Python utilities
* [boto3](https://github.com/boto/boto3) &ndash; Amazon AWS SDK for Python
* [bun](https://github.com/caltechlibrary/bun) &ndash; a set of basic user interface classes and functions
* [CommonPy](https://github.com/caltechlibrary/commonpy) &ndash; a collection of commonly-useful Python functions
* [fastnumbers](https://github.com/SethMMorton/fastnumbers) &ndash; number testing and conversion functions
* [google-api-core, google-api-python-client, google-auth, google-auth-httplib2, google-cloud, google-cloud-vision, googleapis-common-protos, google_api_python_client](https://github.com/googleapis/google-cloud-python) &ndash; Google API libraries 
* [grpcio](https://grpc.io) &ndash; open-source RPC framework
* [humanize](https://github.com/jmoiron/humanize) &ndash; make numbers more easily readable by humans
* [imagesize](https://github.com/shibukawa/imagesize_py) &ndash; determine the dimensions of an image
* [ipdb](https://github.com/gotcha/ipdb) &ndash; the IPython debugger
* [matplotlib](https://matplotlib.org) &ndash; a Python 2-D plotting library
* [numpy](https://numpy.org) &ndash; package for scientific computing in Python
* [Pillow](https://github.com/python-pillow/Pillow) &ndash; a fork of the Python Imaging Library
* [plac](http://micheles.github.io/plac/) &ndash; a command line argument parser
* [psutil](https://github.com/giampaolo/psutil) &ndash; cross-platform package for process and system monitoring in Python
* [PyMuPDF](https://github.com/pymupdf/PyMuPDF) &ndash; Python bindings for the MuPDF rendering library
* [requests](http://docs.python-requests.org) &ndash; an HTTP library for Python
* [Rich](https://rich.readthedocs.io/en/latest/) &ndash; library for writing styled text to the terminal
* [setuptools](https://github.com/pypa/setuptools) &ndash; library for `setup.py`
* [Sidetrack](https://github.com/caltechlibrary/sidetrack) &ndash; simple debug logging/tracing package
* [StringDist](https://github.com/obulkin/string-dist) &ndash; library for calculating string distances
* [textdistance](https://github.com/orsinium/textdistance) &ndash; compute distances between text sequences
* [urllib3](https://github.com/urllib3/urllib3) &ndash; Python HTTP library
* [Validator Collection](https://github.com/insightindustry/validator-collection) &ndash; Python library of 60+ commonly-used validator functions
* [wheel](https://pypi.org/project/wheel/) &ndash; setuptools extension for building wheels

Finally, I am grateful for computing &amp; institutional resources made available by the California Institute of Technology.
    
<div align="center">
  <a href="https://www.caltech.edu">
    <img width="120px" src="https://raw.githubusercontent.com/caltechlibrary/handprint/master/.graphics/caltech-round.png">
  </a>
</div>
