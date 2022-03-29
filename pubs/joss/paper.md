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

Handprint (_**Hand**written **p**age **r**ecognit**i**o**n** **t**est_) is a command-line application that can invoke cloud-based services to perform handwritten text recognition (HTR) on images of documents. It accepts images in various popular formats, sends them to the service providers, gathers the results, and then annotates copies of the images to show the results to the user. It currently supports HTR services from Amazon [@AmazonInc.2022amazon; @AmazonInc.2022amazona], Google [@GoogleInc.2022googlea], and Microsoft [@MicrosoftInc.2022microsoft], but its architecture is modular and could be extended to other services. Handprint is a command-line program written in Python and can run on macOS, Windows, and Linux computers.


# Statement of need

Several of cloud computing companies have developed machine learning-based methods for handwritten text recognition (HTR) and offer them as on-demand services. These network-based services can be applied to images of document pages without the need for training on samples of handwriting. The results are remarkably good overall, but there are differences in quality and features between the different offerings. Comparing the results produced by the competing services is complicated by the fact that they each have unique application programming interfaces (APIs). The purpose of Handprint is to make comparisons simple and easy, without the need for users to learn how to program with the different APIs. With Handprint, users can easily process individual images, directories of images, and URLs pointing to images on remote servers without writing a line of code. If desired, users can also use Handprint in scripts as part of automated workflows.


# Summary of Handprint usage

This section summarizes the user-accessible capabilities provided by Handprint.

## Configuration

The only configuration necessary after installation is to run Handprint with a certain command-line option to store the user's account credentials for each cloud-based HTR service provider. The command needs to be run once for each desired provider, and thereafter, Handprint will use the account information automatically. The Handprint documentation at <https://caltechlibrary.github.io/handprint/> explains the simple file format in which the credentials need to be written.


## Basic features

Handprint can read a number of common image formats: JP2, JPEG, PDF, PNG, GIF, BMP, and TIFF. Image paths or URLs can be supplied to Handprint in any of the following ways: (a) one or more directory paths or one or more image file paths on the local disk, which will be interpreted as images---either individually or in directories---to be processed; (b) one or more URLs, which will be interpreted as network locations of image files to be processed; or (c) if given the `-f` command-line option (`/f` on Windows), a file containing either image paths or image URLs to be processed. When using URLs, Handprint first downloads the image found at the given URL(s) to a directory of the user's choosing on the local disk. No matter whether files or URLs, each item should be a single image of a document page containing text.

Handprint's basic features include the ability to display different kinds of bounding boxes, save the full raw results from HTR services as JSON or text files, and use multiple processor threads to speed up processing. For example, using one of the sample images found in Handprint's source directory, the following command,
```
handprint --text-size 19 --display text,bb-line H96566k.jpg
```
will send, in parallel, the image file named `H96566K.jpg` to the four services currently supported (Amazon Rekognition, Amazon Textract, Google Cloud Vision, and Microsoft Azure Computer Vision). The output will be a file named `H96566k.handprint-all.png` with the contents shown in the figure below.

![**Figure 1**: Example of output from Handprint using default settings.(Source image obtained from Wikipedia [@Wikipediacontributors2012first].)](H96566k.handprint-all.png)

Users can also select a subset of services to use, and can opt to skip the creation of the overview grid image if they only need the other types of outputs that Handprint can produce.


## Advanced features

Handprint also includes additional, more advanced features. One is the ability to filter the displayed results by confidence scores, allowing users to see which words or other components have confidence values that meet or exceed a chosen threshold. Another is a facility to compare text results to expected (ground truth) text. The comparison algorithm has some novel capabilities, notably in how it can treat missing, extra, or transposed lines of text from the HTR results (a common difference between the outputs of different services).


# Documentation

A detailed user manual is available as a GitHub Pages website at <https://caltechlibrary.github.io/handprint/>. Handprint also prints usage information to the terminal when given the command-line option `--help`.


# Acknowledgments

The development of Handprint was supported by the Caltech Library. Handprint benefitted from feedback from several people, notably Tommy Keswick, Mariella Soprano, Peter Collopy and Stephen Davison of the Caltech Library. The [vector artwork](https://thenounproject.com/search/?q=hand&i=733265) of a hand used as a logo for Handprint was created by [Kevin](https://thenounproject.com/kevn/) for the [Noun Project](https://thenounproject.com).


# References
