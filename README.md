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

The following is probably the simplest and most direct way to install this software on your computer:
```sh
sudo pip3 install git+https://github.com/caltechlibrary/handprint.git
```

Alternatively, you can clone this GitHub repository and then run `setup.py`:
```sh
git clone https://github.com/caltechlibrary/handprint.git
cd handprint
sudo python3 -m pip install .
```

▶︎ Basic operation
------------------

Currently, Handprint is a command-line driven program.  There is a single command-line interface program unsprisingly called `handprint`.  Before `handprint` can be run, a `credentials.json` file has to be placed in the Handprint module directory.  Once it is there, `handprint` can be run with a directory or a list of image files as argument:

```bash
bin/handprint /path/to/directory/of/images
```

Each image should be a single page of a document in which handwritten text should be recognized.  The images must the least common denominator among the formats accepted by the cloud services, which at this time, is JPEG, PNG, GIF, and BMP.

<!--
* Google: [JPEG, PNG8, PNG24, GIF, Animated GIF (first frame only), BMP, WEBP, RAW, ICO, PDF, TIFF](https://cloud.google.com/vision/docs/supported-files)
* Microsoft: [JPEG, PNG, GIF, or BMP format](https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/home)
-->


Credentials
-----------

Credentials for different services need to be provided in the form of JSON files.  The specific contents and forms of the files differ depending on the particular service.

### Google

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

### Microsoft

Microsoft's approach to credentials in Azure involves the use of [subscription keys](https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/vision-api-how-to-topics/howtosubscribe).  The credentials file for Handprint just needs to contain a single field:

```json
{
 "subscription_key": "thekey"
}
```

The value of "thekey" will be a string such as "18de248475134eb49ae4a4e94b93461c".  When signing up for an Azure cloud service account, make sure to choose "Western US" as the region so that the service URL begins with "https://westus.api.cognitive.microsoft.com".

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
