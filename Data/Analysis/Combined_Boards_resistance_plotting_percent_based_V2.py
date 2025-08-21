# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 11:33:41 2025

@author: hugol
"""

import os
import copy
import math
import matplotlib.pyplot as plt
import numpy as np

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

impact_numbers_percents = copy.deepcopy(impact_numbers_list)
resistance_numbers_percents = copy.deepcopy(resistance_numbers_list)

for i in range(len(impact_numbers_list)):
    for j in range(len(impact_numbers_list[i])):
        impact_numbers_percents[i][j] = (impact_numbers_list[i][j] / impact_numbers_list[i][-1]) * 100

for i in range(len(resistance_numbers_list)):
    current_max = 0
    current_min = 0
    for j in range(len(resistance_numbers_list[i])):
        if j == 0:
            current_max = resistance_numbers_list[i][j]
            current_min = resistance_numbers_list[i][j]
        else:
            if current_max < resistance_numbers_list[i][j]:
                current_max = resistance_numbers_list[i][j]
            if current_min > resistance_numbers_list[i][j]:
                current_min = resistance_numbers_list[i][j]
    for j in range(len(resistance_numbers_list[i])):
        resistance_numbers_percents[i][j] = ((resistance_numbers_list[i][j] - current_min) / (current_max-current_min)) * 100

plt.figure(figsize=(10, 6))
for i in range(len(board_names)):
    plt.plot(impact_numbers_percents[i], resistance_numbers_percents[i],  marker='o', linestyle='-', label=board_names[i])
#plt.ylim([-0.0005,0.002])
plt.legend()
plt.xlabel('Impact Percent')
plt.ylabel('Resistance Percent')
plt.title('Resistance Percent vs. Impact Percent')
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{save_path}\\all_boards_metric_plot_percent_based_V2.png", dpi=300)
plt.show()

a_values = []
b_values = []

def y_value(a, b, x):
    return (a * (1 - 1*np.exp((-1*b*x))))

def a_value(b, xn, yn):
    sum_for_numerator = 0
    sum_for_denominator = 0
    for i in range(len(yn)):
        sum_for_numerator += (yn[i]*(1-np.exp(-1*b*xn[i])))
        sum_for_denominator += math.pow((1-np.exp(-1*b*xn[i])), 2)
    return (sum_for_numerator/sum_for_denominator)
    
def partial_b_expression(a, b, x, y):
    return (2*(y-a*(1-np.exp(-1*b*x))))*(-1*a*x*np.exp(-1*b*x))

def solve_for_sum_of_partial_b(impact_percents, resistance_percents, a, b):
    sum_of_partial = 0
    for i in range(len(impact_percents)):
        sum_of_partial += partial_b_expression(a, b, impact_percents[i], resistance_percents[i])
    return sum_of_partial

def sum_of_square_residuals(a, b, xn, yn):
    sum_of_residuals = 0
    for i in range(len(xn)):
        sum_of_residuals += math.pow((yn[i]-a*(1-np.exp(-1*b*xn[i]))), 2)
    return sum_of_residuals

for k in range(len(impact_numbers_percents)):
    possible_b_values = np.linspace(-1,2,30000)
    current_min_index = -100
    b_zeros = []
    a_zeros = []
    for j in range(len(possible_b_values)):
        if(solve_for_sum_of_partial_b(impact_numbers_percents[k], resistance_numbers_percents[k], a_value(possible_b_values[j], impact_numbers_percents[k], resistance_numbers_percents[k]), possible_b_values[j]) < 0.00001):
            b_zeros.append(possible_b_values[j])
    for j in range(len(b_zeros)):
        a_zeros.append(a_value(b_zeros[j], impact_numbers_percents[k], resistance_numbers_percents[k]))
    for j in range(len(a_zeros)):
        if(j == 0):
            current_min_index = j
        elif(sum_of_square_residuals(a_zeros[current_min_index], b_zeros[current_min_index], impact_numbers_percents[k], resistance_numbers_percents[k]) > sum_of_square_residuals(a_zeros[j], b_zeros[j], impact_numbers_percents[k], resistance_numbers_percents[k])):
            current_min_index = j
    if (current_min_index != -100):
        a_values.append(a_zeros[current_min_index])
        b_values.append(b_zeros[current_min_index])
    else:
        a_values.append(100)
        b_values.append(0.08)

fit_line_x_values = []
fit_line_y_values = []
for i in range(len(impact_numbers_percents)):
    fit_line_x_values.append(np.linspace(0, 100, 1000))
    fit_line_y_values.append(y_value(a_values[i], b_values[i], fit_line_x_values[i]))
    
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
plt.savefig(f"{save_path}\\all_boards_metric_plot_percent_based_with_trendlines_V2.png", dpi=300)
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
plt.savefig(f"{save_path}\\all_boards_trendline_plot_V2.png", dpi=300)
plt.show()

for i in range(len(board_names)):
    plt.figure(figsize=(10,6))
    plt.plot(fit_line_x_values[i], fit_line_y_values[i], label=board_names_trendline[i])
    plt.plot(impact_numbers_percents[i], resistance_numbers_percents[i],  marker='o', linestyle='', label=board_names[i])
    plt.ylim([-5,120])
    plt.legend()
    plt.xlabel('Impact Percent')
    plt.ylabel('Resistance Percent')
    plt.title('Resistance Percent vs. Impact Percent')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{board_save_paths[i]}\\{board_names[i]}_metric_plot_percent_based_V2.png", dpi=300)
    plt.show()


