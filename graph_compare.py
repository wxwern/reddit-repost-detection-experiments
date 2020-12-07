#!/usr/bin/env python3
import json
from matplotlib import pyplot as plt
import numpy as np

print('input computed graph json file names (empty line to compare graphs):')
ds = []
labels = [] 
while True:
    d = {}
    i = input()
    if i == "":
        break
    with open(i, encoding='utf8') as f:
        jd = json.load(f)
        if 'sample_count' not in d or jd['sample_count'] == d['sample_count']:
            if not d:
                d = jd
            else:
                d['data'] += jd['data']
        else:
            print('error: sample count mismatch')
            continue
    labels.append(i)
    ds.append(d)

plt.xlabel('precision')
plt.ylabel('recall')
plt.grid()
axes = plt.gca()
axes.set_xlim([0.0,1.0])
axes.set_ylim([0.0,1.0])
ax = plt.subplot(111)

def format_name(name):
    try:
        x = name.split("_")
        if x[1].split("/")[1] == "graph" and x[3].endswith(".json") and len(x) == 4:
            return x[1].split("/")[0] + "_" + x[2]
    except:
        pass
    return name


for i, d in enumerate(ds):
    full_list = []
    filtered_list = []

    print('extracting points..')
    img_range = list(set(map(lambda x: x['img_sim_min'], d['data'])))
    img_range.sort()
    for m in img_range:
        points = list(map(lambda x: \
                          (x['results']['precision'], x['results']['recall'], x['img_sim_min'], x['text_sim_min'], x['results']['f1_score']), \
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

    print('computing outer points to highlight...')
    for x in full_list:
        if len(list(filter(lambda y: guaranteed_better_than(y,x), full_list))) == 0:
            filtered_list.append(x)

    print(len(full_list))
    print(len(filtered_list))

    filtered_list = sorted(list(set(filtered_list)), key=lambda x: (get_imgtxtsim_precrec(x)[1][0], -get_imgtxtsim_precrec(x)[1][1]))

    print('drawing points...')
    _prevxis = -1
    x_vals = []
    y_vals = []
    for x in filtered_list:
        _x = get_imgtxtsim_precrec(x)
        x_vals.append(_x[1][0])
        y_vals.append(_x[1][1])
    ax.plot(x_vals, y_vals, label=format_name(labels[i]))

    full_list.sort(key=lambda x: (x[-1], x[0]), reverse=True)
    print()
    print("%d. most feasible points:" % i)
    for x in full_list[0:3]:
        print("img_sim_min: %.3f, text_sim_min: %.3f" % get_imgtxtsim_precrec(x)[0])
        print("precision: %.4f, recall: %.4f" % get_imgtxtsim_precrec(x)[1])
        print("f1_score: %.4f" % x[4])
        print("---")

ax.legend(ncol=1)
plt.show()


