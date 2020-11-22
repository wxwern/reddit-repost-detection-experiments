#!/usr/bin/env python3

from repost.repost_checker import RepostChecker
from repost import repost_multiprocessing as poolRepostChecker
from PIL import Image
import json

def get_concat_h_resize(im1, im2, resample=Image.BICUBIC, resize_big_image=True):
    if im1.height == im2.height:
        _im1 = im1
        _im2 = im2
    elif (((im1.height > im2.height) and resize_big_image) or
          ((im1.height < im2.height) and not resize_big_image)):
        _im1 = im1.resize((int(im1.width * im2.height / im1.height), im2.height), resample=resample)
        _im2 = im2
    else:
        _im1 = im1
        _im2 = im2.resize((int(im2.width * im1.height / im2.height), im1.height), resample=resample)
    dst = Image.new('RGB', (_im1.width + _im2.width, _im1.height))
    dst.paste(_im1, (0, 0))
    dst.paste(_im2, (_im1.width, 0))
    if (dst.height != 200):
        dst = dst.resize((int(dst.width*200/dst.height), 200), resample=resample)
    return dst

def get_concat_h_resize_list(img_lst, resample=Image.BICUBIC):
    if len(img_lst) == 0:
        return None

    img = img_lst[0]

    if len(img_lst) == 1:
        return img

    for i in range(1, len(img_lst)):
        img = get_concat_h_resize(img, img_lst[i])

    return img

if __name__ == "__main__":

    print('this test script allows for manual flagging of duplicate posts')
    print()
    print('what is the directory to process?')
    dirn = input()
    repostChecker = RepostChecker(dirn)
    print()
    print('would you like to process all data (1) or only load past processed cache (2)?')
    if input() == '1':
        print('what is the limit of posts you want to process? (type nothing for no limit)')
        y = input()
        if y == '':
            y = None
        print('processing images in ' + dirn + '...')
        repostChecker.processData(max_capacity=y)
    else:
        print('loading only from ' + dirn + ' cached json...')
        repostChecker.readProcessedDataFromCache()
    print('done!')

    print('image sample seed?')
    seed = int(input())
    print('image start index?')
    img_start_index = int(input())
    print('image sample count?')
    sample_count = int(input())

    print()
    print('mappings storage json path? (type nothing for a trial run)')
    mappings_filename = input()
    print()

    repostChecker.verbose = False
    imgs = repostChecker.getImagesSample(seed=seed, sample_count=(img_start_index+sample_count))[img_start_index:img_start_index+sample_count]

    mappings = {}

    for img in imgs:
        try:
            results = repostChecker.checkRepostDetection(img=img, img_sim_min=0.7, text_sim_min=0.0, recheck_img=False, generate_repost=False)
        except:
            print('Something went wrong, skipping %s' % img)
            continue
        repost_imgnames = list(results.keys())
        imgs_shown = [img] + repost_imgnames[:10]
        compimg = get_concat_h_resize_list(list(map(lambda x: Image.open(dirn + '/' + x), imgs_shown)))
        compimg.show()
        print('---')
        print('Similar images found within 70%% threshold: %d' % len(results))
        print('Images displayed: %s' % str(imgs_shown))
        print()
        print('Which of these images are exact duplicates of the first image?')
        print('Take the first image to be 1, second to be 2 and so on.')
        print('Type "n" to indicate none.')
        print('Type "a" to show all close matches.')
        inp = input()
        print()

        if inp.lower() == 'a':
            imgs_shown = [img] + repost_imgnames
            compimg = get_concat_h_resize_list(list(map(lambda x: Image.open(dirn + '/' + x), imgs_shown)))
            compimg.show()
            print("please choose again from the following items")
            inp = input()

        if img not in mappings:
            mappings[img] = set()

        if inp.lower() == 'n':
            continue

        for x in list(map(int, inp.split(' '))):
            if x >= 2:
                alt_img = imgs_shown[x-1]
                if alt_img not in mappings:
                    mappings[alt_img] = set()
                mappings[img].add(alt_img)
                mappings[alt_img].add(img)

    if mappings_filename != '':
        for key in list(mappings.keys()):
            mappings[key] = list(mappings[key])
        with open(mappings_filename, "w") as f:
            json.dump(mappings, f, indent=4)
    else:
        print('if you are in an interactive shell, you can access the mappings via the `mappings` global variable')
