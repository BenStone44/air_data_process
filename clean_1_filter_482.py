import csv
from itertools import islice
import os
import numpy as np
import random
import requests
import json
import os
import pandas as pd
import copy


def get_file_path_list(base):
    for root, ds, fs in os.walk(base):
        for f in fs:
            fullname = os.path.join(root, f)
            yield fullname


def main():
    output_path = './output/'
    include = []
    with open("./locations.json", 'r') as load_f:
        load_dict = json.load(load_f)
        for item in load_dict:
            include.append(str(item['rid']) + 'A')
        include.append('date')
        include.append('hour')
        include.append('type')
        print(len(include))

    exclude_total = []  # 记录所有需要去除的城市
    csvfile = open('./site_list.csv', encoding='utf-8')
    a = pd.read_csv(csvfile, engine='python')
    for i in range(len(a)):
        if a["监测点编码"][i] not in include:
            exclude_total.append(a["监测点编码"][i])
    print(exclude_total)

    base = './total_file/'
    for i in get_file_path_list(base):
        df = pd.read_csv(i, header=0)
        exclude = df.columns.values.tolist()  # 存在的城市
        for j in range(len(include)):  # 删除需要删除的部分
            exclude.remove(include[j])
        df = df.drop(exclude, axis=1)
        df.to_csv(output_path+i[-10:])


if __name__ == '__main__':
    main()
