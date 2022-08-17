import json
import pandas as pd
import random
import numpy as np

with open('air-data.json', encoding='utf-8') as f:
    line = f.readline()
    d = json.loads(line)
    f.close()

data = []
keys = []
data_step = []
for i in range(179):
    keys.append(i + 1)

index = 0
for key in d:
    step = 0  # 记录步数
    step_time = 48  # 以48小时为步长
    while (step * step_time + 177) <= 8471:
        list_day = []
        for i in range(178):
            list_day.append(d[key][step * step_time + i])
        list_day.append(index)
        data_step.append(list_day)
        step = step + 1
    index = index + 1

for key in d:
    step = 0
    start_point = 0
    for i in range(47):





np.random.shuffle(data_step)

data_step = pd.DataFrame(columns=keys, data=data_step)

data_step.to_csv('data_step.csv', index=True, header=True)
print('finished')
