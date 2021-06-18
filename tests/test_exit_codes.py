import os
import pytest
import sys
from   time import time

try:
    thisdir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(thisdir, '..'))
except:
    sys.path.append('..')

from handprint.exit_codes import *

def test_exceptions():
    assert int(ExitCode.success) == 0
    assert ExitCode.success.meaning == "success -- program completed normally"
