from __future__ import absolute_import
from buzz_celery.celery import app

import os
import uuid
import urllib.request

@app.task
def download_image(uri, target):
    '''
    Simply download an image save it to disk. Many of the incoming links
    will be obfuscated, a la:

        https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9Gc \
        Txoeplnod_6RvVpgLowerb1jzsm5NxRQ1y8A&usqp=CAU

    so we will assume JPG. There are some circumstances in which the file
    is specifically PNG, a la:

        https://www.morayhousetrust.com/wp-content/uploads/2019/02/Jagan.org-2.png

    We could in theory keep the PNG but that makes our image directory
    less homogenous. 

    Alternatively, you can always use PIL (Image.fomat) to go back and
    rename the PNGs. Though to be honest, the file extension is just to make
    the OS happy. When it comes to computation, we obviously are more rigorous
    '''

    # Save directory
    out_dir = os.path.join('images', target.replace(' ', '_'))

    # Make sure the output path exists
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # We actually remove the original file name to avoid collisions, as
    # well because it's not always available. We generate a random id for the file
    filename = uuid.uuid4().hex[:8] + '.jpg'

    # Download
    try:
        urllib.request.urlretrieve(uri, os.path.join(out_dir, filename))
    except urllib.error.HTTPError:
        pass