# -*- coding: utf-8 -*-
"""
Created on Mon Jul 21 12:24:35 2025

@author: hugol
"""

import os
import math
import copy
import numpy as np
import matplotlib.pyplot as plt

file_path = os.getcwd()
save_path = file_path.replace("\Board 4.6", "\Board 4.6\\figures")

impacts = []
feature_names = ["Maximum", "Absolute Mean", "RMS", "Skewness", "Kurtosis", "Crest Factor", "Shape Factor", "Impulse Factor"]
features = [[] for i in range(2)]

lvm_files = sorted([f for f in os.listdir(file_path) if f.endswith(".lvm")])
            
for j, filename in enumerate(lvm_files):
    with open(os.path.join(file_path, filename), 'r') as file:
        data = np.loadtxt(os.path.join(file_path, lvm_files[j]), usecols=(2))
        data = data.tolist()
        data_zeroed = data.copy()
        current_max = -1
        absolute_mean = 0
        for k in range(len(data)):
            data_zeroed[k]-=data[0]
            if abs(data_zeroed[k]) > current_max:
                current_max = abs(data_zeroed[k])
            absolute_mean += (abs(data_zeroed[k])/len(data_zeroed))
                
        features[0].append(current_max)
        features[1].append(absolute_mean)
        impacts.append(j)

#print(features[0])

unfiltered_mean = 0
unfiltered_standard_deviation = 0
for i in range(len(features[0])):
    unfiltered_mean += (abs(features[0][i])/len(features[0]))
for i in range(len(features[0])):
    unfiltered_standard_deviation += pow((features[0][i]-unfiltered_mean), 2)
unfiltered_standard_deviation = math.sqrt((unfiltered_standard_deviation/(len(features[0])-1)))
outliers_fixed = False
while(not outliers_fixed):
    for i in range(len(features[0])):
        if ((features[0][i] > (unfiltered_mean + (4*unfiltered_standard_deviation))) or (features[0][i] < (unfiltered_mean - (4*unfiltered_standard_deviation)))):
            for j in range(len(features)):
                if j == 0:
                    impacts.pop(i)
                features[j].pop(i)
            break
    else:
        outliers_fixed = True

#print(features[0][0])
features_zeroed = copy.deepcopy(features)

for i in range(len(features[0])):
    for j in range(len(features)):
        features_zeroed[j][i] -= features[j][0]

print(features[1])

plt.figure(figsize=(10, 6))
plt.plot(impacts, features_zeroed[0],  marker='o', linestyle='', label=feature_names[0])
plt.plot(impacts, features_zeroed[1],  marker='o', linestyle='', label=feature_names[1])
plt.legend()
plt.xlabel('Impact Number')
plt.ylabel('Feature Values')
plt.title('Feature Plot of Board Acceleration')
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{save_path}\\4_6_feature_plot", dpi=300)
plt.show()