'''
comparison.py: compare results to ground truth

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2019 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from stringdist import levenshtein
from textdistance import lcsseq
# Shorten this name for easier reading in the code below.
lcsseq_score = lcsseq.normalized_similarity

import handprint
from handprint.debug import log
from handprint.exceptions import *


# Constants.
# .............................................................................

_SIMILARITY_THRESHOLD = 0.5


# Main functions.
# .............................................................................

def text_comparison(htr_text, gt_text):
    # We return data as 4 columns.
    output = [('# errors', 'CER (%)', 'Expected text', 'Actual text')]
    total_errors = 0

    # The HTR results may not contain text for every line of text expected.
    # The following tries to match up results to expected lines by scoring
    # them using a normalized LCSSEQ distance.
    htr_index = 0
    htr_lines = htr_text.splitlines()
    for gt_line in gt_text.splitlines():
        htr_line = htr_lines[htr_index]
        if lcsseq_score(gt_line, htr_line) >= _SIMILARITY_THRESHOLD:
            (lev, cer, expected, obtained) = line_score(gt_line, htr_line)
            output.append((str(lev), cer, expected, obtained))
            total_errors += lev
            htr_index += 1
        else:
            # LCSSEQ score too low => lines don't correspond.  Check if any
            # line later in the results matches any better.
            for other_index, other_line in enumerate(htr_lines[htr_index + 1:]):
                if lcsseq_score(gt_line, other_line) >= _SIMILARITY_THRESHOLD:
                    # We found a matching line.
                    (lev, cer, expected, obtained) = line_score(gt_line, other_line)
                    output.append((str(lev), cer, expected, obtained))
                    total_errors += lev
                    htr_index += other_index + 1
            else: # "else" for the for loop, not the if stmt!
                # Nothing sufficiently close. Treat as missing. CER = 100%.
                lev = len(gt_line)
                total_errors += lev
                output.append((str(lev), '100.00', gt_line, ' '))
    # Convert current 'output' values (tuples) to tab-delimited strings.
    output = ['\t'.join(x) for x in output]
    # Append total errors count, and we're done.
    output.append('Total # errors')
    output.append(str(total_errors))
    return '\n'.join(output)


# Helper functions.
# ......................................................................

def line_score(gt_line, htr_line):
    # Remove leading spaces and compress runs of spaces in the line.
    expected = ' '.join(gt_line.split())
    obtained = ' '.join(htr_line.split())
    # The stringdist package definition of levenshtein_norm() divides
    # by the longest of the two strings, but it is more conventional in
    # OCR papers and software to divide by the length of the reference.
    lev = levenshtein(expected, obtained)
    if len(expected) > 0:
        cer = '{:.2f}'.format(100 * float(lev)/len(expected))
    else:
        cer = 'n/a'
    return (lev, cer, expected, obtained)
