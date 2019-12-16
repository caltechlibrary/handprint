'''
images.py: utilities for working with images in Handprint

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
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import os
from   os import path
from   PIL import Image
import warnings

# The following is needed for function annotated_image(...) in this file.
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

import handprint
from handprint.debug import log
from handprint.exceptions import *
from handprint.files import relative, readable


# Main functions.
# .............................................................................

def canonical_format_name(format):
    '''Convert format name "format" to a consistent version.'''
    format = format.lower()
    if format in ['jpg', 'jpeg']:
        return 'jpeg'
    elif format in ['tiff', 'tif']:
        return 'tiff'
    else:
        return format


def image_size(file):
    '''Returns the size of the image in 'file', in units of bytes.'''
    if not file or not readable(file):
        return 0
    return path.getsize(file)


def image_dimensions(file):
    '''Returns the pixel dimensions of the image as a tuple of (width, height).'''
    # When converting images, PIL may issue a DecompressionBombWarning but
    # it's not a concern in our application.  Ignore it.
    if not file:
        return (0, 0)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        im = Image.open(file)
        if not im:
            return (0, 0)
        return im.size


def reduced_image_size(orig_file, dest_file, max_size):
    '''Resizes the image and writes a new file named "ORIGINAL-reduced.EXT".
    Returns a tuple of (new_file, error).  The value of 'error' will be None
    if no error occurred; otherwise, the value will be a string summarizing the
    error that occurred and 'new_file' will be set to None.
    '''
    with warnings.catch_warnings():
        # Catch warnings from image conversion, like DecompressionBombWarning
        warnings.simplefilter('ignore')
        try:
            i_size = image_size(orig_file)
            if i_size <= max_size:
                if __debug__: log('file already smaller than requested: {}', orig_file)
                return (orig_file, None)
            ratio = max_size/i_size
            if __debug__: log('resize ratio = {}', ratio)
            im = Image.open(orig_file)
            dims = im.size
            new_dims = (round(dims[0] * ratio), round(dims[1] * ratio))
            if __debug__: log('resizing image to {}', new_dims)
            resized = im.resize(new_dims, Image.HAMMING)
            resized.save(dest_file)
            if __debug__: log('saved resized image to {}', dest_file)
            return (dest_file, None)
        except Exception as ex:
            return (None, str(ex))


def reduced_image_dimensions(orig_file, dest_file, max_width, max_height):
    '''Resizes the image and writes a new file named "ORIGINAL-reduced.EXT".
    Returns a tuple of (new_file, error).  The value of 'error' will be None
    if no error occurred; otherwise, the value will be a string summarizing the
    error that occurred and 'new_file' will be set to None.
    '''
    with warnings.catch_warnings():
        # Catch warnings from image conversion, like DecompressionBombWarning
        warnings.simplefilter('ignore')
        try:
            im = Image.open(orig_file)
            dims = im.size
            width_ratio = max_width/dims[0]
            length_ratio = max_height/dims[1]
            ratio = min(width_ratio, length_ratio)
            new_dims = (round(dims[0] * ratio), round(dims[1] * ratio))
            if __debug__: log('resizing image to {}', new_dims)
            resized = im.resize(new_dims, Image.HAMMING)
            resized.save(dest_file)
            if __debug__: log('saved re-dimensioned image to {}', dest_file)
            return (dest_file, None)
        except Exception as ex:
            return (None, str(ex))


def converted_image(file, to_format, dest_file = None):
    '''Returns a tuple of (success, output file, error message).
    Returns a tuple of (new_file, error).  The value of 'error' will be None
    if no error occurred; otherwise, the value will be a string summarizing the
    error that occurred and 'new_file' will be set to None.
    '''
    if dest_file is None:
        dest_file = filename_basename(file) + '.' + to_format
    # When converting images, PIL may issue a DecompressionBombWarning but
    # it's not a concern in our application.  Ignore it.
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        try:
            im = Image.open(file)
            im.convert('RGB')
            im.save(dest_file, canonical_format_name(to_format))
            if __debug__: log('saved converted image to {}', dest_file)
            return (dest_file, None)
        except Exception as ex:
            return (None, str(ex))


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


# This function was originally based on code posted by user "Maxim" to
# Stack Overflow: https://stackoverflow.com/a/46877433/743730

def create_image_grid(image_files, dest_file, max_horizontal = np.iinfo(int).max):
    '''Create image by tiling a list of images read from files.'''
    n_images = len(image_files)
    n_horiz = min(n_images, max_horizontal)
    h_sizes = [0] * n_horiz
    v_sizes = [0] * ((n_images // n_horiz) + (1 if n_images % n_horiz > 0 else 0))
    images = [Image.open(f) for f in image_files]
    for i, im in enumerate(images):
        h, v = i % n_horiz, i // n_horiz
        h_sizes[h] = max(h_sizes[h], im.size[0])
        v_sizes[v] = max(v_sizes[v], im.size[1])
    h_sizes, v_sizes = np.cumsum([0] + h_sizes), np.cumsum([0] + v_sizes)
    im_grid = Image.new('RGB', (h_sizes[-1], v_sizes[-1]), color = 'white')
    for i, im in enumerate(images):
        im_grid.paste(im, (h_sizes[i % n_horiz], v_sizes[i // n_horiz]))
    im_grid.save(dest_file)
    return im_grid
