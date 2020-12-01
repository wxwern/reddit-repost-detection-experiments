#!/usr/bin/env python3

import os
import sys
import uuid
import signal
from multiprocessing import Pool, cpu_count
from repost.repost_checker import RepostChecker
from repost import repost_multiprocessing as poolRepostChecker

ress   = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
rots   = [-0.5,0.5]
asps   = [0.9,1.1]
crops   = []

for a in [0, 0.05]:
    for b in [0, 0.05]:
        for c in [0, 0.05]:
            for d in [0, 0.05]:
                tmp = (a,b,c,d)
                if tmp != (0,0,0,0):
                    crops.append(tmp)

def initializer():
    """Ignore CTRL+C in the worker process."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def getconfig(res=1.0, rot=0.0, asp=1.0, crop=(0,0,0,0)):
    x = (res,rot,asp,crop)
    _id = ('%x' % abs(hash(x)))[:8]
    return x + (_id,)

def _helper_generate_variant(x):
    return generate_variant(*x)

def generate_variant(dirn,res,rot,asp,crop,uid, verbose=False):
    repostChecker = RepostChecker(dirn)
    repostChecker.verbose = verbose
    repostChecker.readProcessedDataFromCache()
    s_res = ('_res%.1f' % res) if res != 1.0 else ''
    s_rot = ('_rot%.1f' % rot) if rot != 0.0 else ''
    s_asp = ('_asp%.1f' % asp) if asp != 1.0 else ''
    s_crop = ('_crop(%.2f,%.2f,%.2f,%.2f)' % crop) if crop != (0,0,0,0) else ''
    s_idn = '_idn' if s_res == s_rot == s_asp == s_crop == '' else ''

    filename = "%s%s%s%s%s_%s.json" % (s_res, s_rot, s_asp, s_crop, s_idn, uid)
    print("  * " + filename + " --- generating reposts")
    repostChecker.setJsonCacheFilenmaeTarget(filename)
    success = \
        repostChecker.generateRepostsForAll(count_per_post=1,
                                            res=res,
                                            rot=rot,
                                            asp=asp,
                                            crop=crop,
                                            uid=uid)
    if success:
        print("    " + filename + " --- done!")
    else:
        print("  ? " + filename + " --- interrupted!!")
        os.remove(repostChecker.getCacheJsonPath())
    return uid if success else None

variants = [getconfig()]
for res in ress:
    variants.append(getconfig(res=res))
for rot in rots:
    variants.append(getconfig(rot=rot))
for asp in asps:
    variants.append(getconfig(asp=asp))
for crop in crops:
    variants.append(getconfig(crop=crop))

if __name__ == "__main__":
    print("type directory name or path of scraper_cache:")
    dirn = input()
    print("would you like to update the current cache list?")
    update_current_cache = input().lower().startswith('y')
    if update_current_cache:
        tmpRepCh = RepostChecker(dirn)
        tmpRepCh.processData()
    print()
    print('%d repost variants available.' % len(variants))
    print('select a custom range?')
    print('    type 2 space separated digits as your 1-indexed inclusive range, or nothing to skip.')
    variants_range = input().strip().split(' ')
    if len(variants_range) == 2:
        a = int(variants_range[0])
        b = int(variants_range[1])
        print('range: [%d, %d]' % (a,b))
        variants = variants[a-1:b]
    else:
        print('range: unbounded')
    print('%d repost variants to process.' % len(variants))
    print()

    print("will be generating reposts in " + dirn + " using preprocessed post list")
    print("type maximum cpu usage (threads) as a fraction (0.0-1.0]")
    cpu_threshold = float(input())
    threads = max(int(cpu_count()*cpu_threshold), 1)
    if threads > 1:
        print("executing using %d threads" % threads)
        pool = Pool(threads, initializer=initializer)
        args_list = list(map(lambda x: (dirn,) + x, variants))
        try:
            results = []
            for i, e in enumerate(pool.imap_unordered(_helper_generate_variant, args_list), 1):
                print('[%4.2f%% complete]' % (i/len(args_list)*100))
                results.append(e)
            pool.close()
        except KeyboardInterrupt:
            results = []
            pool.terminate()
        finally:
            pool.join()
        results = list(map(lambda x: x is not None, results))
    else:
        print('executing using 1 thread')
        results = []
        try:
            for res,rot,asp,crop,uid in variants:
                v = generate_variant(dirn, res, rot, asp, crop, uid, verbose=True)
                if not v:
                    raise KeyboardInterrupt()
                else:
                    results.append(v)
        except KeyboardInterrupt:
            pass

    print('%d sets of reposts generated' % len(results))
    print('\a')
