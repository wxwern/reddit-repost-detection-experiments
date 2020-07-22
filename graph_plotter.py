import json
from matplotlib import pyplot as plt

print('input computed graph json file name:')
with open(input()) as f:
    d = json.load(f)

for m in range(20, 20+1, 2):
    points = list(map(lambda x: (x['results']['precision'], x['results']['recall']), filter(lambda x: x['img_diff_min'] == m, d['data'])))
    x = list(map(lambda p: p[0], points))
    y = list(map(lambda p: p[1], points))
    plt.xlabel('precision')
    plt.ylabel('recall')
    plt.plot(x,y)
    plt.grid()
    axes = plt.gca()
    axes.set_xlim([0.0,1.0])
    axes.set_ylim([0.0,1.0])
    break
plt.show()
