#!/usr/bin/env python3

try:
    from repost_checker import RepostChecker
except ImportError:
    from .repost_checker import RepostChecker
from multiprocessing import Pool, cpu_count
import json
import time

_poolRepostChecker = RepostChecker('scraper_cache')
_poolRepostChecker.verbose = False
_poolRepostChecker.update_cache = False
_poolRepostChecker.readProcessedDataFromCache()

def configurePoolRepostChecker(img_dir: str):
    global _poolRepostChecker
    _poolRepostChecker = RepostChecker(img_dir)
    _poolRepostChecker.verbose = False
    _poolRepostChecker.update_cache = False
    _poolRepostChecker.readProcessedDataFromCache()

def _helperFindDetectionRateFromImage(args):
    i = args[0]
    img = args[1]
    idm = args[2]
    tsm = args[3]
    _VERBOSE = args[4]
    if _VERBOSE:
        print('process : item %-5d i.e. %s' % (i, img))
    res = _poolRepostChecker.findDetectionRate(imgs_list=[img],
                                               img_diff_min=idm,
                                               text_sim_min=tsm)
    if _VERBOSE:
        print('finished: item %-5d i.e. %s' % (i, img))
    return res

def _helperFindDetectionRateFromThresholds(args):
    i = args[0]
    imgl = args[1]
    idm = args[2]
    tsm = args[3]
    _VERBOSE = args[4]
    if _VERBOSE:
        print('process : pair %-4d i.e. idm %4d tsm %4.3f' % (i, idm, tsm))
    res = _poolRepostChecker.findDetectionRate(imgs_list=imgl, img_diff_min=idm, text_sim_min=tsm)
    d = {'img_diff_min': idm, 'text_sim_min': tsm, 'results': res}
    if _VERBOSE:
        print('finished: pair %-4d i.e. idm %4d tsm %4.3f -> %s' % (i, idm, tsm, res))
    return d

def findDetectionRate(imgs_list: list = None,
                      seed: int = 69,
                      biased_target: str = None,
                      biased_factor: float = None,
                      sample_count: int = None,
                      img_diff_min: int = 15,
                      text_sim_min: float = 0.7,
                      verbose: bool = True):

    _poolRepostChecker.readProcessedDataFromCache()
    if biased_factor is None:
        names = _poolRepostChecker.getImagesSample(imgs_list=imgs_list,
                                                   sample_count=sample_count,
                                                   seed=seed)
    else:
        names = _poolRepostChecker.getBiasedImagesSample(imgs_list=imgs_list,
                                                         biased_target=biased_target,
                                                         biased_factor=biased_factor,
                                                         sample_count=sample_count,
                                                         seed=seed)


    print('processing detection rate for particular samples and thresholds.')
    print('note: this should utilise at most 90% of cpu power.')
    print('elements to process: %d' % len(names))

    args_list = list(map(lambda x: [0, x, img_diff_min, text_sim_min, verbose], names))
    for i, _ in enumerate(args_list):
        args_list[i][0] = i + 1

    pool = Pool(max(int(cpu_count()*0.9), 1))
    results = pool.map(_helperFindDetectionRateFromImage, args_list)
    pool.close()
    pool.join()

    print('tallying up results')

    vC = {'TP':0,'FP':0,'TN':0,'FN':0,'??':0}
    for r in results:
        vC['TP'] += r['TP']
        vC['TN'] += r['TN']
        vC['FP'] += r['FP']
        vC['FN'] += r['FN']
        vC['??'] += r['??']

    print()
    if sample_count:
        print('-- results (sample count) --')
    else:
        print('-- results --')
    try:
        precision = round(vC['TP']/(vC['TP'] + vC['FP']),5)
        recall    = round(vC['TP']/(vC['TP'] + vC['FN']),5)
        accuracy  = round((vC['TP'] + vC['TN'])/(vC['TP'] + vC['TN'] + vC['FP'] + vC['FN']),5)
        f1_score  = round(2*vC['TP']/(2*vC['TP'] + vC['FP'] + vC['FN']), 5)
        print('precision : %4.3f%%' % (precision*100))
        print('recall    : %4.3f%%' % (recall*100))
        print('accuracy  : %4.3f%%' % (accuracy*100))
        print('f1_score  : %4.3f%%' % (f1_score*100))
        vC['precision'] = round(precision, 8)
        vC['recall']    = round(recall, 8)
        vC['accuracy']  = round(accuracy, 8)
        vC['f1_score']  = round(f1_score, 8)
    except ZeroDivisionError:
        print('failed to compute metrics due to division by zero')

    print('stats     : %s' % str(vC))
    print()


    return vC

def benchmark(sample_count=200):
    print('testing repost detection processing speed...')
    print('-'*30)
    ini = time.time()
    findDetectionRate(sample_count=sample_count, img_diff_min=10, text_sim_min=0.1, verbose=False)
    print('-'*30)
    dtime = time.time() - ini
    total_count = len(_poolRepostChecker.getImagesSample())
    post_count = min(sample_count,total_count)
    post_p_s = round(post_count/dtime, 3)
    print('benchmark v3')
    print('time taken:\n- %.3f seconds for sample count %d' % (dtime, post_count))
    print('speed:\n- %.3f posts per second against %d posts each' % (post_p_s,total_count))

def findDetectionRateForThresholdRange(seed:int=69,
                                       sample_count:  int   = None,
                                       biased_target: str   = None,
                                       biased_factor: float = None,
                                       img_diff_range=(x for x in range(0, 21, 2)),
                                       text_sim_range=(x/10 for x in range(0, 10)),
                                       save_to_file:str=None,
                                       verbose:bool=True):

    print('processing detection rate through a range of thresholds.')
    print('note: this should utilise at most 90% of cpu power.')
    names = _poolRepostChecker.getImagesSample(sample_count=sample_count,
                                               seed=seed)

    if biased_factor is None:
        names = _poolRepostChecker.getImagesSample(sample_count=sample_count,
                                                   seed=seed)
    else:
        names = _poolRepostChecker.getBiasedImagesSample(biased_target=biased_target,
                                                         biased_factor=biased_factor,
                                                         sample_count=sample_count,
                                                         seed=seed)
    args_list = []
    counter = 0
    print('processing items with the following ranges')
    img_diff_range = list(img_diff_range)
    text_sim_range = list(text_sim_range)
    print('img_diffs: ' + str(img_diff_range))
    print('text_sims: ' + str(text_sim_range))
    for i in list(img_diff_range):
        for t in list(text_sim_range):
            counter += 1
            args_list.append((counter, names, i, t, verbose))

    print('elements to process per threshold: %d' % len(names))
    print('threshold pairs to process       : %d' % len(args_list))
    print()

    pool = Pool(max(int(cpu_count()*0.9), 1))
    results = pool.map(_helperFindDetectionRateFromThresholds, args_list)
    pool.close()
    pool.join()

    print()
    print('tallying up and sorting results')
    results.sort(key=lambda x: (x['img_diff_min'], x['text_sim_min']))

    output = {'sample_count': sample_count, 'data': results}

    if save_to_file:
        print('saving to file (%s)...' % save_to_file)
        with open(str(save_to_file), 'w') as f:
            json.dump(output, f, indent=4)

    print('done!')
    return output
