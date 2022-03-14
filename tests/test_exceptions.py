import os
import plac
import pytest
import sys
from   time import time

try:
    thisdir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(thisdir, '..'))
except:
    sys.path.append('..')

from handprint.__main__ import main
from handprint.exceptions import *
from handprint.exit_codes import ExitCode

def test_exceptions():
    try:
        raise InternalError('foo')
    except Exception as ex:
        assert isinstance(ex, HandprintException)
        assert str(ex) == 'foo'


def test_good_cli_arg():
    with pytest.raises(SystemExit) as ex_info:
        output = plac.call(main, ['-V'])
        assert isinstance(output, str)
        assert output.startswith('handprint version')

    assert ex_info.type == SystemExit
    assert ex_info.value.code == int(ExitCode.success)


def test_bad_cli_arg():
    with pytest.raises(SystemExit) as ex_info:
        assert plac.call(main, ['-s', 'bogus'])

    assert ex_info.type == SystemExit
    assert ex_info.value.code == int(ExitCode.bad_arg)
