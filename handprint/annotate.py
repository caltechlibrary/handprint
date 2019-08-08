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
import matplotlib.image as mpimg

import handprint
from handprint.debug import log
from handprint.files import relative


# Main functions.
# .............................................................................

def annotated_image(file, text_boxes, service_name):
    fig, axes = plt.subplots(nrows = 1, ncols = 1, figsize = (20, 20))
    axes.get_xaxis().set_visible(False)
    axes.get_yaxis().set_visible(False)
    axes.set_title(service_name, color = 'r', fontweight = 'bold', fontsize = 14)

    if __debug__: log('reading image file {} for {}', relative(file), service_name)
    axes.imshow(mpimg.imread(file), cmap = "gray")

    props = dict(facecolor = 'white', alpha = 0.6)
    if text_boxes:
        if __debug__: log('adding {} annotations for {}', len(text_boxes), service_name)
        polygons = [(item.boundingBox, item.text) for item in text_boxes]
        for polygon in polygons:
            vertices = [(polygon[0][i], polygon[0][i+1])
                        for i in range(0, len(polygon[0]), 2)]
            text = polygon[1]
            plt.text(vertices[0][0], vertices[0][1], text, color = 'r',
                     fontsize = 8, va = "top", bbox = props)

    if __debug__: log('saving annotated {} image for {}', relative(file), service_name)
    buf = io.BytesIO()
    plt.savefig(buf, format = 'jpg', dpi = 300, bbox_inches = 'tight', pad_inches = 0)
    buf.seek(0)
    return buf
