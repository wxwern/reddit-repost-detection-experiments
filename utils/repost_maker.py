#!/usr/bin/env python3

import random
from PIL import Image

def generate_bad_repost(img: Image):
    """
    Generates and returns a modified image based upon the input image, often seen as compression, cropping etc in reposts.

    The resulting image is low in resolution, heavily compressed and warped.

    The input image can be a path as a str or a PIL Image object.
    The output image will always be a PIL Image object.
    """
    if isinstance(img, str):
        img = Image.open(img)

    x,y = list(img.size)
    downscale_factor = random.uniform(0.2, 0.4)
    downscale_factor = min(max(x*downscale_factor, 250), 500)/x
    x *= downscale_factor * random.uniform(0.9, 1.1)
    y *= downscale_factor * random.uniform(0.9, 1.1)
    new_size = (int(x), int(y))

    rotate_angle = random.uniform(-0.5,0.5)

    crop_box = \
    (random.randint(3,10),
     random.randint(3,10),
     new_size[0] - random.randint(3,10),
     new_size[1] - random.randint(3,10))


    new_img = img.resize(new_size, Image.ANTIALIAS) \
                 .rotate(rotate_angle).crop(crop_box)

    return new_img
