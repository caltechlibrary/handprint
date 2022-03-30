---
title: 'Handprint: a program to explore and compare major cloud-based services for handwritten text recognition'
tags:
- handwritten text recognition
- optical character recognition
- machine learning
authors:
- name: Michael Hucka
  orcid: 0000-0001-9105-5960
  affiliation: 1
affiliations:
- name: Caltech Library, California Institute of Technology, Pasadena, CA 91125, USA
  index: 1
date: 5 April 2022
bibliography: paper.bib
---

# Summary

Handprint (_**Hand**written **p**age **r**ecognit**i**o**n** **t**est_) is a command-line application that can invoke cloud-based services to perform handwritten text recognition (HTR) on images of documents. It accepts images in various popular formats, sends them to service providers, gathers the results, annotates copies of the images to show the results to the user, and optionally performs other operations. It currently supports HTR services from Amazon [@AmazonInc.2022amazon; @AmazonInc.2022amazona], Google [@GoogleInc.2022googlea], and Microsoft [@MicrosoftInc.2022microsoft], but its architecture is modular and could be extended to other services. Handprint is a command-line program written in Python and can run on macOS, Windows, and Linux computers.


# Statement of need

The goal of automating the recognition of text dates back, at minimum, to efforts in the 1950's to develop machines for banking applications [@Berkeley1956magnetic; @Dimond1957devices]. The early methods were extremely limited in scope: they focused essentially on numbers only. Thanks to decades of advances in machine learning, document analysis, and computing power, methods have become so advanced that they can now be used to recognize cursive handwriting in dozens of human languages [@Muehlberger2019transforming]. Today, handwritten text recognition (HTR) is even offered as a service by several computing companies over the Internet, on demand, for small fees---without the need to first train a system on samples of a person's handwriting. The recognition results are remarkably good overall, but there are differences in quality and features between the different offerings. Comparing the results produced by the competing services is complicated by the fact that they each have unique application programming interfaces (APIs).

The purpose of Handprint is to make it easier to test HTR services and compare the results, without the need for users to learn how to write program or work with the different APIs. With Handprint, users can easily test cloud-based HTR services on individual images, directories of images, and URLs pointing to images on remote servers, all without writing a line of code. If desired, users can also use Handprint in scripts as part of automated workflows.


# Summary of Handprint usage

## Configuration

The only configuration necessary after installation is to run Handprint with a command-line option to store the user's account credentials for each cloud-based HTR service provider. The command needs to be run once for each desired provider, and thereafter, Handprint will use the account information automatically. The documentation at <https://caltechlibrary.github.io/handprint/> explains the simple file format in which the credentials need to be written.


## Basic features

Handprint can read many common image formats: JP2, JPEG, PDF, PNG, GIF, BMP, and TIFF. Image paths or URLs can be supplied to Handprint in any of the following ways: (a) one or more directory paths or one or more image file paths on the local disk, which will be interpreted as images---either individually or in directories---to be processed; (b) one or more URLs, which will be interpreted as network locations of image files to be processed; or (c) if given the `-f` command-line option (`/f` on Windows), a file containing either image paths or image URLs to be processed. When using URLs, Handprint first downloads the image found at the given URL(s) to a directory of the user's choosing on the local disk. No matter whether files or URLs, each item should be an image of a single document page containing text.

Handprint's basic features include the ability to select a subset of services to use, save the full raw results from HTR services as JSON or text files, and use multiple processor threads to speed up processing. For example, using one of the sample images found in Handprint's source directory, the following command,
```
handprint --text-size 20 --display text,bb-line H96566k.jpg
```
will send image file `H96566K.jpg` to all services currently supported (Amazon Rekognition and Textract, Google Cloud Vision, and Microsoft Azure Computer Vision). The output will be a file named `H96566k.handprint-all.png` with the contents shown in Figure 1.

![Sample output from Handprint. (Source image: Wikipedia [@Wikipediacontributors2012first].)](figures/H96566k.handprint-all.png)

Users can can opt to skip the creation of the overview grid image if they only need the other types of outputs that Handprint can produce.


## Advanced features

Handprint also includes additional, more advanced features, including the following:

* _Controlling the style and placement annotations overlaid on input images_. Users control whether to display recognized text, bounding boxes, or both, and which types of bounding boxes (word, line, and/or paragraph---although not all services provide all types).
* _Filtering the results by confidence scores_. This allows users to see which words or other components have confidence values that meet or exceed a chosen threshold.
* _Comparing text results to expected (ground truth) text_. Users can supply a text file containing the expected text for a given image, and Handprint will calculate the number of errors and the character error rate for each line. The comparison algorithm has some novel capabilities, notably in how it can treat missing, extra, or transposed lines of text from the HTR results (a common difference between the outputs of different services).


# Documentation

A detailed user manual is available at <https://caltechlibrary.github.io/handprint/>. Handprint also prints usage information to the terminal when given the command-line option `--help`.


# Acknowledgments

Handprint benefited from feedback from several people, notably Tommy Keswick, Mariella Soprano, Peter Collopy and Stephen Davison of the Caltech Library, and from bug reports by GitHub users "braytac" (actual name unknown), Tommaso Bendinelli, Tom Morrell, and "syed-9909" (actual name unknown).


# References


