#!/usr/bin/env python3
# =============================================================================
# @file    setup.py
# @brief   Handprint setup file
# @author  Michael Hucka <mhucka@caltech.edu>
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/caltechlibrary/handprint
# =============================================================================

import os
from   os import path
from   setuptools import setup
import sys

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'requirements.txt')) as f:
    reqs = f.read().rstrip().splitlines()

with open("README.md", "r", errors = 'ignore') as f:
    readme = f.read()

# The following reads the variables without doing an "import handprint",
# because the latter will cause the python execution environment to fail if
# any dependencies are not already installed -- negating most of the reason
# we're using setup() in the first place.  This code avoids eval, for security.

version = {}
with open(path.join(here, 'handprint/__version__.py')) as f:
    text = f.read().rstrip().splitlines()
    vars = [line for line in text if line.startswith('__') and '=' in line]
    for v in vars:
        setting = v.split('=')
        version[setting[0].strip()] = setting[1].strip().replace("'", '')

# Finally, define our namesake.

setup(
    name             = version['__title__'].lower(),
    description      = version['__description__'],
    long_description = readme,
    long_description_content_type = "text/markdown",
    version          = version['__version__'],
    author           = version['__author__'],
    author_email     = version['__email__'],
    maintainer       = version['__author__'],
    maintainer_email = version['__email__'],
    license          = version['__license__'],
    url              = version['__url__'],
    project_urls     = {
        "Tracker": "https://github.com/caltechlibrary/handprint/issues",
        "Source": "https://github.com/caltechlibrary/handprint",
    },
    packages         = ['handprint', 'handprint/services', 'handprint/credentials'],
    scripts          = ['bin/handprint'],
    install_requires = reqs,
    platforms        = 'any',
    python_requires  = '>=3.5',
    classifiers      = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Science/Research',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'Topic :: Text Processing :: Linguistic'
    ]
)