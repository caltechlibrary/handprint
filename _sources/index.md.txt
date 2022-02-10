# Handprint<img width="75em" align="right" style="display: block; margin: auto auto 2em 2em"  src="_static/media/handprint-icon.svg">

The _**Hand**written **p**age **r**ecognit**i**o**n** **t**est_ is a command-line program that invokes HTR (handwritten text recognition) services on images of document pages.  It can produce annotated images showing the results, compare the recognized text to expected text, save the HTR service results as JSON and text files, and more. Handprint currently supports Google's [Google Cloud Vision API](https://cloud.google.com/vision/docs/ocr), Microsoft's Azure [Computer Vision API](https://azure.microsoft.com/en-us/services/cognitive-services/computer-vision/), and Amazon's [Textract](https://aws.amazon.com/textract/) and [Rekognition](https://aws.amazon.com/rekognition/); its framework for connecting to services could be expanded to support others in the future.

## Sections

```{toctree}
---
maxdepth: 2
---
installation.md
configuration.md
basic-usage.md
advanced-usage.md
command-summary.md
known-issues.md
colophon.md
```
