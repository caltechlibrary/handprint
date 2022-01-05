# Handprint<img width="12%" align="right" src="https://raw.githubusercontent.com/caltechlibrary/handprint/develop/.graphics/noun_Hand_733265.png">

The _**Hand**written **P**age **R**ecognit**i**o**n** **T**est_ is a command-line program that invokes HTR (handwritten text recognition) services on images of document pages.  It can produce annotated images showing the results, compare the recognized text to expected text, save the HTR service results as JSON and text files, and more.

[![Latest release](https://img.shields.io/github/v/release/caltechlibrary/handprint.svg?style=flat-square&color=b44e88&label=Latest%20release)](https://github.com/caltechlibrary/handprint/releases)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg?style=flat-square)](https://choosealicense.com/licenses/bsd-3-clause)
[![Python](https://img.shields.io/badge/Python-3.8+-brightgreen.svg?style=flat-square)](http://shields.io)
[![GitHub stars](https://img.shields.io/github/stars/caltechlibrary/handprint.svg?style=flat-square&color=lightgray&label=Stars)](https://github.com/caltechlibrary/handprint/stargazers)
[![DOI](https://img.shields.io/badge/dynamic/json.svg?label=DOI&style=flat-square&colorA=gray&colorB=navy&query=$.metadata.doi&uri=https://data.caltech.edu/api/record/8960)](https://data.caltech.edu/records/8960)
[![PyPI](https://img.shields.io/pypi/v/handprint.svg?style=flat-square&color=orange&label=PyPI)](https://pypi.org/project/handprint/)


## Log of recent changes

_Version 1.5.5_: This release updates dependency versions in `requirements.txt` and `Pipfile`, to address a security issue in Pillow, update CommonPy, and some other version updates. It also fixes an internal bug in the image resizing code.


## Table of Contents

* [Introduction](#introduction)
* [Installation and configuration](#installation-and-configuration)
   * [Install Handprint on your computer](#-install-handprint-on-your-computer)
   * [Add cloud service credentials](#-add-cloud-service-credentials)
* [Usage](#︎-usage)
   * [Supported HTR/OCR services](#supported-htrocr-services)
   * [Input files and URLs](#input-files-and-urls)
   * [Selecting destination services](#selecting-destination-services)
   * [Visual display of recognition results](#visual-display-of-recognition-results)
   * [Annotation types](#annotation-types)
   * [Thresholding by confidence](#thresholding-by-confidence)
   * [Comparison to ground truth text](#comparison-to-ground-truth-text)
   * [Extended results](#extended-results)
   * [Other options](#other-options)
   * [Command line options summary](#command-line-options-summary)
   * [Return values](#return-values)
* [Known issues and limitations](#known-issues-and-limitations)
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

Handprint comes with a single command-line interface program called `handprint`.  Here is a screen cast to give a sense for what it's like to run Handprint. Click on the following image:

<p align="center">
  <a href="https://raw.githubusercontent.com/caltechlibrary/handprint/develop/.graphics/handprint-demo.gif"><img src="https://raw.githubusercontent.com/caltechlibrary/handprint/develop/.graphics/handprint-preview-image.png" alt="Screencast of simple Handprint demo"></a>
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


### _Input files and URLs_

After credentials are installed, running Handprint _without_ the `-a` option will invoke one or more services on files, directories of files, or URLs pointing to files. Here is an example of running Handprint on a directory containing images:
```sh
handprint tests/data/caltech-archives/glaser/
```

Image paths or URLs can be supplied to Handprint in any of the following ways:
* One or more directory paths or one or more image file paths on the local disk, which will be interpreted as images (either individually or in directories) to be processed
* One or more URLs, which will be interpreted as network locations of image files to be processed
* If given the `-f` option (`/f` on Windows), a file containing either image paths or image URLs to be processed

Handprint assumes a path is a URL if it meets the test of [`is_url(...)`](https://validator-collection.readthedocs.io/en/latest/checkers.html?highlight=is_url#validator_collection.checkers.is_url) from the Python Validator Collection.  For every input given as a URL, Handprint will first download the image found at the URL to a directory indicated by the option `-o` (`/o` on Windows), or the current directory if option `-o` is not used.

No matter whether files or URLs, each input item should be a single image of a document page in which text should be recognized.  Handprint reads a number of common formats: JP2, JPEG, PDF, PNG, GIF, BMP, and TIFF.  However, for simplicity and maximum compatibility with all cloud services, Handprint always **converts all input files to PNG** if they are not already in that format, no matter if a given service can accept other formats.  Handprint also **reduces the size of input images to the smallest size accepted by any of the services invoked** if an image exceeds that size.  (For example, when sending a file to services A and B at the same time, if service A accepts files up to 10 MB in size and service B accepts files up to 4 MB, Handprint will resize the file to 4 MB before sending it to _both_ A and B, even if A could accept a higher-resolution image.)  Finally, if the input contains more than one page (e.g., in a PDF file), **Handprint will only use the first page of the input** and ignore the remaining pages.

Be aware that **downsizing images can change the text recognition results returned by some services** compared to the results obtained using the original full-size input image.  If your images are larger when converted to PNG than the smallest size accepted by one of the destination services (currently 4 MB, for Microsoft), then you may wish to compare the results of using multiple services at once versus one at a time (i.e., one destination at a time in separate invocations of Handprint).

Finally, note that providing URLs on the command line can be problematic due to how terminal shells interpret certain characters, and so when supplying URLs, it's usually better to store the URLs in a file in combination with the `-f` option (`/f` on Windows).


### _Selecting destination services_

You can use the `-l` option (`/l` on Windows) to make it display a list of the services currently supported by Handprint:

```sh
# handprint -l
Known services: amazon-rekognition, amazon-textract, google, microsoft
```

By default, Handprint will send images to all of the known services, creating annotated images to represent the results of each individual service.  To invoke only specific services, use the `-s` option (`/s` on Windows) followed by a service name or a list of names separated by commas (e.g., `google,microsoft`).  For example, the following command will invoke Microsoft's text recognition service on a page from [Clara Barton's unpublished draft book "The Life of My Childhood"](https://picryl.com/media/clara-barton-papers-speeches-and-writings-file-1849-1947-books-the-life-of-71), available in Handprint's source directory:
```sh
handprint -s microsoft tests/data/public-domain/images/clara-barton-life-of-my-childhood-p90.jpg
```

Here is the result of that command:
<p align="center">
<img width="90%" src="https://raw.githubusercontent.com/caltechlibrary/handprint/develop/.graphics/clara-barton-page.jpg" alt="Example of running Microsoft's service on a page from Clara Barton's unpublished draft book, The Life of My Childhood.">
</p>

### _Visual display of recognition results_

After gathering the results of each service for a given input, Handprint will create a single compound image consisting of the results for each service arranged in a _N_&times;_N_ grid.  This overview image is intended to make it easier to compare the results of multiple services against each other.  The grid image will have the suffix `.handprint-all.png`.  Here is a sample output image to illustrate:

<p align="center">
<img width="90%" src="https://raw.githubusercontent.com/caltechlibrary/handprint/develop/.graphics/all-results-example.png" alt="Example annotated results output image">
</p>

The 2&times;2 image above was produced by running the following command from the Handprint `tests/data/caltech-archives/glaser` directory:
```csh
handprint --text-size 20  "DAG_5_1_6 1952-1957 Notebook VI p2.jpg"
```

To move the position of the text annotations overlaid over the input image, you can use the option `-m` (or `/m` on Windows).  This takes two numbers separated by a comma in the form `x,y`.  Positive numbers move the text rightward and upward, respectively, relative to the default position.  The default position of each text annotation in the annotated output is such that the _left edge of the word_ starts at the location of the _upper left corner of the bounding box_ returned by the service; this has the effect of putting the annotation near, but above, the location of the (actual) word in the input image by default.  For example, if the word in the image is _strawberry_, the bounding box returned by the service will enclose _strawberry_, and the upper left corner of that bounding box will be somewhere above the letter _s_. Then, the default position of the text annotation will put the left edge of the word "strawberry" at that point above the letter _s_. Using the move-text option allows you to move the annotation if desired. A value such as `0,-5` will move it downward five pixels.

To change the color of the text annotations overlaid over the input image, you can use the option `-x` (or `/x` on Windows).  You can use hex color codes such as `"#ff0000"` (make sure to enclose the value with quotes, or the shell will interpret the pound sign as a comment character), or X11/CSS4 color names with no spaces such as `purple` or `darkgreen`.

To change the size of the text annotations overlaid over the input image, you can use the option `-z` (or `/z` on Windows).  The value is in units of points.  The default size is 12.

Finally, the individual results, as well as individual annotated images corresponding to the results from each service, will not be retained unless the `-e` extended results option (`/e` on Windows) is invoked (described in more detail below).  The production of the overview grid image can be skipped by using the `-G` option (`/G` on Windows).


### _Annotation types_

Handprint produces copies of the input images overlaid with the recognition results received from the different services.  By default, it shows only the recognized text.  The option `-d` (`/d` on Windows) can be used to tell Handprint to display other results.  The recognized values are as follows:

* `text`: display the text recognized in the image (default)
* `bb`: display all bounding boxes returned by the service
* `bb-word`: display the bounding boxes for words (in red)
* `bb-line`: display the bounding boxes for lines (in blue)
* `bb-para`: display the bounding boxes for paragraphs (in green)

Separate multiple values with a comma.  The option `bb` is a shorthand for the value `bb-word,bb-line,bb-para`.  As an example, the following command will show both the recognized text and the bounding boxes around words:
```sh
handprint -d text,bb-word  -s google  tests/data/public-domain/images/H96566k.jpg
```

And here is the output from that command:

<p align="center">
<img width="90%" src="https://raw.githubusercontent.com/caltechlibrary/handprint/develop/.graphics/google-bounding-box-example.png" alt="Example of bounding boxes">
</p>

Note that as of June 2021, the main services (Amazon, Google, Microsoft) do not all provide the same bounding box information in their results.  The following table summarizes what is available:

| Service   | Word<br>bounding boxes | Line<br>bounding boxes | Paragraph<br>bounding boxes |
|-----------|:----:|:----:|:---------:|
| Amazon    |  Y   |  Y   |     -     |
| Google    |  Y   |  -   |     Y     |
| Microsoft |  Y   |  Y   |     -     |

If a service does not provide a particular kind of bounding box, Handprint will not display that kind of 
bounding box in the annotated output for that service.


### _Thresholding by confidence_

All of the services return confidence scores for items recognized in the input.  By default, Handprint will show all results no matter how low the confidence score.  The option `-n` (`/n` on Windows) can be used to threshold the results based on the confidence value for each item (text or bounding boxes).  The value provided as the argument to the option must be a floating point number between 0 and 1.0.  For example, the following command will make Handprint only show text that is rated with least 99.5% confidence:
```sh
handprint -n 0.995  somefile.png
```

Note that the **confidence values returned by the different services are not normalized against each other**.  What one service considers to be 80% confidence may not be what another service considers 80% confidence.  Handprint performs the thresholding against the raw scores returned by each service individually.


### _Comparison to ground truth text_

Handprint offers the ability to compare the output of HTR services to expected output (i.e., ground truth) using the option `-c` (or `/c` on Windows).  This facility requires that the user provides text files that contain the expected text for each input image.  The ground-truth text files must have the following characteristics:

* The file containing the expected results should be named `.gt.txt`, with a base name identical to the image file.  For example, an image file named `somefile.jpg` should have a corresponding text file `somefile.gt.txt`.  (This is a convention used by some other tools such as [ocropy](https://github.com/tmbdev/ocropy/wiki/Working-with-Ground-Truth).)
* The ground-truth text file should be located in the same directory as the input image file.
* The text should be line oriented, with each line representing a line of text in the image.
* The text should be plain text only.  No Unicode or binary encodings.  (This limitation comes from the HTR services, which &ndash; as of this writing &ndash; return results in plain text format.)

Handprint will write the comparison results to a tab-delimited file named after the input image and service but with the extension `.tsv`.  For example, for an input image `somefile.jpg` and results received from Google, the comparison results will be written to `somefile.handprint-google.tsv`.  The use of a tab-delimited format rather than comma-delimited format avoids the need to quote commas and other characters in the text.  The output file will have one row for each line of text in the input, plus an additional row at the end for total number of errors found.  Each row will have the following columns:

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
<img width="60%" src="https://raw.githubusercontent.com/caltechlibrary/handprint/develop/.graphics/example-tsv-file.png">
</p>


### _Extended results_

If the option `-e` (`/e` on Windows) is used, Handprint saves not only the overview image containing all the results, but also, individual annotated images for each service's results, the raw data (converted to a JSON file by Handprint), and the text extracted by the service.  These additional outputs will be written in files named after the original files with the addition of a string that indicates the service used.  For example, a file named `somefile.jpg` will produce

```
somefile.handprint-amazon-textract.png
somefile.handprint-amazon-textract.json
somefile.handprint-amazon-textract.txt
somefile.handprint-google.png
somefile.handprint-google.json
somefile.handprint-google.txt
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
document-1.handprint-google.png
document-1.handprint-google.json
document-1.handprint-google.txt
document-1.handprint-microsoft.png
document-1.handprint-microsoft.json
document-1.handprint-microsoft.txt
...
document-2.jpg
document-2.url
document-2.handprint-google.png
document-2.handprint-google.json
document-2.handprint-google.txt
document-2.handprint-microsoft.png
document-2.handprint-microsoft.json
document-2.handprint-microsoft.txt
...
document-3.jpg
document-3.url
document-3.handprint-google.png
document-3.handprint-google.json
document-3.handprint-google.txt
document-3.handprint-microsoft.png
document-3.handprint-microsoft.json
document-3.handprint-microsoft.txt
...
```

The base name `document` can be changed using the `-b` option (`/b` on Windows).  For example, running Handprint with the option `-b einstein` will cause the outputs to be named `einstein-1.jpg`, `einstein-1.url`, etc.


### _Other options_

The option `-j` (`/j` on Windows) tells Handprint to look for and reuse preexisting results for each input instead of contacting the services.  This makes it look for JSON files produced in a previous run with the `-e` option,
```
somefile.handprint-amazon-rekognition.json
somefile.handprint-amazon-textract.json
somefile.handprint-google.json
somefile.handprint-microsoft.json
```

and use those instead of getting results from the services.  This can be useful to save repeated invocations of the services if all you want is to draw the results differently or perform some testing/debugging on the same inputs.

Handprint will send files to the different services in parallel, using a number of process threads equal to 1/2 of the number of cores on the computer it is running on.  (E.g., if your computer has 4 cores, it will by default use at most 2 threads.)  The `-t` option (`/t` on Windows) can be used to change this number.

If given the `-q` option (`/q` on Windows), Handprint will not print its usual informational messages while it is working.  It will only print messages for warnings or errors.  By default messages printed by Handprint are also color-coded.  If given the option `-Z` (`/Z` on Windows), Handprint will not color the text of messages it prints.  (This latter option is useful when running Handprint within subshells inside other environments such as Emacs.)

If given the `-@` argument (`/@` on Windows), this program will output a detailed trace of what it is doing.  The debug trace will be sent to the given destination, which can be `-` to indicate console output, or a file path to send the output to a file.  On non-Windows platforms, Handprint will also install a signal handler that responds to signal `SIGUSR1`; if the signal is sent to the running process, it will drop Handprint into the `pdb` debugger.  _Note_: It's best to use `-t 1` when attempting to use a debugger because otherwise subthreads will continue running even if the main thread is interrupted.

If given the `-V` option (`/V` on Windows), this program will print the version and other information, and exit without doing anything else.


### _Command line options summary_

The following table summarizes all the command line options available. (Note: on Windows computers, `/` must be used as the prefix character instead of the `-` dash character):

| Short&nbsp;&nbsp;&nbsp;&nbsp;   | Long&nbsp;form | Meaning | Default |  |
|---------------------------------|----------------|---------|---------|--|
| `-a`_A_   | `--add-creds`_A_    | Add credentials for service _A_ and exit | | |
| `-b`_B_   | `--base-name`_B_    | Write outputs to files named _B_-n | Use base names of image files | ⚑ |
| `-C`      | `--no-color`        | Don't color-code info messages | Color-code terminal output |
| `-c`      | `--compare`         | Compare to ground truth; see `-r` too | |
| `-d`_D_   | `--display`_D_      | Display annotation types _D_ | Display text annotations | ★ |
| `-e`      | `--extended`        | Produce extended results | Produce only summary image | |
| `-f`_F_   | `--from-file`_F_    | Read file names or URLs from file _F_ | Use args on the command line |
| `-G`      | `--no-grid`         | Don't create summary image | Create an _N_&times;_N_ grid image| |
| `-h`      | `--help`            | Display help, then exit | | |
| `-j`      | `--reuse-json`      | Reuse prior JSON results if found | Ignore any existing results | | 
| `-l`      | `--list`            | Display known services and exit | | | 
| `-m`_x,y_ | `--text-move`_x,y_  | Move each text annotation by x,y | `0,0` | |
| `-n`_N_   | `--confidence`_N_   | Use confidence score threshold _N_ | `0` | |
| `-o`_O_   | `--output`_O_       | Write all outputs to directory _O_ | Write to images' directories | |
| `-q`      | `--quiet`           | Don't write messages while working | Be chatty while working |
| `-r`      | `--relaxed`         | Use looser criteria for `--compare` | |
| `-s`_S_   | `--service`_S_      | Use recognition service _S_; see `-l` | Use all services | |
| `-t`_T_   | `--threads`_T_      | Use _T_ number of threads | Use (#cores)/2 threads | |
| `-V`      | `--version`         | Write program version info and exit | | |
| `-x`_X_   | `--text-color`_X_   | Use color _X_ for text annotations | Red | |
| `-z`_Z_   | `--text-size`_Z_    | Use font size _Z_ for text annotations | Use font size 12 | |
| `-@`_OUT_ | `--debug`_OUT_      | Write detailed execution info to _OUT_ | Normal mode | ⬥ |

⚑ &nbsp; If URLs are given, then the outputs will be written by default to names of the form `document-n`, where n is an integer.  Examples: `document-1.jpg`, `document-1.handprint-google.txt`, etc.  This is because images located in network content management systems may not have any clear names in their URLs.<br>
★ &nbsp; The possible values of _D_ are: `text`, `bb`, `bb-word`, `bb-line`, `bb-para`. Multiple values must be separated with commas. The value `bb` is a shorthand for `bb-word,bb-line,bb-para`. The default is `text`.<br>
⬥ &nbsp; To write to the console, use the character `-` as the value of _OUT_; otherwise, _OUT_ must be the name of a file where the output should be written.


### _Return values_

This program exits with a return code of 0 if no problems are encountered.  It returns a nonzero value otherwise. The following table lists the possible return values:

| Code | Meaning                                                  |
|:----:|----------------------------------------------------------|
| 0    | success &ndash; program completed normally               |
| 1    | the user interrupted the program's execution             |
| 2    | encountered a bad or missing value for an option         |
| 3    | no network detected &ndash; cannot proceed               |
| 4    | file error &ndash; encountered a problem with a file     |
| 5    | server error &ndash; encountered a problem with a server |
| 6    | an exception or fatal error occurred                     |


### _Additional notes_

The debug logging functionality is implemented using [Sidetrack](https://github.com/caltechlibrary/sidetrack) and all calls to the debug code are conditionalized on the Python symbol `__debug__`.  It is carefully written so that you can cause the calls to be _optimized out completely_ if your run Python with [optimization turned on](https://docs.python.org/3/using/cmdline.html#cmdoption-o) (e.g., using the `-O` command-line option).


## Known issues and limitations

Here are some known limitations in the current version of Handprint:

* If the input has multiple pages, only the first page/image is used; the rest (if any) are ignored.
* The Amazon Rekognition API will return [at most 50 words in an image](https://docs.aws.amazon.com/rekognition/latest/dg/limits.html).
* The Microsoft Azure API will only detect a maximum of [300 lines of text per page](https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/concept-recognizing-text).
* Some services have different file size restrictions depending on the format of the file, but Handprint always uses the same limit for all files for a given service.  This is a code simplification.


## Getting help

If you find an issue, please submit it in [the GitHub issue tracker](https://github.com/caltechlibrary/handprint/issues) for this repository.


## Contributing

I would be happy to receive your help and participation with enhancing Handprint!  Please visit the [guidelines for contributing](CONTRIBUTING.md) for some tips on getting started.


## License

Software produced by the Caltech Library is Copyright © 2021 California Institute of Technology.  This software is freely distributed under a BSD/MIT type license.  Please see the [LICENSE](LICENSE) file for more information.


## Authors and history

[Mike Hucka](https://github.com/mhucka) designed and implemented Handprint beginning in mid-2018.


## Acknowledgments

The [vector artwork](https://thenounproject.com/search/?q=hand&i=733265) of a hand used as a logo for Handprint was created by [Kevin](https://thenounproject.com/kevn/) from the Noun Project.  It is licensed under the Creative Commons [CC-BY 3.0](https://creativecommons.org/licenses/by/3.0/) license.

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
