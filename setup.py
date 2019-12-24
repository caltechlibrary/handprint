#!/usr/bin/env python3
# =============================================================================
# @file    setup.py
# @brief   Installation setup file
# @author  Michael Hucka <mhucka@caltech.edu>
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/caltechlibrary/handprint
#
# Note: configuration metadata is maintained in setup.cfg.  This file exists
# primarily to hook in setup.cfg and requirements.txt.
#
# =============================================================================

import os
from   os import path
from   setuptools import setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'requirements.txt')) as f:
    reqs = f.read().rstrip().splitlines()

setup(
    setup_requires = ['wheel'],
    install_requires = reqs,
)
