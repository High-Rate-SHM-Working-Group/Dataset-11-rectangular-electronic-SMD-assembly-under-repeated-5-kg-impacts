"""
Created on Fri Jun 27 10:42:08 2025

@author: Hugo Luck
@Credits: trott
"""

import os
import matplotlib.pyplot as plt

save_path_combined = r"C:\Users\hugol\Documents\Dataset-11-rectangular-electronic-assembly-under-repeated-5-kg-impacts\Data\Analysis\Figures"

MAX_VALID_RESISTANCE = 5  # Define your threshold here
MIN_VALID_RESISTANCE = 1      # Avoid log(0) or negative

#%% Opens Data For Board 4.1
# Folder containing your .lvm files
folder_path_3_4 = r"C:\Users\hugol\Documents\Dataset-11-rectangular-electronic-assembly-under-repeated-5-kg-impacts\Data\Board 3.4"

lvm_files = sorted([f for f in os.listdir(folder_path_3_4) if f.endswith(".lvm")])

resistances_3_4 = [] # Resistances for board
impact_numbers_3_4 = [] # Impact Numbers for board
resistance_baseline = -1 # Resets the baseline resistance for upcoming for loop

for i, filename in enumerate(lvm_files):
    with open(os.path.join(folder_path_3_4, filename), 'r') as file:
        first_line = file.readline().strip()
        columns = first_line.split('\t')

        try:
            resistance = float(columns[-1]) # Gets the resistance measurement for the respective board and impact number
            if resistance_baseline == -1: # Runs for first value to set the base resistance and zero the graph
                resistance_baseline = resistance
                resistances_3_4.append((resistance-resistance_baseline))
                impact_numbers_3_4.append(i + 1)
            elif resistance < MAX_VALID_RESISTANCE: # Adds resistance if valid
                resistances_3_4.append((resistance-resistance_baseline))
                impact_numbers_3_4.append(i + 1)
            else:
                print(f"Skipping {filename}: resistance {resistance} exceeds threshold")
        except (IndexError, ValueError):
            print(f"Skipping {filename}: invalid format")

#%% Opens Data For Board 4.1
# Folder containing your .lvm files
folder_path_4_1 = r"C:\Users\hugol\Documents\Dataset-11-rectangular-electronic-assembly-under-repeated-5-kg-impacts\Data\Board 4.1"

lvm_files = sorted([f for f in os.listdir(folder_path_4_1) if f.endswith(".lvm")])

resistances_4_1 = [] # Resistances for board
impact_numbers_4_1 = [] # Impact Numbers for board
resistance_baseline = -1 # Resets the baseline resistance for upcoming for loop

for i, filename in enumerate(lvm_files):
    with open(os.path.join(folder_path_4_1, filename), 'r') as file:
        first_line = file.readline().strip()
        columns = first_line.split('\t')

        try:
            resistance = float(columns[-1]) # Gets the resistance measurement for the respective board and impact number
            if resistance_baseline == -1: # Runs for first value to set the base resistance and zero the graph
                resistance_baseline = resistance
                resistances_4_1.append((resistance-resistance_baseline))
                impact_numbers_4_1.append(i + 1)
            elif resistance < MAX_VALID_RESISTANCE: # Adds resistance if valid
                resistances_4_1.append((resistance-resistance_baseline))
                impact_numbers_4_1.append(i + 1)
            else:
                print(f"Skipping {filename}: resistance {resistance} exceeds threshold")
        except (IndexError, ValueError):
            print(f"Skipping {filename}: invalid format")

#%% Opens Data For test 4.3
# Folder containing your .lvm files
folder_path_4_3 = r"C:\Users\hugol\Documents\Dataset-11-rectangular-electronic-assembly-under-repeated-5-kg-impacts\Data\Board 4.3"

lvm_files = sorted([f for f in os.listdir(folder_path_4_3) if f.endswith(".lvm")])

resistances_4_3 = [] # Resistances for board
impact_numbers_4_3 = [] # Impact Numbers for board
resistance_baseline = -1 # Resets the baseline resistance for upcoming for loop

for i, filename in enumerate(lvm_files):
    with open(os.path.join(folder_path_4_3, filename), 'r') as file:
        first_line = file.readline().strip()
        columns = first_line.split('\t')

        try:
            resistance = float(columns[-1]) # Gets the resistance measurement for the respective board and impact number
            if resistance_baseline == -1: # Runs for first value to set the base resistance and zero the graph
                resistance_baseline = resistance
                resistances_4_3.append((resistance-resistance_baseline))
                impact_numbers_4_3.append(i + 1)
            elif resistance < MAX_VALID_RESISTANCE: # Adds resistance if valid
                resistances_4_3.append(resistance-resistance_baseline)
                impact_numbers_4_3.append(i + 1)
            else:
                print(f"Skipping {filename}: resistance {resistance} exceeds threshold")
        except (IndexError, ValueError):
            print(f"Skipping {filename}: invalid format")

#%% Opens Data For test 4.4
# Folder containing your .lvm files
folder_path_4_4 = r"C:\Users\hugol\Documents\Dataset-11-rectangular-electronic-assembly-under-repeated-5-kg-impacts\Data\Board 4.4"

lvm_files = sorted([f for f in os.listdir(folder_path_4_4) if f.endswith(".lvm")])

resistances_4_4 = [] # Resistances for board
impact_numbers_4_4 = [] # Impact Numbers for board
resistance_baseline = -1 # Resets the baseline resistance for upcoming for loop

for i, filename in enumerate(lvm_files):
    with open(os.path.join(folder_path_4_4, filename), 'r') as file:
        first_line = file.readline().strip()
        columns = first_line.split('\t')

        try:
            resistance = float(columns[-1]) # Gets the resistance measurement for the respective board and impact number
            if resistance_baseline == -1: # Runs for first value to set the base resistance and zero the graph
                resistance_baseline = resistance
                resistances_4_4.append((resistance-resistance_baseline))
                impact_numbers_4_4.append(i + 1)
            elif resistance < MAX_VALID_RESISTANCE: # Adds resistance if valid
                resistances_4_4.append(resistance-resistance_baseline)
                impact_numbers_4_4.append(i + 1)
            else:
                print(f"Skipping {filename}: resistance {resistance} exceeds threshold")
        except (IndexError, ValueError):
            print(f"Skipping {filename}: invalid format")

#%% Opens Data For test 4.5
# Folder containing your .lvm files
folder_path_4_5 = r"C:\Users\hugol\Documents\Dataset-11-rectangular-electronic-assembly-under-repeated-5-kg-impacts\Data\Board 4.5\temp all"

lvm_files = sorted([f for f in os.listdir(folder_path_4_5) if f.endswith(".lvm")])

resistances_4_5 = [] # Resistances for board
impact_numbers_4_5 = [] # Impact Numbers for board
resistance_baseline = -1 # Resets the baseline resistance for upcoming for loop

for i, filename in enumerate(lvm_files):
    with open(os.path.join(folder_path_4_5, filename), 'r') as file:
        first_line = file.readline().strip()
        columns = first_line.split('\t')

        try:
            resistance = float(columns[-1]) # Gets the resistance measurement for the respective board and impact number
            if resistance_baseline == -1: # Runs for first value to set the base resistance and zero the graph
                resistance_baseline = resistance
                resistances_4_5.append((resistance-resistance_baseline))
                impact_numbers_4_5.append(i + 1)
            elif resistance < MAX_VALID_RESISTANCE: # Adds resistance if valid
                resistances_4_5.append(resistance-resistance_baseline)
                impact_numbers_4_5.append(i + 1)
            else:
                print(f"Skipping {filename}: resistance {resistance} exceeds threshold")
        except (IndexError, ValueError):
            print(f"Skipping {filename}: invalid format")

#%% Opens Data For test 4.6
# Folder containing your .lvm files
folder_path_4_6 = r"C:\Users\hugol\Documents\Dataset-11-rectangular-electronic-assembly-under-repeated-5-kg-impacts\Data\Board 4.6"

lvm_files = sorted([f for f in os.listdir(folder_path_4_6) if f.endswith(".lvm")])

resistances_4_6 = [] # Resistances for board
impact_numbers_4_6 = [] # Impact Numbers for board
resistance_baseline = -1 # Resets the baseline resistance for upcoming for loop

for i, filename in enumerate(lvm_files):
    with open(os.path.join(folder_path_4_6, filename), 'r') as file:
        first_line = file.readline().strip()
        columns = first_line.split('\t')

        try:
            resistance = float(columns[-1]) # Gets the resistance measurement for the respective board and impact number
            if resistance_baseline == -1: # Runs for first value to set the base resistance and zero the graph
                resistance_baseline = resistance
                resistances_4_6.append((resistance-resistance_baseline))
                impact_numbers_4_6.append(i + 1)
            elif resistance < MAX_VALID_RESISTANCE: # Adds resistance if valid
                resistances_4_6.append(resistance-resistance_baseline)
                impact_numbers_4_6.append(i + 1)
            else:
                print(f"Skipping {filename}: resistance {resistance} exceeds threshold")
        except (IndexError, ValueError):
            print(f"Skipping {filename}: invalid format")

#%% Plotting All Data Together
# Plotting
plt.figure(figsize=(10, 6))
plt.plot(impact_numbers_3_4, resistances_3_4, marker='o', linestyle='', label="Board 3.4")
plt.plot(impact_numbers_4_1, resistances_4_1, marker='o', linestyle='', label="Board 4.1")
plt.plot(impact_numbers_4_3, resistances_4_3, marker='o', linestyle='', label="Board 4.3")
plt.plot(impact_numbers_4_4, resistances_4_4, marker='o', linestyle='', label="Board 4.4")
plt.plot(impact_numbers_4_5, resistances_4_5, marker='o', linestyle='', label="Board 4.5")
plt.plot(impact_numbers_4_6, resistances_4_6, marker='o', linestyle='', label="Board 4.6")
plt.ylim([-0.0001,0.002])
plt.legend()
plt.xlabel('Impact Number')
plt.ylabel('Resistance Change (Ohms)')
plt.title('Filtered Resistance vs. Impact Number')
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{save_path_combined}\\combined_boards_metric_plot.png", dpi=300)
plt.show()