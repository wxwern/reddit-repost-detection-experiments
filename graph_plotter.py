#!/usr/bin/env python3
import json
from matplotlib import pyplot as plt
import numpy as np

print('input computed graph json file name:')
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
            print('loaded ' + i)
        else:
            print('error: sample count mismatch')
        print('input another computed graph json file name (type nothing to graph):')

def compute_color(i_sim,t_sim):
    return np.array([max(min(1.0,i_sim),0.0)*0.75, 0, max(min(1.0,t_sim),0.0)*0.75, 1.0])

plt.xlabel('precision')
plt.ylabel('recall')
plt.grid()
axes = plt.gca()
axes.set_xlim([0.0,1.0])
axes.set_ylim([0.0,1.0])

full_list = []

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
    for x,y,i_diff,t_sim,_ in points:
        plt.scatter(x,y, color=compute_color(i_diff, t_sim))
full_list.sort(key=lambda x: (x[-1], x[0]), reverse=True)
print()
print("Most feasible points")
for x in full_list[0:5]:
    print("img_sim_min: %.3f, text_sim_min: %.3f" % (x[2], x[3]))
    print("precision: %.4f, recall: %.4f" % (x[0], x[1]))
    print("f1_score: %.4f" % x[4])
    print("---")
plt.show()

