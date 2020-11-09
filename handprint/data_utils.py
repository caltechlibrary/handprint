'''
data_utils: data manipulation utilities

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2020 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import dateparser
import datetime
from   datetime import datetime as dt
from   dateutil import tz


# Constants.
# .............................................................................

DATE_FORMAT = '%b %d %Y %H:%M:%S %Z'
'''Format in which lastmod date is printed back to the user. The value is used
with datetime.strftime().'''


# Functions.
# .............................................................................

def timestamp():
    '''Return a string describing the date and time right now.'''
    return dt.now(tz = tz.tzlocal()).strftime(DATE_FORMAT)


def parse_datetime(string):
    '''Parse a human-written time/date string using dateparser's parse()
function with predefined settings.'''
    return dateparser.parse(string, settings = {'RETURN_AS_TIMEZONE_AWARE': True})


def plural(word, count):
    '''Simple pluralization; adds "s" to the end of "word" if count > 1.'''
    if isinstance(count, int):
        return word + 's' if count > 1 else word
    elif isinstance(count, (list, set, dict)) or type(count) is {}.values().__class__:
        return word + 's' if len(count) > 1 else word
    else:
        # If we don't recognize the kind of thing it is, return it unchanged.
        return word
