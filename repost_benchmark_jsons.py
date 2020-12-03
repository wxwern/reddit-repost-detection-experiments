#!/usr/bin/env python3

import os
from repost.repost_checker import RepostChecker
from repost import repost_multiprocessing as poolRepostChecker

if __name__ == "__main__":
    print()
    print('repost benchmarking folder:')
    dir_name = input().strip()
    files = os.listdir(dir_name)

    print()
    print(' [seed number] ', end='')
    seed = int(input())
    print(' [sample count] ', end='')
    sample_c = int(input())
    print()
    print(' [minimum image sim, fraction] ', end='')
    minv = float(input())
    print(' [maximum image sim, fraction] ', end='')
    maxv = float(input())
    img_sim_values = list(filter(lambda x: minv <= x <= maxv, [x/40 for x in range(1, 40)]))
    print('> ', end='')
    print(img_sim_values)
    print()
    print(' [minimum text sim, fraction] ', end='')
    minv = float(input())
    print(' [maximum text sim, fraction] ', end='')
    maxv = float(input())
    text_sim_values = list(filter(lambda x: minv <= x <= maxv, [x/10 for x in range(0, 10)]))
    print('> ', end='')
    print(text_sim_values)
    print()
    print(' [cpu usage max limit, fraction] ', end='')
    cpu_limit = max(0.0,min(1.0, float(input())))
    print()

    for file in files:
        if not file.startswith('_'):
            continue
        if file == "__repost_check_data__.json":
            print("warning: default repost json ignored")
            continue
        if ("graph" + file) in files:
            print("warning: already processed repost json ignored")
            continue

        print("will be processing: " + file)
        save_loc = os.path.join(dir_name, "graph" + file)
        print("target save location: " + save_loc)
        poolRepostChecker.configurePoolRepostChecker(dir_name, json_filename=file)

        print('starting in a few seconds... (ctrl-c to cancel)')
        try:
            import time
            time.sleep(5)
        except KeyboardInterrupt:
            import sys
            sys.exit()

        res = poolRepostChecker.findDetectionRateForThresholdRange(seed=seed,
                                                                   sample_count=sample_c,
                                                                   img_sim_range=img_sim_values,
                                                                   text_sim_range=text_sim_values,                                                                                       save_to_file=save_loc,
                                                                   cpu_threshold=cpu_limit)
        print("done!")
    print("completed processing for all tasks!\a")




