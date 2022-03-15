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

from handprint.images import *


def test_format_name():
    assert canonical_format_name('jpeg') == 'jpeg'
    assert canonical_format_name('jpg') == 'jpeg'
    assert canonical_format_name('TIF') == 'tiff'


def test_image_size():
    thisdir = path.dirname(os.path.abspath(__file__))
    assert image_size(path.join(thisdir, 'data', 'fragments', 'f1.png')) == 15553
    assert image_size(path.join(thisdir, 'data', 'fragments', 'f2.png')) == 8613


def test_image_dimensions():
    thisdir = path.dirname(os.path.abspath(__file__))
    assert image_dimensions(path.join(thisdir, 'data', 'fragments', 'f1.png')) == (340, 106)
    assert image_dimensions(path.join(thisdir, 'data', 'fragments', 'f2.png')) == (228, 60)


def test_reduced_image_size():
    _, tmpfile = tempfile.mkstemp(dir = '/tmp', suffix = '.png')
    thisdir = path.dirname(os.path.abspath(__file__))
    f1_file = path.join(thisdir, 'data', 'fragments', 'f1.png')
    (a, b) = reduced_image_size(f1_file, tmpfile, 1000)
    assert isinstance(a, str)
    assert b is None
    assert image_dimensions(tmpfile) == (22, 7)
    delete_existing(tmpfile)


def test_reduced_image_dimensions():
    _, tmpfile = tempfile.mkstemp(dir = '/tmp', suffix = '.png')
    thisdir = path.dirname(os.path.abspath(__file__))
    f1_file = path.join(thisdir, 'data', 'fragments', 'f1.png')
    (a, b) = reduced_image_dimensions(f1_file, tmpfile, 100, 100)
    assert isinstance(a, str)
    assert b is None
    assert image_dimensions(tmpfile) == (100, 31)
    delete_existing(tmpfile)


def test_converted_image():
    _, tmpfile = tempfile.mkstemp(dir = '/tmp', suffix = '.tiff')
    thisdir = path.dirname(os.path.abspath(__file__))
    f1_file = path.join(thisdir, 'data', 'fragments', 'f1.png')
    (a, b) = converted_image(f1_file, 'tif', tmpfile)
    assert isinstance(a, str)
    assert b is None
    delete_existing(tmpfile)
