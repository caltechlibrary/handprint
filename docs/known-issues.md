# Known issues and limitations

Here are some known limitations in the current version of Handprint:
* If the input has multiple pages, only the first page/image is used; the rest (if any) are ignored.
* The Amazon Rekognition API will return [at most 50 words in an image](https://docs.aws.amazon.com/rekognition/latest/dg/limits.html).
* The Microsoft Azure API will only detect a maximum of [300 lines of text per page](https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/concept-recognizing-text).
* Some services have different file size restrictions depending on the format of the file, but Handprint always uses the same limit for all files for a given service.  This is a code simplification.
