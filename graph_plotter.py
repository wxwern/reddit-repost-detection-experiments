#!/usr/bin/env python3
import json
from matplotlib import pyplot as plt
import numpy as np

print('input computed graph json file names (empty line to graph):')
d = {}
ipath = ""
while True:
    i = input()
    if i == "":
        break
    ipath = i
    with open(i, encoding='utf8') as f:
        x = json.load(f)
        if 'sample_count' not in d or x['sample_count'] == d['sample_count']:
            if not d:
                d = x
            else:
                d['data'] += x['data']
        else:
            print('error: sample count mismatch')


print("select graph mode: (0-3)")
mode = int(input())

fig = plt.figure()

plt.xlabel('precision')
plt.ylabel('recall')
plt.grid()
axes = plt.gca()
axes.set_xlim([0.0,1.0])
axes.set_ylim([0.0,1.0])

full_list = []
set_list = []
filtered_list = []

print('extracting points..')
if mode == 2:
    txt_range = list(set(map(lambda x: x['text_sim_min'], d['data'])))
    txt_range.sort()
    for m in txt_range:

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
                                   filter(lambda x: x['text_sim_min'] == m, d['data']) \
                                   ), \
                              key=lambda x: x['img_sim_min']
                          )
                          )
                      )

        full_list += points
        set_list.append(points)
else:
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
        if mode != 1:
            set_list.extend(list(map(lambda x: [x], points)))
        else:
            set_list.append(points)


def get_imgtxtsim_precrec(x):
    return ((x[2], x[3]), (x[0], x[1]))

def guaranteed_better_than(a,b):
    a = get_imgtxtsim_precrec(a)
    b = get_imgtxtsim_precrec(b)
    return (a[1][0] >= b[1][0] and a[1][1] >= b[1][1]) and a[1] != b[1]

def compute_color(x):
    i_sim,t_sim = get_imgtxtsim_precrec(x)[0]
    arr = [max(min(1.0,(i_sim-0.6)*2.5),0.0)*0.75,
           0 if x not in filtered_list else 0.75,
           max(min(1.0,t_sim),0.0)*0.75, 1.0]

    if mode == 1:
        arr[1] = 0
        arr[2] = 0
    if mode == 2:
        arr[0] = 0
        arr[1] = 0
    if mode == 3:
        arr[0] = 0
        arr[2] = 0

    return np.array(arr)

print('computing outer points to highlight...')
for x in full_list:
    if len(list(filter(lambda y: guaranteed_better_than(y,x), full_list))) == 0:
        filtered_list.append(x)

print(len(full_list))
print(len(filtered_list))

filtered_list = set(filtered_list)

print('drawing points...')
_prevxis = -1
for points_set in set_list:
    x_l = []
    y_l = []
    col = 'black'
    marker = 'x'
    for point in points_set:
        _x = get_imgtxtsim_precrec(point)
        col = compute_color(point)
        x_l.append(_x[1][0])
        y_l.append(_x[1][1])
        if mode == 3:
            if point in filtered_list:
                marker = 'o'
    plt.plot(x_l, y_l, col=col, marker=marker, markeredgewidth=1.5)

full_list.sort(key=lambda x: (x[-1], x[0]), reverse=True)
print()
print("most feasible points:")
for x in full_list[0:5]:
    print("img_sim_min: %.3f, text_sim_min: %.3f" % get_imgtxtsim_precrec(x)[0])
    print("precision: %.4f, recall: %.4f" % get_imgtxtsim_precrec(x)[1])
    print("f1_score: %.4f" % x[4])
    print("---")

ipath = ipath.replace('.json', '_mode%d.png' % mode)
print('\rsaving  %s... ' % ipath, end='')
fig.savefig(ipath)
plt.show()
