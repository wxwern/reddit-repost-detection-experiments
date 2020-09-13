#!/usr/bin/env python3
import json
from matplotlib import pyplot as plt
import numpy as np

print('input computed graph json file name:')
with open(input()) as f:
    d = json.load(f)

def compute_color(i_diff,t_sim):
    return np.array([max(min(1.0, 1-i_diff/20),0.0)*0.75, 0, max(min(1.0,t_sim),0.0)*0.75, 1.0])

plt.xlabel('precision')
plt.ylabel('recall')
plt.grid()
axes = plt.gca()
axes.set_xlim([0.0,1.0])
axes.set_ylim([0.0,1.0])

img_range = range(0, 20+1, 2)
for m in img_range:
    points = list(map(lambda x: \
                      (x['results']['precision'], x['results']['recall'], x['img_diff_min'], x['text_sim_min']), \
                      sorted(
                          list( \
                              filter(lambda x: x['img_diff_min'] == m, d['data']) \
                          ), \
                          key=lambda x: x['text_sim_min']
                      )
                      )
                  )
    x = list(map(lambda p: p[0], points))
    y = list(map(lambda p: p[1], points))
    print(points)
    for x,y,i_diff,t_sim in points:
        plt.scatter(x,y, color=compute_color(i_diff, t_sim))
plt.show()
