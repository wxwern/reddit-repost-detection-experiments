import json
from matplotlib import pyplot as plt

print('input computed graph json file name:')
with open(input()) as f:
    d = json.load(f)

for m in range(0, 20+1, 2):
    points = list(map(lambda x: \
                      (x['results']['precision'], x['results']['recall']), \
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
    plt.xlabel('precision')
    plt.ylabel('recall')
    plt.plot(x,y)
    plt.grid()
    axes = plt.gca()
    axes.set_xlim([0.0,1.0])
    axes.set_ylim([0.0,1.0])
plt.show()
