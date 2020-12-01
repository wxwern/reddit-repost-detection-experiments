#!/usr/bin/env python3

from repost.repost_checker import RepostChecker

if __name__ == "__main__":
    print("type directory name or path of scraper_cache:")
    dirn = input()
    print("generating reposts in " + dirn + " using preprocessed post list")
    repostChecker = RepostChecker(dirn)
    repostChecker.readProcessedDataFromCache()
    print('type number of reposts to generate per post:')
    no=input()

    print('use random generation? (y/n)')
    if input().lower() == 'y':
        repostChecker.generateRepostsForAll(count_per_post=int(input()))
    else:
        print('resize factor (input value):')
        res=float(input())
        print('rotation deg (input value):')
        rot=float(input())
        print('aspect ratio adjust factor (input value):')
        asp=float(input())
        print('crop factor (L,T,R,B) (input 4 space-separated values):')
        crop=tuple(map(float,input().split(' ')))

        repostChecker.generateRepostsForAll(count_per_post=int(input()),
                                            res=res,
                                            rot=rot,
                                            asp=asp,
                                            crop=crop)
    print('done!\a')




