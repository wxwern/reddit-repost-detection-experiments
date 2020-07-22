#!/usr/bin/env python3

from repost.repost_checker import RepostChecker
from repost import repost_multiprocessing as poolRepostChecker

if __name__ == "__main__":
    repostChecker = RepostChecker('scraper_cache')

    print('this test script is for testing simple repost detection via image hashing and ocr capabilities')
    print('processing images in scraper_cache...')
    repostChecker.processData()
    print('done!')
    print('would you like to check repost detection for individual images now? [y/N]')
    if input().lower().startswith('y'):
        while True:
            try:
                print('type an image name in scraper_cache! (ctrl-c to exit)')
                imgName = input()
                print('generate a repost with prefix _REPOST_? [y/N]')
                shdRepost = input().lower().startswith('y')
                _ = repostChecker.checkRepostDetection(imgName, generate_repost=shdRepost)
            except KeyboardInterrupt:
                break
            except:
                print('something was wrong.')
                continue

    print()
    poolRepostChecker.configurePoolRepostChecker('scraper_cache')
    print('-'*30)
    print('''
if you\'re in an interactive shell,
try the following examples:

    # get other image names flagged as reposts of the given image name
    res = repostChecker.listRepostsOf(imageName)

    # get detailed detection results of this particular image against all images
    res = repostChecker.checkRepostDetection(imageName[, options])

    # finds detection rate w/ all images against all images
    res = repostChecker.findDetectionRate()

    # find detection rate w/ 100 random images against all images,
    # using seed 69 (so we can repeat using the same 100 random images later),
    # given positive result refers to image difference of 15 or less,
    # and text similarity of 60% or higher
    res = repostChecker.findDetectionRate(sample_count=100,
                                          seed=69,
                                          img_diff_min=15,
                                          text_sim_min=0.6)

    # find detection rate w/ 100 random images against all images,
    # using seed 69 (so we can repeat using the same 100 random images later),
    # via a range of image difference and text similarity thresholds
    res = repostChecker.findDetectionRateForThresholdRange(sample_count=100,
                                                           seed=69,
                                                           img_diff_range=range(0,20+1),
                                                           text_sim_range=(x/10 for x in range(0,10+1),
                                                           save_to_file=filename)

for detection rate computations, you may replace the commands with "poolRepostChecker",
which would efficiently utilise all your computer's processing power by
assigning parts of tasks to different threads, e.g.:

    res1 = poolRepostChecker.findDetectionRate(sample_count=100)
    res2 = poolRepostChecker.findDetectionRateForThresholdRange(sample_count=100)

''')


