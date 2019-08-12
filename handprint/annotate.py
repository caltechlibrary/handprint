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

def annotated_image(file, text_boxes, service):
    service_name = service.name()

    fig, axes = plt.subplots(nrows = 1, ncols = 1, figsize = (20, 20))
    axes.get_xaxis().set_visible(False)
    axes.get_yaxis().set_visible(False)
    axes.set_title(service_name, color = 'r', fontweight = 'bold', fontsize = 22)

    if __debug__: log('reading image file {} for {}', relative(file), service_name)
    axes.imshow(mpimg.imread(file), cmap = "gray")

    # Basic sanity check against something going really wrong.
    (width, height) = fig.get_size_inches()*fig.dpi     # size in pixels
    if width > 100000 or height > 100000:
        # This happens occasionally at random.  I think there's some thread
        # safety issue causing data corruption somewhere, but I haven't solved it.
        return None

    props = dict(facecolor = 'white', alpha = 0.7)
    if text_boxes:
        if __debug__: log('adding {} annotations for {}', len(text_boxes), service_name)
        polygons = [(item.boundingBox, item.text) for item in text_boxes]
        for polygon in polygons:
            vertices = [(polygon[0][i], polygon[0][i+1])
                        for i in range(0, len(polygon[0]), 2)]
            text = polygon[1]
            plt.text(vertices[0][0] - 4, vertices[0][1] - 8, text, color = 'r',
                     fontsize = 11, va = "top", bbox = props)

    if __debug__: log('saving {} annotated image {}', service_name, relative(file))
    try:
        buf = io.BytesIO()
        plt.savefig(buf, format = 'jpg', dpi = 300, bbox_inches = 'tight', pad_inches = 0)
        buf.seek(0)
    except Exception as ex:
        if __debug__: log('error saving {} annotated image: {}', service_name, str(ex))
        return None
    finally:
        plt.close(fig)
    return buf
