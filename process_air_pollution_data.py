import json
import os
import csv
from geopy.distance import geodesic
import pandas as pd
import numpy as np
import math
import random

# read all data
path = "./total_file"  # 文件夹目录
files = os.listdir(path)  # 得到文件夹下的所有文件名称
day = 0
STSeriesAll = {}
attr_name = 'AQI'

# generate ids
ids = list(range(1000, 3500))
for id in ids:
    STSeriesAll[id] = pd.Series([np.nan for _ in range(8472)])

headers = []  # headers for each file

for file in files:  # 遍历文件夹
    if not os.path.isdir(file):  # 判断是否是文件夹，不是文件夹才打开
        # 读取csv至字典
        csvFile = open(path + "/" + file, "r")
        reader = csv.reader(csvFile)

        for row in reader:
            headers = row[3:]  # 当前文件的header
            break

        nReading = 0
        for row in reader:
            if reader.line_num == 1:  # 忽略第一行
                continue
            if row[2] == attr_name:
                hour = int(row[1])
                nReading += 1
                for idIndex, item in enumerate(row[3:]):
                    id = headers[idIndex][:-1]
                    value = np.nan if item == '' else int(item)  # int is for AQI
                    STSeriesAll[int(id)][day * 24 + hour] = value
        csvFile.close()
    day += 1

# import filter sites
sites = []
with open("./locations.json", 'r') as load_f:
    sites = json.load(load_f)

# series of filter
STSeries = {}
for site in sites:
    rid = site["rid"]
    STSeries[rid] = STSeriesAll[rid]

# import all sites
sitesAll = []
csvFile = open("./site_list.csv", "r", encoding='UTF-8')
reader = csv.reader(csvFile)
for row in reader:
    if reader.line_num == 1:  # 忽略第一行
        continue
    id = int(row[0][:-1])
    lat = float(row[4])
    lng = float(row[3])
    sitesAll.append({
        "rid": id,
        "lng": lng,
        "lat": lat
    })

# prepare knn
knn_dict_15 = {}
for i, site in enumerate(sites):
    rid = site["rid"]
    lat = site['lat']
    lng = site['lng']
    knn_dict_15[rid] = []

    for site2 in sitesAll:
        rid2 = site2["rid"]
        lat2 = site2['lat']
        lng2 = site2['lng']
        if rid2 == rid:
            continue

        d = geodesic((lat2, lng2), (lat, lng)).km
        if d < 15:
            knn_dict_15[rid].append({"d": d, "rid": rid2})

# interpolate
for id, series in STSeriesAll.items():
    STSeriesAll[id] = series.interpolate(method='polynomial', order=2, limit=3, limit_direction='both')

# replace using knn again
for id, series in STSeries.items():
    neighbors = knn_dict_15[id]
    for hour, value in enumerate(series):
        if math.isnan(value):
            weightSum = 0
            valueSum = 0
            for neighbor in neighbors:
                neighborD = neighbor["d"]
                neighborId = neighbor["rid"]

                v1 = STSeriesAll[neighborId][hour]
                if not math.isnan(v1):
                    valueSum += v1 * (16 - neighborD)
                    weightSum += (16 - neighborD)

                if hour != 8471:
                    v2 = STSeriesAll[neighborId][hour + 1]
                    if not math.isnan(v2):
                        valueSum += v2 * (16 - neighborD) * 0.8
                        weightSum += (16 - neighborD) * 0.8

                if hour != 0:
                    v0 = STSeriesAll[neighborId][hour - 1]
                    if not math.isnan(v0):
                        valueSum += v0 * (16 - neighborD) * 0.8
                        weightSum += (16 - neighborD) * 0.8

            if weightSum > 0:
                series[hour] = valueSum / weightSum
    print(id, series.isnull().sum(), series.size)

for id, series in STSeries.items():
    STSeries[id] = series.interpolate(method='polynomial', order=2)
    print(id, STSeries[id].isnull().sum(), series.size)


def hackFixer(x):
    if math.isnan(x):
        return x
    elif x <= 0:
        return random.randint(0, 15)
    else:
        return int(x)


validSTSeries = {}
for id, series in STSeries.items():
    if STSeries[id].isnull().sum() < 8:
        l = list(series.interpolate(method='pad'))
        validSTSeries[id] = list(map(lambda x: hackFixer(x), l))
        # print(id, validSTSeries[id].isnull().sum())

with open('air-data.json', 'w', encoding='UTF-8') as f:
    json.dump(validSTSeries, f)
