#!/usr/bin/env python3

import json
import random
from difflib import SequenceMatcher
from os import listdir
from os.path import isfile, join
from PIL import Image, UnidentifiedImageError
from ocr import OCR
from hasher import Hasher
try:
    from repost_maker import generate_bad_repost
except ImportError:
    from .repost_maker import generate_bad_repost

class RepostChecker:
    '''
    helper class to check reposts using all available modules

    variables that can be modified:
    - verbose      : Boolean value indicating whether verbose output is printed.
    - use_cache    : Boolean value indicating whether to read from cache if possible.
    - update_cache : Boolean value indicating whether to update the cache.
    '''

    def __init__(self, img_dir: str, imagehash_method = 'dHash'):
        '''
        Initialises the repost checker using the given image directory and image hashing method

        Parameters:
        - img_dir          : A string representing the location to read post images from. Also saves it's resulting cache data there.
        - imagehash_method : The method for hashing the image. A Hasher.ImageHashMethod enum value or its raw value string is accepted.
        '''
        self.verbose = True
        self.__imagehash_method = imagehash_method
        self.img_dir = img_dir
        self.__cache_json_path = join(img_dir, '__repost_check_data__.json')
        self.use_cache = True
        self.update_cache = True
        self.__imageToHash = {}
        self.__imageToText = {}

    def vPrint(self,x=''):
        if self.verbose:
            print(x)

    def readProcessedDataFromCache(self):
        try:
            if self.use_cache:
                with open(self.__cache_json_path, 'r', encoding='utf-8') as json_data:
                    x = json.load(json_data)
                    if 'image_to_hash' in x:
                        self.__imageToHash = x['image_to_hash']
                    if 'image_to_text' in x:
                        self.__imageToText = x['image_to_text']
                    if 'image_to_text_hash' in x:
                        self.__imageToTextHash = x['image_to_text_hash']
        except FileNotFoundError:
            pass

    def saveProcessedDataToCache(self):
        if self.update_cache:
            output = {'image_to_hash': self.__imageToHash, 'image_to_text': self.__imageToText}
            with open(self.__cache_json_path, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=4, ensure_ascii=False)

    def getCacheJsonPath(self):
        return self.__cache_json_path

    def setJsonCacheFilenmaeTarget(self, filename='__repost_check_data__.json'):
        self.__cache_json_path = join(self.img_dir, filename)

    def processData(self, only_cached_files=False, max_capacity=None):
        '''
        Processes all posts and returns two dictionaries in a tuple.
        The first maps image name to hash, and
        the second maps image name to OCR results.

        The results will also be cached in memory within the class and
        will be used in other methods for checking reposts

        Returns:
        A tuple of two dictionaries, first one containing image name to hash mappings
        and second one containing image name to OCR readings.
        '''

        if not only_cached_files:
            files = [f for f in listdir(self.img_dir) if isfile(join(self.img_dir, f)) and not f.startswith('.')]
            files.sort()
            self.readProcessedDataFromCache()
        else:
            self.readProcessedDataFromCache()
            files = list(self.__imageToHash.keys())
            files.sort()

        if max_capacity is not None:
            files = files[:max_capacity]

        d = self.__imageToHash
        t = self.__imageToText

        self.vPrint("loading... " + str(len(files)) + ' items')
        for i, file in enumerate(files):
            if len(files) < 50 or i % (len(files)//20) == 0:
                self.vPrint('partial: %5d/%d' % (i,len(files)))

            try:
                if file not in d or file not in t:
                    img = Image.open(join(self.img_dir, file))
                    d[file] = Hasher.hashImage(img, self.__imagehash_method)
                    t[file] = OCR.read2Normalized(img)
            except KeyboardInterrupt:
                self.vPrint('skipped remaining files')
                if file in d:
                    del d[file]
                if file in t:
                    del t[file]
                break
            except UnidentifiedImageError:
                self.vPrint('skipped ' + file + ' (not an image)')
                if file in d:
                    del d[file]
                if file in t:
                    del t[file]

        self.vPrint('loaded: ' + str(len(d.items())) + ' items')
        self.__imageToHash = d
        self.__imageToText = t
        self.saveProcessedDataToCache()
        return (d,t)


    def checkRepostDetection(self,
                             img: str,
                             img_sim_min: int = 0.8,
                             text_sim_min: float = 0.7,
                             recheck_img: bool = True,
                             generate_repost: bool = False,
                             save_generated_repost: bool = True):
        '''
        Checks whether reposts can be detected correctly using
        a naive algorithm considering image hashes and ocr text.

        This assumes the dataset is correctly labelled such that
        a reposted image is the image name prefixed with _REPOST_.

        If an image is custom crafted and you don't want it to
        make a deduction of whether it's a true positive or otherwise,
        simply avoid using the standard format name of:
            <subreddit>_<postID>.<imgExtension>
        '''
        distances = []
        name_dist_dict = {}
        d = self.__imageToHash
        t = self.__imageToText

        target_check = img
        target_path = join(self.img_dir, target_check)
        target_img = None
        self.vPrint('we\'ll process post : ' + target_check)
        if generate_repost or recheck_img:
            target_img = Image.open(target_path)
        if target_img and (recheck_img or target_check not in d or target_check not in t):
            self.vPrint('computing target metadata')
            target_hash = Hasher.hashImage(target_img, self.__imagehash_method)
            target_text = OCR.read2Normalized(target_img)
            target_texthash = Hasher.hashText(target_text)
            d[target_check] = target_hash
            t[target_check] = target_text
            self.__imageToHash = d
            self.__imageToText = t
        else:
            target_hash = d[target_check]
            target_text = t[target_check]


        bad_check = '_REPOST_' + target_check
        if generate_repost:
            self.vPrint('generating dummy repost : _REPOST_' + target_check)
            bad_img = generate_bad_repost(target_path)
            bad_img_path = join(self.img_dir, bad_check)
            self.vPrint('computing target metadata')
            bad_img_hash = Hasher.hashImage(bad_img, self.__imagehash_method)
            bad_img_text = OCR.read2Normalized(bad_img)
            bad_img_texthash = Hasher.hashText(bad_img_text)
            d[bad_check] = bad_img_hash
            t[bad_check] = bad_img_text
            if save_generated_repost:
                bad_img.save(bad_img_path)
                self.__imageToHash = d
                self.__imageToText = t

        if self.update_cache:
            self.saveProcessedDataToCache()


        self.vPrint('\nchecking...')

        for key, value in d.items():
            if key == target_check:
                continue
            img_diff = Hasher.diff(value, target_hash, 'IMAGE')
            text_sim = 1
            distances.append \
                    ( \
                     (key, \
                      img_diff, \
                      text_sim)
                     )
            name_dist_dict[key] = (distances[-1][1], distances[-1][2])


        def orderOfSort(x):
            '''dynamic sorting to prioritise text if image and text are both really close'''
            img_diff = x[1]
            txt_diff = 1-x[2]
            if txt_diff <= 1-text_sim_min and img_diff <= 1-img_sim_min:
                return (txt_diff-1, img_diff-1)
            return (img_diff, txt_diff)

        distances.sort(key=orderOfSort)
        counter = 0

        results = {}
        FP = 0
        FN = 0


        self.vPrint('--- similar results ---')
        self.vPrint('  SAME?  | IMG_SIM | TEXT_SIM | IMAGE')
        for a,b,c in distances:
            standardFormat = len(a.split('.')) == 2 and len(a.split('.')[0].split('_REPOST_')[-1].split('_')) == 2
            is_known_same = a.split('_REPOST_')[-1] == target_check.split('_REPOST_')[-1]
            is_repost = b <= 1-img_sim_min and c >= text_sim_min
            if not standardFormat:
                validity = '??'
            else:
                if is_known_same:
                    if is_repost:
                        validity = 'TP'
                    else:
                        validity = 'FN'
                        FN += 1
                else:
                    if is_repost:
                        validity = 'FP'
                        FP += 1
                    else:
                        validity = 'TN'

            if counter < 10:
                counter += 1
                if self.verbose:
                    self.vPrint('%8s   %7.3f   %8.3f    %-50s' % \
                                (('YES, ' if is_repost else ' NO, ') + validity,1-b,c,a))

                    if standardFormat:
                        subreddit = a.split('_REPOST_')[-1].split('_')[0]
                        post_id   = a.split('_REPOST_')[-1].split('_')[-1].split('.')[0]
                        self.vPrint('reddit.com/r/' + subreddit + '/comments/' + post_id + '/')
                    else:
                        self.vPrint('• this image isn\'t from the standard dataset')

                    if a == target_check:
                        self.vPrint('• this is the originally chosen image')
                    elif is_known_same:
                        self.vPrint('• this is a known to be the same as the chosen image')
                    self.vPrint()

            results[a] = {
                'imgName': a,
                'isRepost': is_repost,
                'validity': validity,
                'imgDiff': b,
                'textSim': c
            }

        if FP or FN:
            self.vPrint('important notes:')
            self.vPrint('we have %d known false positives and %d known false negatives for this\n' % (FP, FN))

        return results

    def listRepostsOf(self, img: str):
        '''lists detected reposts for the given image name in the image directory'''
        detection = self.checkRepostDetection(img, generate_repost=False)
        data = []
        for key, value in detection.items():
            if value['isRepost'] and key != img:
                data.append(key)
        return data

    def generateRepostsForAll(self, count_per_post=1, res=None, rot=None, asp=None, crop=None, uid=None):
        '''generates reposts for every single non repost image in the image directory'''
        names = list(filter(lambda x: '_REPOST_' not in x, self.__imageToHash.keys()))
        self.vPrint('generating ' + str(len(names)) + ' reposts')
        interrupted = False
        try:
            for i, name in enumerate(names):
                repname = (str(uid) if uid else '') + '_REPOST_' + name
                if count_per_post == 1:
                    if repname in self.__imageToHash and repname in self.__imageToText:
                        continue
                elif count_per_post > 1:
                    if (str(count_per_post - 1) + repname) in self.__imageToHash and \
                       (str(count_per_post - 1) + repname) in self.__imageToText:
                        continue
                else:
                    return

                if i < 30 or i % 10 == 0:
                    self.vPrint('partial: %5d/%d' % (i,len(names)))

                try:
                    target_path = join(self.img_dir, name)
                    loc = join(self.img_dir, repname)
                    bad_imgs = generate_bad_repost(target_path,
                                                   count=(count_per_post),
                                                   res=res,
                                                   rot=rot,
                                                   asp=asp,
                                                   crop=crop,
                                                   save_loc=loc)
                    if not isinstance(bad_imgs, list):
                        bad_imgs = [(repname, bad_imgs)]

                    for newrepname, bad_img in bad_imgs:
                        bad_img_hash = Hasher.hashImage(bad_img, self.__imagehash_method)
                        bad_img_text = OCR.read2Normalized(bad_img)
                        self.__imageToHash[newrepname] = bad_img_hash
                        self.__imageToText[newrepname] = bad_img_text
                except FileNotFoundError as e:
                    print(e)
                    print("skipped an image that doesn't exist")
                    continue
                except UnidentifiedImageError as e:
                    print(e)
                    print('skipped an unidentified image')
                    continue

            self.vPrint('done!')
        except KeyboardInterrupt:
            self.vPrint('interrupted!')
            interrupted=True
        finally:
            self.saveProcessedDataToCache()
            self.vPrint('saved!')
        return not interrupted

    def getImagesSample(self,
                        imgs_list: list = None,
                        sample_count: int = None,
                        seed: int = None):
        '''
        Returns a subsample of sample_count standard images using the seed (if given) from the list (or the list of images loaded in this class if not provided)
        '''
        names = imgs_list if imgs_list else list(self.__imageToHash.keys())
        names =       (list(filter(lambda x: \
                                   len(x.split('_REPOST_')[-1].split('_')) == 2 and \
                                   len(x.split('_REPOST_')[-1].split('_')[1].split('.')) == 2,
                                   names)))
        if seed:
            random.seed(seed)
        total = min(len(names), sample_count) if sample_count else len(names)
        names = random.sample(names, total)
        return names

    def getBiasedImagesSample(self,
                              imgs_list: list = None,
                              biased_target: str = None,
                              biased_factor: float = 0.5,
                              sample_count: int = None,
                              seed: int = None):
        '''
        Returns a biased subsample towards biased_target with a factor of biased_factor, of sample_count standard images using the seed (if given), from the list (or the list of images loaded in this class if not provided)
        '''
        unfiltered_names = imgs_list if imgs_list else list(self.__imageToHash.keys())
        unfiltered_names =       (list(filter(lambda x: \
                                              len(x.split('_REPOST_')[-1].split('_')) == 2 and \
                                              len(x.split('_REPOST_')[-1].split('_')[1].split('.')) == 2,
                                              unfiltered_names)))

        if unfiltered_names == []:
            return unfiltered_names

        if seed:
            random.seed(seed)
        names = list(filter(lambda x: '_REPOST_' not in x, unfiltered_names))

        target_name = biased_target if biased_target else random.choice(names)
        target_repost_samples = list(filter(lambda x: target_name in x and target_name != x, unfiltered_names))

        print('---')
        print(target_name)
        print(target_repost_samples)
        print('---')

        total = min(len(names), sample_count) if sample_count else len(names)
        repost_total = min(int(total*biased_factor), len(target_repost_samples))

        random_unique_samples = random.sample(names, total - repost_total)
        random_repost_samples = random.sample(target_repost_samples, repost_total)

        samples = random_repost_samples + random_unique_samples
        return samples


    def findDetectionRate(self,
                          imgs_list: list = None,
                          sample_count: int = None,
                          seed: int = 69,
                          img_sim_min: int = 15,
                          text_sim_min: float = 0.7):
        '''finds the repost detection rate (precision, recall, true/false positives/negatives) given the parameters'''

        vC = {'TP':0,'FP':0,'TN':0,'FN':0,'??':0}
        names = self.getImagesSample(imgs_list=imgs_list,
                                     sample_count=sample_count,
                                     seed=seed)

        interrupted = False
        v = self.verbose
        self.verbose = False
        c = self.update_cache
        self.update_cache = False

        try:
            for i, img in enumerate(names):
                if sample_count and i >= sample_count:
                    break
                res = self.checkRepostDetection(img, img_sim_min=img_sim_min, text_sim_min=text_sim_min, recheck_img=False, generate_repost=False)
                for _, data in res.items():
                    vC[data['validity']] += 1
                if v:
                    try:
                        precision = round(vC['TP']/(vC['TP'] + vC['FP'])*100, 1)
                        recall    = round(vC['TP']/(vC['TP'] + vC['FN'])*100, 1)
                    except ZeroDivisionError:
                        precision = 0
                        recall    = 0
                    print('\n[%5d/%-5d] %s' % \
                          (i+1, len(names), img))
                    print('  ~> (precision: %5.1f%%, recall: %5.1f%%) %s' % \
                          (precision, recall, str(vC)))
        except KeyboardInterrupt:
            interrupted = True
            if v:
                print('keyboard interrupt received, skipping remaining tests')
        finally:
            self.verbose = v
            self.update_cache = c
            self.saveProcessedDataToCache()

        if v:
            print()
            if sample_count or interrupted:
                print('-- results (sample count) --')
            else:
                print('-- results --')
        try:
            precision = round(vC['TP']/(vC['TP'] + vC['FP']),5)
            recall    = round(vC['TP']/(vC['TP'] + vC['FN']),5)
            accuracy  = round((vC['TP'] + vC['TN'])/(vC['TP'] + vC['TN'] + vC['FP'] + vC['FN']),5)
            f1_score  = round(2*vC['TP']/(2*vC['TP'] + vC['FP'] + vC['FN']), 5)

            if v:
                print('precision : %4.3f%%' % (precision*100))
                print('recall    : %4.3f%%' % (recall*100))
                print('accuracy  : %4.3f%%' % (accuracy*100))
                print('f1_score  : %4.3f%%' % (f1_score*100))

            vC['precision'] = round(precision, 8)
            vC['recall']    = round(recall, 8)
            vC['accuracy']  = round(accuracy, 8)
            vC['f1_score']  = round(f1_score, 8)

        except ZeroDivisionError:
            if v:
                print('cannot compute other metrics due to division by zero')

        if v:
            print('stats     : %s' % str(vC))
            print()

        return vC

    def findDetectionRateForThresholdRange(self,
                                           seed:int=69,
                                           sample_count:int=None,
                                           img_sim_range=(0.7+x*0.3/10 for x in range(0, 10)),
                                           text_sim_range=(x/10 for x in range(0, 10)),
                                           save_to_file:str=None):
        data = []

        self.vPrint('')
        v = self.verbose
        self.verbose = False
        c = self.update_cache
        self.update_cache = False

        for i in img_sim_range:
            for t in text_sim_range:
                if v:
                    print('processing img_sim_min %d text_sim_min %.2f' % \
                          (i, t))
                res = self.findDetectionRate(sample_count=sample_count,
                                             seed=seed,
                                             img_sim_min=i,
                                             text_sim_min=t)

                d = {'img_sim_min': i, 'text_sim_min': t, 'results': res}
                if v:
                    print('completed img_sim_min %d text_sim_min %.2f' % \
                          (i, t))
                    print(json.dumps(d, indent=4))
                data.append(d)

        self.verbose = v
        self.update_cache = c

        output = {'sample_count': sample_count, 'data': data}

        if save_to_file:
            if v:
                print('saving to file (%s)...' % save_to_file)
            with open(str(save_to_file), 'w') as f:
                json.dump(output, f, indent=4)

        if v:
            print('done!')

        return output
