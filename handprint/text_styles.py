'''
text_styles: color & style definitions for use with Python colorful.

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2019 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import colorful
from   os import path

from .debug import log

# A missing load statement in colorful 0.53 (the currently-released version
# as of 2019-08-29) means the COLORNAMES_COLOR palette was actually not
# defined until version 0.54 (c.f. issue #31 and the commit at
# https://github.com/timofurrer/colorful/commit/8e3ea7293ca5a5d98aa427116211992088ffc9fc
# This loads the file directly, and as a fallback, defines the colors we need.

try:
    rgb_file = path.join(colorful.__path__[0], 'data/rgb.txt')
    if path.exists(rgb_file):
        if __debug__: log('loading colorful colors from {}', rgb_file)
        colorful.setup(colorpalette = rgb_file)
    else:
        if __debug__: log('cannot find colorful rgb.txt file')
except Exception:
    colorful.update_palette({
        'springGreen4'    : (  0, 139, 69),
    })

# The following defines the basic styles we use in this application.
# Regarding the ones like 'bold': There are more possible using the Python
# colorful and other packages, but not all work on all platforms
# (particularly Windows) and not all are that useful in pratice.  Note: the
# following have to be defined after the palette above is loaded into
# "colorful", or else the colors used below will not be defined when the
# _COLORS dictionary is created at load time.

_STYLES = {
    'info'          : colorful.springGreen4,
    'warn'          : colorful.orange,
    'warning'       : colorful.orange,
    'error'         : colorful.red,
    'fatal'         : colorful.red & colorful.bold & colorful.underlined,

    'blink'         : colorful.blinkslow,
    'bold'          : colorful.bold,
    'italic'        : colorful.italic,
    'struckthrough' : colorful.struckthrough,
    'underlined'    : colorful.underlined,
}

colorful.update_palette(_STYLES)
