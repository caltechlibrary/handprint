# Advanced Handprint usage

This section describes commands that are somewhat more complex than those described in the [section on basic usage](basic-usage.md).


## Annotation types

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


## Thresholding by confidence

All of the services return confidence scores for items recognized in the input.  By default, Handprint will show all results no matter how low the confidence score.  The option `-n` (`/n` on Windows) can be used to threshold the results based on the confidence value for each item (text or bounding boxes).  The value provided as the argument to the option must be a floating point number between 0 and 1.0.  For example, the following command will make Handprint only show text that is rated with least 99.5% confidence:
```sh
handprint -n 0.995  somefile.png
```

Note that the **confidence values returned by the different services are not normalized against each other**.  What one service considers to be 80% confidence may not be what another service considers 80% confidence.  Handprint performs the thresholding against the raw scores returned by each service individually.


## Comparison to ground truth text

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


## Extended results

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


## Other options

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
