# Notes about the Google Vision text recognition API

These notes correspond to v1 and v1p4beta1. I obtained the Python package from PyPI. These notes correspond to [version 2.3.1](https://pypi.org/project/google-cloud-vision/2.3.1/), released on 2021-04-13.

## Calling the service

The basic API is obtained by importing `google.cloud.vision_v1`.  For example,

```python
from google.cloud import vision_v1 as gv
```

To invoke image recognition, you need a client object of type `ImageAnnotatorClient` and an `ImageContext` object. To set certain parameters, you also need a `TextDetectionParams` object. In principle, the parameters available are described in the [documentation for `TextDetectionParams`](https://cloud.google.com/vision/docs/reference/rpc/google.cloud.vision.v1#google.cloud.vision.v1.TextDetectionParams); however, as of 2021-06-10, **only `enable_text_detection_confidence_score` is supported** by `TextDetectionParams`, which you can verify by looking at the [API documentation for `TextDetectionParam`](https://googleapis.dev/python/vision/latest/vision_v1/types.html?highlight=textdetectionparam#google.cloud.vision_v1.types.TextDetectionParams) as well as the [source code in GitHub](https://googleapis.dev/python/vision/latest/_modules/google/cloud/vision_v1/types/image_annotator.html#TextDetectionParams). `ImageContext` also takes a `language_hints` parameter, which for English handwriting, should be set to `"en-t-i0-handwrit"`. 

All together, this leads to the following code to get the client and context objects:

```python
client  = gv.ImageAnnotatorClient()
params  = gv.TextDetectionParams(mapping = { 'enable_text_detection_confidence_score': True })
context = gv.ImageContext(language_hints = ['en-t-i0-handwrit'], text_detection_params = params)
```

If you do not include the parameters for the confidence score, the results come back with _some_ confidence scores, but not as many.

Next, you need to create an object containing the image to be uploaded to Google. Assuming the raw bytes of a PNG (or similar) image are stored in the variable `image`, you can do this as follows:

```python
img = gv.Image(content = image)
```

And now you can invoke the text recognition service on the image. There are two flavors: `TEXT_DETECTION` and `DOCUMENT_TEXT_DETECTION`. Both are used for OCR, but as described in the [Google Vision API documentation](https://cloud.google.com/vision/docs/ocr#optical_character_recognition_ocr), the `DOCUMENT_TEXT_DETECTION` service is "optimized for dense text and documents", and thus presumably more suited to handling scanned documents. (In my testing on pretty easy text pages bears this out; the results from `TEXT_DETECTION` were worse.)

```python
response = client.document_text_detection(image = img, image_context = context)
```

More information about this service can be found in the section of Google's docs titled [Detect handwriting in images](https://cloud.google.com/vision/docs/handwriting), and in particular the section on [specifying the language](https://cloud.google.com/vision/docs/handwriting#specify_the_language_optional), which has a box explaining how the language hint works.

To help figure out how to parse the results, the [Document Text Tutorial](https://cloud.google.com/vision/docs/fulltext-annotations) is worth reading. In the end, I came up with code by inspecting the results and figuring out what the different parts were. See in particular the [sample code for `doctext.py`](https://github.com/googleapis/python-vision/blob/HEAD/samples/snippets/document_text/doctext.py).

To get the full text of a page, there are three approaches possible:
* Access `full_text_annotation.text` from the `response` object. 
* Access `text_annotation.description` from the `response` object. In the limited tests I've done on this, the contents were always the same as `full_text_annotation.text`.
* Traverse the hierarchy of objects returned in the list of `full_text_annotation.pages` objects. These will be blocks, paragraphs, words, and symbols. The symbol objects contain in addition indications of breaks in the text. In my testing, assembling words into lines (using the break indicators) produced the same results as the full text annotation text.
