#!/usr/bin/env python3
import json
import copy
import os
from matplotlib import pyplot as plt

print('input computed graph json folder for generating graphs.')
print('all files will be generated in the same folder as the jsons folder.')
print('graphs generated will compare potential peak performance with ocr vs no-ocr.')
ds = []

def format_name(name):
    try:
        x = name.split("_")
        if x[1].split("/")[1] == "graph" and x[3].endswith(".json") and len(x) == 4:
            return x[1].split("/")[0] + "_" + x[2]
    except:
        pass
    return name

print('directory:')
dr = input().strip()
fls = os.listdir(dr)
for f in fls:
    if not f.startswith('graph') or not f.endswith('.json'):
        continue

    ipath = os.path.join(dr, f)

    print('loading %s...' % ipath, end='')
    with open(ipath, encoding='utf8') as f:
        jd1 = json.load(f)
        jd2 = copy.deepcopy(jd1)
        jd1["data"] = list(filter(lambda x: x["text_sim_min"] == 0.0, jd1["data"]))
        ds = [jd1, jd2]
    labels = [format_name(ipath) + " (w/o ocr)", format_name(ipath) + " (w/ ocr)"]

    fig = plt.figure()
    plt.xlabel('precision')
    plt.ylabel('recall')
    plt.grid()
    axes = plt.gca()
    axes.set_xlim([0.0,1.0])
    axes.set_ylim([0.0,1.0])
    ax = plt.subplot(111)

    for i, d in enumerate(ds):
        full_list = []
        filtered_list = []

        img_range = list(set(map(lambda x: x['img_sim_min'], d['data'])))
        img_range.sort()
        for m in img_range:
            def formatter(x):
                try:
                    return (x['results']['precision'], \
                            x['results']['recall'], \
                            x['img_sim_min'], \
                            x['text_sim_min'], \
                            x['results']['f1_score'])
                except KeyError:
                    return (0,0,x['img_sim_min'],x['text_sim_min'],0)

            points = list(map(formatter, \
                              sorted(
                                  list( \
                                       filter(lambda x: x['img_sim_min'] == m, d['data']) \
                                       ), \
                                  key=lambda x: x['text_sim_min']
                              )
                              )
                          )
            full_list += points


        def get_imgtxtsim_precrec(x):
            return ((x[2], x[3]), (x[0], x[1]))

        def guaranteed_better_than(a,b):
            a = get_imgtxtsim_precrec(a)
            b = get_imgtxtsim_precrec(b)
            return a[1][0] > b[1][0] and a[1][1] > b[1][1]

        for x in full_list:
            if len(list(filter(lambda y: guaranteed_better_than(y,x), full_list))) == 0:
                filtered_list.append(x)

        filtered_list = sorted(list(set(filtered_list)), key=lambda x: (get_imgtxtsim_precrec(x)[1][0], -get_imgtxtsim_precrec(x)[1][1]))

        _prevxis = -1
        x_vals = []
        y_vals = []
        for x in filtered_list:
            _x = get_imgtxtsim_precrec(x)
            x_vals.append(_x[1][0])
            y_vals.append(_x[1][1])
        ax.plot(x_vals, y_vals, \
                label=labels[i], \
                marker=['x','+'][i%2], \
                markeredgewidth=2, \
                markersize=max(8-2*(i//2),4))

        full_list.sort(key=lambda x: (x[-1], x[0]), reverse=True)

    ax.legend(ncol=1, loc='lower left')

    ipath = ipath.replace('.json', '.png')
    print('\rsaving  %s... ' % ipath, end='')
    fig.savefig(ipath)
    print('\rsaved   %s    ' % ipath)
    plt.close(fig)

