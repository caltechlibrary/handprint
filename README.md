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

Each image should be a single page of a document in which handwritten text should be recognized.


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
