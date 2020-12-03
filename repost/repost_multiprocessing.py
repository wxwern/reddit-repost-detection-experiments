#!/usr/bin/env python3

try:
    from repost_checker import RepostChecker
except ImportError:
    from .repost_checker import RepostChecker
from multiprocessing import Pool, cpu_count
import json
import time

#_poolRepostChecker = RepostChecker('scraper_cache')
#_poolRepostChecker.verbose = False
#_poolRepostChecker.update_cache = False
#_poolRepostChecker.readProcessedDataFromCache()

def configurePoolRepostChecker(img_dir: str, json_filename='__repost_check_data__.json'):
    global _poolRepostChecker
    _poolRepostChecker = RepostChecker(img_dir)
    _poolRepostChecker.verbose = False
    _poolRepostChecker.update_cache = False
    _poolRepostChecker.setJsonCacheFilenmaeTarget(filename=json_filename)
    _poolRepostChecker.readProcessedDataFromCache()
    #return _poolRepostChecker

def _helperFindDetectionRateFromImage(args):
    i = args[1]
    img = args[2]
    idm = args[3]
    tsm = args[4]
    _VERBOSE = args[5]
    if _VERBOSE:
        print('process : item %-5d i.e. %s' % (i, img))
    res = args[0].findDetectionRate(imgs_list=[img],
                                               img_sim_min=idm,
                                               text_sim_min=tsm)
    if _VERBOSE:
        print('finished: item %-5d i.e. %s' % (i, img))
    return res

def _helperFindDetectionRateFromThresholds(args):
    i = args[1]
    imgl = args[2]
    idm = args[3]
    tsm = args[4]
    _VERBOSE = args[5]
    if _VERBOSE:
        print('process : pair %-4d i.e. ism %4.3f tsm %4.3f' % (i, idm, tsm))
    res = args[0].findDetectionRate(imgs_list=imgl, img_sim_min=idm, text_sim_min=tsm)
    d = {'img_sim_min': idm, 'text_sim_min': tsm, 'results': res}
    if _VERBOSE:
        print('finished: pair %-4d i.e. ism %4.3f tsm %4.3f -> %s' % (i, idm, tsm, res))
    return d

def findDetectionRate(imgs_list: list = None,
                      seed: int = 69,
                      biased_target: str = None,
                      biased_factor: float = None,
                      sample_count: int = None,
                      img_sim_min: int = 0.8,
                      text_sim_min: float = 0.6,
                      cpu_threshold: float = 0.9,
                      verbose: bool = True):
    try:
        _poolRepostChecker
    except NameError:
        print("Pool Repost Checker is not yet configured.")
        print("run configurePoolRepostChecker to do so.")
        return None

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
    print('note: this should utilise at most %d%% of cpu power.' % int(cpu_threshold*100))
    print('elements to process: %d' % len(names))

    args_list = list(map(lambda x: [_poolRepostChecker, 0, x, img_sim_min, text_sim_min, verbose], names))
    for i, _ in enumerate(args_list):
        args_list[i][1] = i + 1

    pool = Pool(max(int(cpu_count()*cpu_threshold), 1))
    results = []
    for i, x in enumerate(pool.imap_unordered(_helperFindDetectionRateFromImage, args_list), 1):
        print("[%6.2f%% complete]" % (i/len(args_list)*100))
        results.append(x)
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
    print('\a')

    return vC

def benchmark(sample_count=200):
    print('testing repost detection processing speed...')
    print('-'*30)
    ini = time.time()
    findDetectionRate(sample_count=sample_count, img_sim_min=10, text_sim_min=0.1, verbose=False)
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
                                       img_sim_range  = list((0.7 + x/40) for x in range(0, 12)),
                                       text_sim_range = list(x/10 for x in range(0, 10)),
                                       save_to_file:str = None,
                                       cpu_threshold:float = 0.9,
                                       verbose:bool = True):

    try:
        _poolRepostChecker
    except NameError:
        print("Pool Repost Checker is not yet configured.")
        print("run configurePoolRepostChecker to do so.")
        return None

    print('processing detection rate through a range of thresholds.')
    print('note: this should utilise at most %d%% of cpu power.' % int(cpu_threshold*100))
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
    img_sim_range = list(img_sim_range)
    text_sim_range = list(text_sim_range)
    print('img_diffs: ' + str(img_sim_range))
    print('text_sims: ' + str(text_sim_range))
    for i in list(img_sim_range):
        for t in list(text_sim_range):
            counter += 1
            args_list.append((_poolRepostChecker, counter, names, i, t, verbose))

    print('elements to process per threshold: %d' % len(names))
    print('threshold pairs to process       : %d' % len(args_list))
    print()

    pool = Pool(max(int(cpu_count()*cpu_threshold), 1))
    results = []
    for i, e in enumerate(pool.imap_unordered(_helperFindDetectionRateFromThresholds, args_list), 1):
        print("[%6.2f%% complete]" % (i/len(args_list)*100))
        results.append(e)
    pool.close()
    pool.join()

    print()
    print('tallying up and sorting results')
    results.sort(key=lambda x: (x['img_sim_min'], x['text_sim_min']))

    output = {'sample_count': sample_count, 'data': results}

    if save_to_file:
        print('saving to file (%s)...' % save_to_file)
        with open(str(save_to_file), 'w') as f:
            json.dump(output, f, indent=4)

    print('done!\a')
    return output
