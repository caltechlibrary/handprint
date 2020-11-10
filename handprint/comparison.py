'''
comparison.py: compare results to ground truth

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2019-2020 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from collections  import namedtuple
from stringdist   import levenshtein
from textdistance import lcsseq
# Shorten this name for easier reading in the code below.
lcsseq_score = lcsseq.normalized_similarity

import handprint
from handprint.exceptions import *


# Data structures.
# .............................................................................

Line = namedtuple('Line', 'number distance cer gt_text htr_text')
Line.__doc__ = '''Data about one line in the comparison results.
  'number' is the line number in the HTR text results
  'distance' is the Levenshtein distance between the HTR text and the g.t.
  'cer' is the character error for the HTR text line
  'gt_text' is the ground truth text line
  'htr_text' is the HTR text line
'''


# Constants.
# .............................................................................

_SIMILARITY_THRESHOLD = 0.5

_PUNCTUATION_REMOVER = str.maketrans('', '', '.,:;')


# Main functions.
# .............................................................................

def text_comparison(htr_text, gt_text, relaxed = False):
    '''Compare the HTR result text in "htr_text" with the expected ground truth
    text in "gt_text".  Returns a tab-separated table describing the results.

    This function accounts for the possibility that the HTR results may not
    contain a line of text for every line of ground truth, and conversely,
    may also contain lines of text that are not supposed to appear.  The
    approach uses a novel algorithm to compare the texts line-by-line using
    longest common subsequence similarity (as implemented by the LCSSEQ
    function in the Python "textdistance" package), to try to match up
    corresponding lines in the two texts before calculating Levenshtein
    distance and CER for each line individually.
    '''

    # This works by building up an intermediate data structure that consists
    # of a list of tuples of type "Line" (a named tuple).  Each has this form:
    #
    #    (htr line #,  Levenshtein error,  CER,  gt line text,  htr line text)
    #
    # If a line is missing from the htr text (relative to the gt text), its
    # line number is written as None.  If a line is missing from the gt text
    # (relative to the htr text), its value (in the "gt line text" column) is
    # written as ''.  The order of the list of tuples is important; in the
    # end it represents the entire list of text lines present in either the
    # gt text or htr text.  Here is an example showing missing lines:
    #
    #    htr line #   gt text             htr text
    #    ----------   -------            --------
    #        1        ""                  doc 01
    #        2        April 25, 2019      Avril 25, 2019
    #        3        My darling,         My darling,
    #      None       what a wonderful    ""
    #        4        day today was.      bay today vas.
    #        5        ""                  rooujjlh
    #
    # The final outcome for the above will have 6 lines, even though the ground
    # truth has 4 lines, in order to describe the fact that the HTR text
    # contains extra lines text at the beginning and end.  The HTR text is also
    # missing a line in the middle.

    # Algorithm:
    # 1) Go through the gt text lines one at a time in linear order, and
    #    compare each line to each line of the HTR text using LCSSEQ.  If
    #    a line in the gt text does not appear in the HTR text (judged by
    #    the LCSSEQ score not crossing a certain threshold), mark that line
    #    as missing; otherwise, store the Levenshtein distance and CER scores
    #    for that line in a tuple.
    #
    # 2) Go through the list of tuples and find all lines in the HTR text
    #    that do not exist in the gt text.
    #
    # 3) Go through this list of extra HTR lines and insert tuples in the
    #    correct locations in the main list of tuples.
    #
    # 4) Go through the list of tuples, add up error scores and other things
    #    and produce the final output string.

    gt_lines  = gt_text.strip().splitlines()
    htr_lines = htr_text.strip().splitlines()
    htr_index = 0
    results   = []

    if relaxed:
        gt_lines  = [text.lower() for text in gt_lines]
        gt_lines  = [text.translate(_PUNCTUATION_REMOVER) for text in gt_lines]
        htr_lines = [text.lower() for text in htr_lines]
        htr_lines = [text.translate(_PUNCTUATION_REMOVER) for text in htr_lines]

    for gt_line in gt_lines:
        htr_line = htr_lines[htr_index]
        if lcsseq_score(gt_line, htr_line) >= _SIMILARITY_THRESHOLD:
            results.append(line_data(gt_line, htr_line, htr_index))
            htr_index += 1
        else:
            # LCSSEQ score too low => lines don't correspond.  Also means the
            # line in the HTR text is something not found in the gt text.
            # Check if any line later in the HTR text matches any better.
            for other_index, other_line in enumerate(htr_lines[htr_index + 1:], 1):
                if lcsseq_score(gt_line, other_line) >= _SIMILARITY_THRESHOLD:
                    # We found a matching line.
                    htr_index += other_index
                    results.append(line_data(gt_line, other_line, htr_index))
                    break
            else: # "else" for the for loop, not the if stmt!
                # Nothing sufficiently close. Treat as missing.
                results.append(line_data(gt_line, '', None))

    # Are there any lines in htr_text after the end of the lines in gt_text?
    # If so, add them (as errors) to the results.
    if len(htr_lines) - (htr_index + 1) > 0:
        for index, line in enumerate(htr_lines[htr_index + 1:], htr_index + 1):
            results.append(line_data('', line, index))

    # At this point, if there are gaps in the htr line numbers that we
    # stored, it means those are extra lines in the beginning or middle of
    # the htr text.  Find and insert those lines into the results list.
    matched = [line.number for line in results if line.gt_text != '']
    extra_lines = [i for i in range(0, len(htr_lines)) if i not in matched]
    for index in extra_lines:
        # Find the previous location in the results list.  We will insert a
        # new tuple after it.
        for pos, line in enumerate(results):
            if line.number is not None and index < line.number:
                results.insert(pos, line_data('', htr_lines[index], index))
                break

    # We return data as 4 columns.
    output = ['Errors\tCER (%)\tExpected text\tReceived text']
    total_errors = 0
    for line in results:
        total_errors += line.distance
        output.append('{}\t{}\t{}\t{}'.format(
            line.distance, line.cer, line.gt_text, line.htr_text))
    # Append total errors count, and we're done.
    output.append('Total errors\t\t\t')
    output.append(str(total_errors) + '\t\t\t')
    return '\n'.join(output)


# Helper functions.
# ......................................................................

def line_data(gt_line, htr_line, htr_index):
    # Remove leading spaces and compress runs of spaces in the line.
    expected = ' '.join(gt_line.split())
    obtained = ' '.join(htr_line.split())
    # The stringdist package definition of levenshtein_norm() divides
    # by the longest of the two strings, but it is more conventional in
    # OCR papers and software to divide by the length of the reference.
    distance = levenshtein(expected, obtained)
    if len(expected) > 0:
        cer = '{:.2f}'.format(100 * float(distance)/len(expected))
    else:
        cer = '100.00'
    return Line(htr_index, distance, cer, expected, obtained)
