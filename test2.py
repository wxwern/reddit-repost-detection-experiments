#!/usr/bin/env python3

from os import listdir
from os.path import isfile, join
from PIL import Image
from ocr import OCR
from hasher import Hasher
from utils import generate_bad_repost
from difflib import SequenceMatcher

if __name__ == '__main__':
    print('this test script is for testing simple repost detection via image hashing and ocr capabilities')

    cache_dir = 'scraper_cache'

    files = [f for f in listdir(cache_dir) if isfile(join(cache_dir, f)) and not f.startswith('.')]
    files.sort()

    d = {}
    t = {}
    print("loading... " + str(len(files)) + ' items')
    for i, file in enumerate(files):
        if i % 100 == 0:
            print('partial: %5d/%d' % (i,len(files)))

        method = 'dHash'
        try:
            img = Image.open(join('scraper_cache', file))
            d[file] = Hasher.hashImage(img, method)
            t[file] = OCR.read2(img)
        except KeyboardInterrupt:
            print('skipped remaining files')
            break
        except:
            print('skipped ' + file)

    print('loaded: ' + str(len(d.items())) + ' items')

    try:
        while True:
            print('\nchoose image name in scraper_cache to compare')
            distances = []
            target_check = input()
            target_path = join(cache_dir, target_check)
            target_img = Image.open(target_path)
            target_hash = Hasher.hashImage(target_img, method)
            target_text = OCR.read2(target_img)

            print('we\'ll now process this post : ' + target_check)

            print('generating new dummy repost : _REPOST_' + target_check)
            bad_img = generate_bad_repost(target_path)
            bad_img_path = join(cache_dir, '_REPOST_' + target_check)
            bad_img_hash = Hasher.hashImage(bad_img, method)
            bad_img_text = OCR.read2(target_img)
            bad_img.save(bad_img_path)
            d['_REPOST_' + target_check] = bad_img_hash
            t['_REPOST_' + target_check] = bad_img_text

            print('\nchecking...')

            for key, value in d.items():
                distances.append( \
                    (key, \
                     Hasher.diff(value, target_hash, 'IMAGE'), \
                     SequenceMatcher(None, t[key] if key in t else '', target_text).ratio()
                     )
                )

            
            def orderOfSort(x):
                '''dynamic sorting to prioritise text if image and text are both really close'''
                img_diff = x[1]
                txt_diff = 1-x[2]
                if txt_diff >= 0.25 or img_diff >= 20:
                    return (img_diff, txt_diff)
                else:
                    return (txt_diff, img_diff)


            distances.sort(key=orderOfSort)


            print('--- similar results ---')
            print(' IMG_DIFF | TEXT_SIM | IMAGE')
            for a,b,c in distances[0:10]:
                print('%8d   %8.3f    %-50s' % (b,c,a))
                subreddit = a.split('_')[0]
                if subreddit == "" and a.split('_')[1] == 'REPOST':
                    subreddit = a.split('_')[2]
                post_id = a.split('_')[-1].split('.')[0]
                print('reddit.com/r/' + subreddit + '/comments/' + post_id + '/')
                if a == target_check:
                    print('* this is the originally chosen image')
                if a == '_REPOST_' + target_check:
                    print('* this is a repost generated based upon the chosen image')
                print()
    except IOError:
        print("oops wrong file")
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
