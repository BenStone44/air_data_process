import matplotlib.pyplot as plt
import numpy as np
import json
with open('air-data.json', encoding='utf-8') as f:
    line = f.readline()
    d = json.loads(line)
    f.close()

x = []
for i in range(8472):
    x.append(i+1)
x = np.array(x)

for key in d:
    y = np.array(d[key])
    plt.scatter(x, y, s=1)
    plt.savefig('./pictures/'+key+'.jpg', dpi=800)
    plt.show()
