#!/usr/bin/env python3

import random
import os
from PIL import Image

def generate_bad_repost(img: Image, count: int=1, res: float = None, rot: float=None, asp: float=None, crop: tuple=None, save_loc: str=None):
    """
    Generates and returns a modified image based upon the input image, often seen as compression, cropping etc in reposts.

    The resulting image is low in resolution, heavily compressed and warped.

    The input image can be a path as a str or a PIL Image object.

    Custom parameters can be provided, including:
    - res: resize factor
    - rot: rotation in degrees
    - asp: aspect ratio (w/h)
    - crop: (L,T,R,B) in percentage
    If None is provided, a random value will be used.

    The output image will always be a PIL Image object.

    If a save location is given, it'll be saved there. If count is greater than one, a list will be returned, and images will have numbers prefixed except the first (which is considered '0').
    """
    if isinstance(img, str):
        img = Image.open(img)

    lst_imgs = []
    while count >= 1:

        x,y = list(img.size)
        if res != 1.0:
            scale_factor = res if res else random.uniform(0.2, 1.0)
            scale_factor = max(x*downscale_factor, 250)/x
        else:
            scale_factor = 1

        x *= scale_factor
        y *= scale_factor

        if asp != 1.0:
            x *= (asp if asp else random.uniform(0.9,1.1))

        new_size = (int(x), int(y))


        if crop is None:
            crop = (random.uniform(0.0,0.02),
                    random.uniform(0.0,0.02),
                    random.uniform(0.0,0.02),
                    random.uniform(0.0,0.02))

        if rot != 0.0:
            rotate_angle = rot if rot else random.uniform(-0.5,0.5)
            crop = list(crop)
            crop[0] += 0.03
            crop[1] += 0.03
            crop[2] += 0.03
            crop[3] += 0.03
            crop = tuple(crop)

        if crop != (0,0,0,0):
            crop_box = \
            (newsize[0]*crop[0],
             newsize[1]*crop[1],
             new_size[0]*(1 - crop[2]),
             new_size[1]*(1 - crop[3]))



        #final computation
        if asp != 1.0 or res != 1.0:
            new_img = img.resize(new_size, Image.ANTIALIAS)
        if rot != 0.0:
            new_img = new_img.rotate(rotate_angle)
        if crop != (0,0,0,0):
            new_img = new_img.crop(crop_box)


        #saving
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
