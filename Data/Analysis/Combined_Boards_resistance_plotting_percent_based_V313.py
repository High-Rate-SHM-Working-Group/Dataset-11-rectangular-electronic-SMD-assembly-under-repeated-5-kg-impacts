# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 11:33:41 2025

@author: hugol
"""

import os
import copy
#import math
import matplotlib.pyplot as plt
import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin
from scipy.optimize import curve_fit

#plt.figure().close('all')

current_directory = os.getcwd()
file_path = current_directory.replace("\Analysis", "")
save_path = current_directory.replace("\Analysis", "\Analysis\\figures")

data_list = os.listdir(file_path)
impact_numbers_list = []
resistance_numbers_list = []
board_names = []
board_names_trendline = []
board_save_paths = []
MAX_VALID_RESISTANCE = 2

only_boards = [-1,-1,-1,3,4,-1,6,-1,-1,-1]

impacts_to_remove = [[0], [5], [0], [0], [27,33,34,53,54], [6,9,46,79], [21], [22,23,24,25,26], [0], [23,24]]

for i in data_list:
    if "Board" in i:
        if not i == "Board 0.0":
            new_file_address = file_path+"\\"+i
            new_save_address = file_path+"\\"+i+"\\figures"
            board_names.append(i)
            board_names_trendline.append(i+' Trendline')
            board_save_paths.append(new_save_address)
            
            lvm_files = sorted([f for f in os.listdir(new_file_address) if f.endswith(".lvm")])
            
            resistance_baseline = 0
            impacts = []
            resistances = []
            
            for j, filename in enumerate(lvm_files):
                with open(os.path.join(new_file_address, filename), 'r') as file:
                    first_line = file.readline().strip()
                    columns = first_line.split('\t')

                    try:
                        resistance = float(columns[-1]) # Gets the resistance measurement for the respective board and impact number
                        if resistance < MAX_VALID_RESISTANCE and resistance > 0: # Adds resistance if valid
                            resistances.append((resistance-resistance_baseline))
                            impacts.append(j)
                        else:
                            print(f"Skipping {filename}: resistance {resistance} exceeds threshold")
                    except (IndexError, ValueError):
                        print(f"Skipping {filename}: invalid format")
            
            impact_numbers_list.append(impacts)
            resistance_numbers_list.append(resistances)

resistance_numbers_removed = copy.deepcopy(resistance_numbers_list)

impact_numbers_percents = copy.deepcopy(impact_numbers_list)


for i in range(len(impact_numbers_list)):
    for j in range(len(impact_numbers_list[i])):
        impact_numbers_percents[i][j] = (impact_numbers_list[i][j] / impact_numbers_list[i][-1]) * 100

for i in range(len(impact_numbers_list)):
    pop_total = 0
    for j in range(len(impact_numbers_list[i])):
        for k in range(len(impacts_to_remove[i])):
            if impact_numbers_list[i][j] == impacts_to_remove[i][k] or impact_numbers_list[i][j] == 0 or impact_numbers_list[i][j] == 1 or impact_numbers_list[i][j] == len(impact_numbers_list[i])-1:
                impact_numbers_percents[i].pop(j-pop_total)
                resistance_numbers_removed[i].pop(j-pop_total)
                pop_total= pop_total+1
                break

resistance_numbers_percents = copy.deepcopy(resistance_numbers_removed)

for i in range(len(resistance_numbers_removed)):
    current_max = 0
    current_min = 0
    for j in range(len(resistance_numbers_removed[i])):
        if j == 0:
            current_max = resistance_numbers_removed[i][j]
            current_min = resistance_numbers_removed[i][j]
        else:
            if current_max < resistance_numbers_removed[i][j]:
                current_max = resistance_numbers_removed[i][j]
            if current_min > resistance_numbers_removed[i][j]:
                current_min = resistance_numbers_removed[i][j]
    for j in range(len(resistance_numbers_removed[i])):
        resistance_numbers_percents[i][j] = ((resistance_numbers_removed[i][j] - current_min) / (current_max-current_min)) * 100

#plt.figure(figsize=(10, 6))
#for i in range(len(board_names)):
    #plt.plot(impact_numbers_percents[i], resistance_numbers_percents[i],  marker='o', linestyle='-', label=board_names[i])
#plt.ylim([-0.0005,0.002])
#plt.legend()
#plt.xlabel('Impact Percent')
#plt.ylabel('Resistance Percent')
#plt.title('Resistance Percent vs. Impact Percent')
#plt.grid(True)
#plt.tight_layout()
#plt.savefig(f"{save_path}\\all_boards_metric_plot_percent_based_V2.png", dpi=300)
#plt.show()

a_values = []
b_values = []

#impact_numbers_percents_array = copy.deepcopy(impact_numbers_percents)
#resistance_numbers_percents_array = copy.deepcopy(resistance_numbers_percents)

#for i in range(len(impact_numbers_percents_array)):
    #for j in range(len(impact_numbers_percents_array[i])):
        #impact_numbers_percents_array[i][j] = [impact_numbers_percents[i][j]]
        #resistance_numbers_percents_array[i][j] = np.array(resistance_numbers_percents[i][j])

#print(impact_numbers_percents_array)
#svr_rbf = []
#for i in range(len(impact_numbers_percents)):
    #svr_rbf.append(SVR(kernel="rbf"))
    #svr_rbf[i].fit(impact_numbers_percents_array[i], resistance_numbers_percents[i])
def custom_eq(x, a, b):
    return a * (1 - np.exp(-b * x))

class CustomExpRegressor(BaseEstimator, RegressorMixin):
    def __init__(self, a_init=100, b_init=0.08):
        self.a_init = a_init
        self.b_init = b_init
        self.a_ = None
        self.b_ = None

    def fit(self, X, y):
        # Make sure X is 1D
        X = np.asarray(X).ravel()
        y = np.asarray(y)

        # Use curve_fit to estimate parameters
        params, _ = curve_fit(custom_eq, X, y, p0=[self.a_init, self.b_init], maxfev=30000)
        self.a_, self.b_ = params
        return self

    def predict(self, X):
        X = np.asarray(X).ravel()
        return custom_eq(X, self.a_, self.b_)

models = []
for i in range(len(impact_numbers_percents)):
    models.append(CustomExpRegressor(a_init = 100, b_init = 0.08))
    models[i].fit(impact_numbers_percents[i], resistance_numbers_percents[i])

fit_line_x_values = []
fit_line_y_values = []
for i in range(len(impact_numbers_percents)):
    fit_line_x_values.append(np.linspace(0, 100, 1000))
    fit_line_y_values.append(models[i].predict(fit_line_x_values[i]))
    
#for i in range(len(impact_numbers_percents)):
    #for j in range(1001):
        #fit_line_x_values[i].append([(j*0.1)])
    #fit_line_y_values.append(svr_rbf[i].predict(fit_line_x_values[i]))
 
'''
plt.figure(figsize=(12,8))
#plt.plot(fit_line_x_values[0], fit_line_y_values[0])
for i in range(len(board_names)):
    plt.plot(fit_line_x_values[i], fit_line_y_values[i], label=board_names_trendline[i])
for i in range(len(board_names)):
    plt.plot(impact_numbers_percents[i], resistance_numbers_percents[i],  marker='o', linestyle='', label=board_names[i])
#plt.plot(fit_line_x_values[8], fit_line_y_values[8], label=board_names[8])
#plt.plot(impact_numbers_percents[8], resistance_numbers_percents[8],  marker='o', linestyle='', label=board_names[8])
plt.ylim([-5,120])
plt.legend()
plt.xlabel('Impact Percent')
plt.ylabel('Resistance Percent')
plt.title('Resistance Percent vs. Impact Percent')
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{save_path}\\all_boards_metric_plot_percent_based_with_trendlines_V312.png", dpi=300)
plt.show()



plt.figure(figsize=(10, 6))
for i in range(len(board_names)):
    plt.plot(fit_line_x_values[i], fit_line_y_values[i], label=board_names_trendline[i])
plt.ylim([-5,120])
plt.legend()
plt.xlabel('Impact Percent')
plt.ylabel('Resistance Percent')
plt.title('Resistance Percent vs. Impact Percent')
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{save_path}\\all_boards_trendline_plot_V312.png", dpi=300)
plt.show()
'''

for i in range(len(board_names)):
    if i == only_boards[i]:
        plt.rcParams['font.family'] = 'Times New Roman'
        plt.rcParams['font.size'] = 10
        
        plt.figure(figsize=(6,3))
        plt.plot(impact_numbers_percents[i], resistance_numbers_percents[i], label=board_names[i], linewidth=1, linestyle='',  marker='.')
        plt.plot(fit_line_x_values[i], fit_line_y_values[i], label=board_names_trendline[i], linewidth=1)
        
        plt.xlabel("impact percent")
        plt.ylabel("resistance percent")
        # plt.title("Midpoint Displacement Comparison: MATLAB vs Abaqus")
        plt.legend(loc="lower right", facecolor="white", edgecolor="lightgray", framealpha=1, frameon=True)
        plt.grid(True)
        plt.tight_layout()
        
        #plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        


plt.figure(figsize=(6, 3))
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 10

for i in range(len(board_names)):
    if i == only_boards[i]:  # Only selected boards
        plt.plot(
            impact_numbers_percents[i],
            resistance_numbers_percents[i],
            marker='.',
            linestyle='',
            linewidth=1,
            label=board_names[i]
        )

# plt.ylim([-5, 120])
plt.legend(loc="lower right", facecolor="white", edgecolor="lightgray", framealpha=1, frameon=True)
plt.xlabel("impact percent")
plt.ylabel("resistance percent")
# plt.title("Resistance Percent vs. Impact Percent (Data Only)")
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{save_path}\\selected_boards_data_only.png", dpi=300, bbox_inches='tight')
plt.show()


plt.figure(figsize=(6, 3))
for i in range(len(board_names)):
    if i == only_boards[i]:  # Only selected boards
        plt.plot(
            fit_line_x_values[i],
            fit_line_y_values[i],
            linewidth=1,
            label=board_names_trendline[i]
        )

# plt.ylim([-5, 120])
plt.legend(loc="lower right", facecolor="white", edgecolor="lightgray", framealpha=1, frameon=True)
plt.xlabel("impact percent")
plt.ylabel("resistance percent")
# plt.title("Resistance Percent vs. Impact Percent (Trendlines Only)")
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{save_path}\\selected_boards_trendlines_only.png", dpi=300, bbox_inches='tight')
plt.show()