from   commonpy.file_utils import delete_existing
import os
import os.path
import pytest
import sys
import tempfile
from   time import time

try:
    thisdir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(thisdir, '..'))
except:
    sys.path.append('..')

from handprint.comparison import *


def test_text_comparison():
    x = text_comparison('a', 'a')
    assert x == 'Errors\tCER (%)\tExpected text\tReceived text\n0\t0.00\ta\ta\nTotal errors\t\t\t\n0\t\t\t'
    x = text_comparison('a', 'b')
    assert x == 'Errors\tCER (%)\tExpected text\tReceived text\n1\t100.00\tb\t\nTotal errors\t\t\t\n1\t\t\t'
