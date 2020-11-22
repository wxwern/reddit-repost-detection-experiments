#!/usr/bin/env python3
import json
from matplotlib import pyplot as plt
import numpy as np

print('input computed graph json file names (empty line to graph):')
d = {}
while True:
    i = input()
    if i == "":
        break
    with open(i) as f:
        x = json.load(f)
        if 'sample_count' not in d or x['sample_count'] == d['sample_count']:
            if not d:
                d = x
            else:
                d['data'] += x['data']
        else:
            print('error: sample count mismatch')




plt.xlabel('precision')
plt.ylabel('recall')
plt.grid()
axes = plt.gca()
axes.set_xlim([0.0,1.0])
axes.set_ylim([0.0,1.0])

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
    x = list(map(lambda p: p[0], points))
    y = list(map(lambda p: p[1], points))
    full_list += points


def get_imgtxtsim_precrec(x):
    return ((x[2], x[3]), (x[0], x[1]))

def guaranteed_better_than(a,b):
    a = get_imgtxtsim_precrec(a)
    b = get_imgtxtsim_precrec(b)
    return a[1][0] > b[1][0] and a[1][1] > b[1][1]

def compute_color(x):
    i_sim,t_sim = get_imgtxtsim_precrec(x)[0]
    return np.array([max(min(1.0,(i_sim-0.6)*2.5),0.0)*0.75,
                     0 if x not in filtered_list else 0.75,
                     max(min(1.0,t_sim),0.0)*0.75, 1.0])

print('computing outer points to highlight...')
for x in full_list:
    if len(list(filter(lambda y: guaranteed_better_than(y,x), full_list))) == 0:
        filtered_list.append(x)

print(len(full_list))
print(len(filtered_list))

filtered_list = set(filtered_list)

print('drawing points...')
_prevxis = -1
for x in full_list:
    _x = get_imgtxtsim_precrec(x)
    if _prevxis != _x[0][0]:
        plt.pause(0.25)
        _prevxis = _x[0][0]
    else:
        pass
        #plt.pause(0.005)
    plt.scatter(_x[1][0], _x[1][1], color=compute_color(x))

full_list.sort(key=lambda x: (x[-1], x[0]), reverse=True)
print()
print("most feasible points:")
for x in full_list[0:5]:
    print("img_sim_min: %.3f, text_sim_min: %.3f" % get_imgtxtsim_precrec(x)[0])
    print("precision: %.4f, recall: %.4f" % get_imgtxtsim_precrec(x)[1])
    print("f1_score: %.4f" % x[4])
    print("---")

plt.pause(5)
plt.show()




