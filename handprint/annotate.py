'''
annotate.py: utility for annotating an image with text recognition results

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2018-2019 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import io
import matplotlib
import matplotlib.pyplot as plt

# On macOS 10.13.6 with Python 3.5.7 and matplotlib 3.0.3, when running with
# parallel treads, I experienced random failures in the AGG renderer.  The
# error always manifested itself as an exception that ended like this, on
# different input images with different sizes, even though I always ran on the
# same test images under the same conditions:
#
#   File "/Users/mhucka/system/lib/python3.5/site-packages/matplotlib/figure.py", line 2094, in savefig
#     self.canvas.print_figure(fname, **kwargs)
#   File "/Users/mhucka/system/lib/python3.5/site-packages/matplotlib/backend_bases.py", line 2075, in print_figure
#     **kwargs)
#   File "/Users/mhucka/system/lib/python3.5/site-packages/matplotlib/backends/backend_agg.py", line 560, in print_jpg
#     buf, size = self.print_to_buffer()
#   File "/Users/mhucka/system/lib/python3.5/site-packages/matplotlib/backends/backend_agg.py", line 526, in print_to_buffer
#     FigureCanvasAgg.draw(self)
#   File "/Users/mhucka/system/lib/python3.5/site-packages/matplotlib/backends/backend_agg.py", line 396, in draw
#     self.renderer = self.get_renderer(cleared=True)
#   File "/Users/mhucka/system/lib/python3.5/site-packages/matplotlib/backends/backend_agg.py", line 417, in get_renderer
#     self.renderer = RendererAgg(w, h, self.figure.dpi)
#   File "/Users/mhucka/system/lib/python3.5/site-packages/matplotlib/backends/backend_agg.py", line 87, in __init__
#     self._renderer = _RendererAgg(int(width), int(height), dpi)
#   ValueError: Image size of 4896646x5895191 pixels is too large. It must be less than 2^16 in each direction.
#
# This is a bogus error -- the image did not have this size.  I tried many
# things over many days, thinking the problem was in my code or due to
# threading issues.  Wrapping the savefig() call in threading.lock didn't
# help.  However, switching the backend currently seems to have stopped the
# problem.  The tricky thing about switching backends, however, is that not
# all the backends support all the same output types.  In particular, the
# Cairo backend does not write JPEG output: when you switch to Cairo and save
# a plot as a JPG file, it turns out Matplotlib still invokes AGG.  I had to
# switch not only the backend, but also the output format to PNG (which is
# a format that Cairo does write) in order to make it all work.
#
try:
    plt.switch_backend('cairo')
except:
    pass

import matplotlib.image as mpimg

import handprint
from handprint.debug import log
from handprint.exceptions import *
from handprint.files import relative


# Main functions.
# .............................................................................

def annotated_image(file, text_boxes, service):
    service_name = service.name()

    fig, axes = plt.subplots(nrows = 1, ncols = 1, figsize = (20, 20))
    axes.get_xaxis().set_visible(False)
    axes.get_yaxis().set_visible(False)
    axes.set_title(service_name, color = 'r', fontweight = 'bold', fontsize = 22)

    if __debug__: log('reading image file for {}: {}', service_name, relative(file))
    img = mpimg.imread(file)
    axes.imshow(img, cmap = "gray")

    props = dict(facecolor = 'white', alpha = 0.7)
    if text_boxes:
        if __debug__: log('adding {} annotations for {}', len(text_boxes), service_name)
        polygons = [(item.boundingBox, item.text) for item in text_boxes]
        for polygon in polygons:
            vertices = [(polygon[0][i], polygon[0][i+1])
                        for i in range(0, len(polygon[0]), 2)]
            x = max(0, vertices[0][0] - 4)
            y = max(0, vertices[0][1] - 8)
            text = polygon[1]
            plt.text(x, y, text, color = 'r', fontsize = 11, va = "top", bbox = props)

    if __debug__: log('generating png for {} for {}', service_name, relative(file))
    buf = io.BytesIO()
    fig.savefig(buf, format = 'png', dpi = 300, bbox_inches = 'tight', pad_inches = 0)
    buf.flush()
    buf.seek(0)
    plt.close(fig)

    return buf
