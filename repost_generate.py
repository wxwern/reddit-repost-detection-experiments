#!/usr/bin/env python3

from repost.repost_checker import RepostChecker
from repost import repost_multiprocessing as poolRepostChecker

if __name__ == "__main__":
    print("type directory name or path of scraper_cache:")
    dirn = input()
    print("generateing reposts in " + dirn)
    repostChecker = RepostChecker(dirn)
    repostChecker.readProcessedDataFromCache()
    print('type number of reposts to generate per post:')
    repostChecker.generateRepostsForAll(count_per_post=int(input()))
    print('done!')




