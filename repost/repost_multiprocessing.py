#!/usr/bin/env python3

try:
    from repost_checker import RepostChecker
except ImportError:
    from .repost_checker import RepostChecker
from multiprocessing import Pool
import json

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
    print('process : item %-5d i.e. %s' % (i, img))
    res = _poolRepostChecker.findDetectionRate(imgs_list=[img],
                                               img_diff_min=idm,
                                               text_sim_min=tsm)
    print('finished: item %-5d i.e. %s' % (i, img))
    return res

def _helperFindDetectionRateFromThresholds(args):
    i = args[0]
    imgl = args[1]
    idm = args[2]
    tsm = args[3]
    print('process : pair %-4d i.e. idm %4d tsm %4.3f' % (i, idm, tsm))
    res = _poolRepostChecker.findDetectionRate(imgs_list=imgl, img_diff_min=idm, text_sim_min=tsm)
    d = {'img_diff_min': idm, 'text_sim_min': tsm, 'results': res}
    print('finished: pair %-4d i.e. idm %4d tsm %4.3f -> %s' % (i, idm, tsm, res))
    return d

def findDetectionRate(imgs_list: list = None,
                      seed: int = 69,
                      biased_target: str = None,
                      biased_factor: float = None,
                      sample_count: int = None,
                      img_diff_min: int = 15,
                      text_sim_min: float = 0.7):

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
    print('note: this will utilise 100% of every cpu core you have.')
    print('elements to process: %d' % len(names))

    args_list = list(map(lambda x: [0, x, img_diff_min, text_sim_min], names))
    for i, _ in enumerate(args_list):
        args_list[i][0] = i + 1

    pool = Pool()
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

    precision = round(vC['TP']/(vC['TP'] + vC['FP']),5)
    recall    = round(vC['TP']/(vC['TP'] + vC['FN']),5)
    accuracy  = round((vC['TP'] + vC['TN'])/(vC['TP'] + vC['TN'] + vC['FP'] + vC['FN']),5)
    f1_score  = round(2*vC['TP']/(2*vC['TP'] + vC['FP'] + vC['FN']), 5)

    print()
    if sample_count:
        print('-- results (sample count) --')
    else:
        print('-- results --')
    print('precision : %4.3f%%' % (precision*100))
    print('recall    : %4.3f%%' % (recall*100))
    print('accuracy  : %4.3f%%' % (accuracy*100))
    print('f1_score  : %4.3f%%' % (f1_score*100))
    print('stats     : %s' % str(vC))
    print()

    vC['precision'] = round(precision, 8)
    vC['recall']    = round(recall, 8)
    vC['accuracy']  = round(accuracy, 8)
    vC['f1_score']  = round(f1_score, 8)

    return vC

def findDetectionRateForThresholdRange(seed:int=69,
                                       sample_count:  int   = None,
                                       biased_target: str   = None,
                                       biased_factor: float = None,
                                       img_diff_range=(x for x in range(0, 21, 2)),
                                       text_sim_range=(x/10 for x in range(0, 10)),
                                       save_to_file:str=None):

    print('processing detection rate through a range of thresholds.')
    print('note: this will utilise 100% of every cpu core you have.')
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
            args_list.append((counter, names, i, t))

    print('elements to process per threshold: %d' % len(names))
    print('threshold pairs to process       : %d' % len(args_list))
    print()

    pool = Pool()
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
