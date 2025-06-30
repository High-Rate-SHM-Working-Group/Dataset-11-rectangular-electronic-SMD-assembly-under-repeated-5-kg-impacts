"""
Created on Mon Jun 30 11:57:50 2025

@author: hugol
"""

import os
import matplotlib.pyplot as plt

current_directory = os.getcwd()
file_path = current_directory.replace("\Analysis", "")
save_path = current_directory.replace("\Analysis", "\Analysis\\figures")

data_list = os.listdir(file_path)
impact_numbers_list = []
resistance_numbers_list = []
board_names = []
MAX_VALID_RESISTANCE = 5

for i in data_list:
    if "Board" in i:
        if not i == "Board 0.0":
            new_file_address = file_path+"\\"+i
            board_names.append(i)
            
            lvm_files = sorted([f for f in os.listdir(new_file_address) if f.endswith(".lvm")])
            
            resistance_baseline = -1
            impacts = []
            resistances = []
            
            for j, filename in enumerate(lvm_files):
                with open(os.path.join(new_file_address, filename), 'r') as file:
                    first_line = file.readline().strip()
                    columns = first_line.split('\t')

                    try:
                        resistance = float(columns[-1]) # Gets the resistance measurement for the respective board and impact number
                        if resistance_baseline == -1: # Runs for first value to set the base resistance and zero the graph
                            resistance_baseline = resistance
                            resistances.append((resistance-resistance_baseline))
                            impacts.append(j + 1)
                        elif resistance < MAX_VALID_RESISTANCE: # Adds resistance if valid
                            resistances.append((resistance-resistance_baseline))
                            impacts.append(j + 1)
                        else:
                            print(f"Skipping {filename}: resistance {resistance} exceeds threshold")
                    except (IndexError, ValueError):
                        print(f"Skipping {filename}: invalid format")
            
            impact_numbers_list.append(impacts)
            resistance_numbers_list.append(resistances)

plt.figure(figsize=(10, 6))
for i in range(len(board_names)):
    plt.plot(impact_numbers_list[i], resistance_numbers_list[i],  marker='o', linestyle='', label=board_names[i])
plt.ylim([-0.0001,0.002])
plt.legend()
plt.xlabel('Impact Number')
plt.ylabel('Resistance Change (Ohms)')
plt.title('Filtered Resistance vs. Impact Number')
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{save_path}\\all_boards_metric_plot.png", dpi=300)
plt.show()
