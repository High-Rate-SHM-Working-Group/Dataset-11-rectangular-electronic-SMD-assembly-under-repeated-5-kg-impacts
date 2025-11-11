# -*- coding: utf-8 -*-
import os
import copy
import matplotlib.pyplot as plt
import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin
from scipy.optimize import curve_fit

current_directory = os.getcwd()
file_path = current_directory.replace("\\Analysis", "")
save_path = current_directory.replace("\\Analysis", "\\Analysis\\figures")
os.makedirs(save_path, exist_ok=True)

data_list = os.listdir(file_path)
impact_numbers_list = []
resistance_numbers_list = []
board_names = []
board_names_trendline = []
board_save_paths = []
MAX_VALID_RESISTANCE = 2


# flexible selection: include all except specific boards
exclude_boards = ["Board 4.1", "Board 4.9", "Board 4.10"]

only_boards = []  # will be filled dynamically after scanning directories
def board_selected(i):
    # if exclude list is defined, filter by name
    if board_names[i] in exclude_boards:
        return False
    # if only_boards is empty, include all others
    return (not only_boards) or (i in only_boards)

impacts_to_remove = [[0], [5], [0], [0], [27,33,34,53,54], [6,9,46,79], [21], [22,23,24,25,26], [0], [23,24]]

for entry in data_list:
    if "Board" in entry and entry != "Board 0.0":
        board_path = os.path.join(file_path, entry)
        board_fig_path = os.path.join(board_path, "figures")
        os.makedirs(board_fig_path, exist_ok=True)
        board_names.append(entry)
        board_names_trendline.append(entry + " Trendline")
        board_save_paths.append(board_fig_path)

        lvm_files = sorted([f for f in os.listdir(board_path) if f.endswith(".lvm")])
        impacts = []
        resistances = []

        for j, fname in enumerate(lvm_files):
            fp = os.path.join(board_path, fname)
            try:
                with open(fp, 'r') as fh:
                    first_line = fh.readline().strip()
                cols = first_line.split('\t')
                resistance = float(cols[-1])
                if 0 < resistance < MAX_VALID_RESISTANCE:
                    resistances.append(resistance)
                    impacts.append(j)
                else:
                    print(f"Skipping {fname}: resistance {resistance} exceeds threshold")
            except (IndexError, ValueError, FileNotFoundError):
                print(f"Skipping {fname}: invalid format or unreadable")

        impact_numbers_list.append(impacts)
        resistance_numbers_list.append(resistances)

resistance_numbers_removed = copy.deepcopy(resistance_numbers_list)
impact_numbers_percents = copy.deepcopy(impact_numbers_list)

for i in range(len(impact_numbers_list)):
    if not impact_numbers_list[i]:
        impact_numbers_percents[i] = []
        continue
    last = impact_numbers_list[i][-1]
    if last == 0:
        impact_numbers_percents[i] = [0.0 for _ in impact_numbers_list[i]]
    else:
        impact_numbers_percents[i] = [(imp / last) * 100 for imp in impact_numbers_list[i]]

filtered_imp_perc = []
filtered_res_removed = []
for idx in range(len(impact_numbers_percents)):
    raw_impacts = impact_numbers_list[idx]
    imp_perc = impact_numbers_percents[idx]
    res_raw = resistance_numbers_removed[idx]
    to_remove = set(impacts_to_remove[idx]) if idx < len(impacts_to_remove) else set()

    new_imp_perc = []
    new_res = []
    for pos, imp_val in enumerate(raw_impacts):
        if imp_val in to_remove or imp_val == 0 or imp_val == 1 or pos == (len(raw_impacts) - 1):
            continue
        new_imp_perc.append(imp_perc[pos])
        new_res.append(res_raw[pos])

    filtered_imp_perc.append(new_imp_perc)
    filtered_res_removed.append(new_res)

impact_numbers_percents = filtered_imp_perc
resistance_numbers_removed = filtered_res_removed

resistance_numbers_percents = []
for res_list in resistance_numbers_removed:
    if not res_list:
        resistance_numbers_percents.append([])
        continue
    rmax = max(res_list)
    rmin = min(res_list)
    if np.isclose(rmax, rmin):
        resistance_numbers_percents.append([0.0 for _ in res_list])
    else:
        resistance_numbers_percents.append([((r - rmin) / (rmax - rmin)) * 100 for r in res_list])
        
def set_legend(outside=True, loc="center left"):
    if outside:
        plt.legend(bbox_to_anchor=(1.05, 0.5), loc=loc, borderaxespad=0.,
                   facecolor="white", edgecolor="lightgray", framealpha=1, frameon=True)
    else:
        plt.legend(loc="lower right", facecolor="white", edgecolor="lightgray", framealpha=1, frameon=True)


plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 10

plt.figure(figsize=(6,3))
for i in range(len(board_names)):
    if i < len(impact_numbers_percents) and i < len(resistance_numbers_percents) and board_selected(i):
        x = impact_numbers_percents[i]
        y = resistance_numbers_percents[i]
        if x and y:
            plt.plot(x, y, label=board_names[i], linewidth=1, linestyle='', marker='.')
plt.xlabel("impact percent")
plt.ylabel("resistance percent")
set_legend(outside=True)
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(save_path, "all_boards_metric_plot_percent_based_V313.png"), dpi=300, bbox_inches='tight')
plt.show()

def custom_eq(x, a, b):
    return a * (1 - np.exp(-b * x))

class CustomExpRegressor(BaseEstimator, RegressorMixin):
    def __init__(self, a_init=100, b_init=0.08):
        self.a_init = a_init
        self.b_init = b_init
        self.a_ = None
        self.b_ = None

    def fit(self, X, y):
        X = np.asarray(X).ravel()
        y = np.asarray(y)
        if len(X) == 0:
            self.a_, self.b_ = self.a_init, self.b_init
            return self
        try:
            params, _ = curve_fit(custom_eq, X, y, p0=[self.a_init, self.b_init], maxfev=30000)
            self.a_, self.b_ = params
        except Exception:
            self.a_, self.b_ = self.a_init, self.b_init
        return self

    def predict(self, X):
        X = np.asarray(X).ravel()
        return custom_eq(X, self.a_, self.b_)

models = []
for i in range(len(impact_numbers_percents)):
    mdl = CustomExpRegressor(a_init=100, b_init=0.08)
    mdl.fit(impact_numbers_percents[i], resistance_numbers_percents[i])
    models.append(mdl)

fit_line_x_values = []
fit_line_y_values = []
for i in range(len(impact_numbers_percents)):
    xvals = np.linspace(0, 100, 1000)
    fit_line_x_values.append(xvals)
    fit_line_y_values.append(models[i].predict(xvals))

plt.figure(figsize=(6,3))
for i in range(len(board_names)):
    if i < len(impact_numbers_percents) and i < len(resistance_numbers_percents) and board_selected(i):
        x = impact_numbers_percents[i]
        y = resistance_numbers_percents[i]
        if x and y:
            plt.plot(x, y, label=board_names[i], linewidth=1, linestyle='', marker='.')
for i in range(len(board_names)):
    if i < len(fit_line_x_values) and board_selected(i):
        plt.plot(fit_line_x_values[i], fit_line_y_values[i], label=board_names_trendline[i], linewidth=1)
plt.xlabel("impact percent")
plt.ylabel("resistance percent")
set_legend(outside=True)
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(save_path, "all_boards_metric_plot_percent_based_with_trendlines_V313.png"), dpi=300, bbox_inches='tight')
plt.show()

plt.figure(figsize=(6,3))
for i in range(len(board_names)):
    if i < len(fit_line_x_values) and board_selected(i):
        plt.plot(fit_line_x_values[i], fit_line_y_values[i], linewidth=1, label=board_names_trendline[i])
plt.xlabel("impact percent")
plt.ylabel("resistance percent")
set_legend(outside=True)
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(save_path, "all_boards_trendline_plot_V313.png"), dpi=300, bbox_inches='tight')
plt.show()

for i in range(len(board_names)):
    if i < len(impact_numbers_percents) and i < len(resistance_numbers_percents) and board_selected(i):
        plt.figure(figsize=(6,3))
        x = impact_numbers_percents[i]
        y = resistance_numbers_percents[i]
        if x and y:
            plt.plot(x, y, label=board_names[i], linewidth=1, linestyle='', marker='.')
        if i < len(fit_line_x_values):
            plt.plot(fit_line_x_values[i], fit_line_y_values[i], label=board_names_trendline[i], linewidth=1)
        plt.xlabel("impact percent")
        plt.ylabel("resistance percent")
        set_legend(outside=False)
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(board_save_paths[i], f"{board_names[i]}_metric_plot_percent_based_V313.png"), dpi=300, bbox_inches='tight')
        plt.show()

plt.figure(figsize=(6,3))
for i in range(len(board_names)):
    if i < len(impact_numbers_percents) and i < len(resistance_numbers_percents) and board_selected(i):
        x = impact_numbers_percents[i]
        y = resistance_numbers_percents[i]
        if x and y:
            plt.plot(x, y, marker='.', linestyle='', linewidth=1, label=board_names[i])
plt.xlabel("impact percent")
plt.ylabel("resistance percent")
set_legend(outside=True)
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(save_path, "selected_boards_data_only.png"), dpi=300, bbox_inches='tight')
plt.show()

plt.figure(figsize=(6,3))
for i in range(len(board_names)):
    if i < len(fit_line_x_values) and board_selected(i):
        plt.plot(fit_line_x_values[i], fit_line_y_values[i], linewidth=1, label=board_names_trendline[i])
plt.xlabel("impact percent")
plt.ylabel("resistance percent")
set_legend(outside=True)
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(save_path, "selected_boards_trendlines_only.png"), dpi=300, bbox_inches='tight')
plt.show()
