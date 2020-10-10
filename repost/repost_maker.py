#!/usr/bin/env python3

import random
import os
from PIL import Image

def generate_bad_repost(img: Image, count: int=1, save_loc: str=None):
    """
    Generates and returns a modified image based upon the input image, often seen as compression, cropping etc in reposts.

    The resulting image is low in resolution, heavily compressed and warped.

    The input image can be a path as a str or a PIL Image object.
    The output image will always be a PIL Image object.

    If a save location is given, it'll be saved there. If count is greater than one, a list will be returned, and images will have numbers prefixed except the first (which is considered '0').
    """
    if isinstance(img, str):
        img = Image.open(img)

    lst_imgs = []
    while count >= 1:

        x,y = list(img.size)
        downscale_factor = random.uniform(0.2, 0.4)
        downscale_factor = min(max(x*downscale_factor, 250), 350)/x
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

        if save_loc:
            save_dir = str(os.path.sep).join(save_loc.split(str(os.path.sep))[:-1])
            save_name = save_loc.split(str(os.path.sep))[-1]

            if save_dir != '':
                save_dir += str(os.path.sep)
            if count > 1:
                save_name = str(count - 1) + save_name
            new_img.save(save_dir + save_name)

        count -= 1

        lst_imgs.append((save_name if save_loc else None, new_img))

    return lst_imgs if len(lst_imgs) > 1 else new_img
