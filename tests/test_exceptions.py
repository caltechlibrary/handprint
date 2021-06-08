import os
import pytest
import sys
from   time import time

try:
    thisdir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(thisdir, '..'))
except:
    sys.path.append('..')

from handprint.exceptions import *

def test_exceptions():
    try:
        raise InternalError('foo')
    except Exception as ex:
        assert isinstance(ex, HandprintException)
        assert str(ex) == 'foo'
