# -*- coding: utf-8 -*-
import os
import copy
import numpy as np
import matplotlib.pyplot as plt
from sklearn.base import BaseEstimator, RegressorMixin
from scipy.optimize import curve_fit
import itertools
from matplotlib.lines import Line2D

current_directory = os.getcwd()
file_path = current_directory.replace("\\Analysis", "")
save_path = current_directory.replace("\\Analysis", "\\Analysis\\figures")
os.makedirs(save_path, exist_ok=True)

MAX_VALID_RESISTANCE = 2
only_boards = []
# exclude_boards = ["Board 4.1", "Board 4.7", "Board 4.8", "Board 4.9", "Board 4.10"]
exclude_boards = []

# per-board exclusions
impacts_to_exclude = {
    "Board 4.04": [27, 33, 34, 53, 54],
    "Board 4.05": [6, 9, 46, 79],
    "Board 4.06": [21],
}

data_list = sorted([d for d in os.listdir(file_path) if d.startswith("Board")])
impact_numbers_list = []
resistance_numbers_list = []
board_names = []
board_names_trendline = []
board_save_paths = []

for entry in data_list:
    if entry == "Board 0.0":
        continue
    board_dir = os.path.join(file_path, entry)
    if not os.path.isdir(board_dir):
        continue
    board_names.append(entry)
    board_names_trendline.append(entry + " Trendline")
    board_save_paths.append(os.path.join(board_dir, "figures"))
    os.makedirs(board_save_paths[-1], exist_ok=True)

    lvm_files = sorted([f for f in os.listdir(board_dir) if f.endswith(".lvm")])
    impacts = []
    resistances = []
    for j, fname in enumerate(lvm_files):
        fp = os.path.join(board_dir, fname)
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

def board_selected(i):
    if i < 0 or i >= len(board_names):
        return False
    if board_names[i] in exclude_boards:
        return False
    return (not only_boards) or (i in only_boards)

def set_legend(outside=True, below=False, loc="center left"):
    if outside and below:
        plt.legend(bbox_to_anchor=(0.5, -0.25), loc="upper center", ncol=3,
                   facecolor="white", edgecolor="lightgray", framealpha=1, frameon=True)
    elif outside:
        plt.legend(bbox_to_anchor=(1.05, 0.5), loc=loc, borderaxespad=0.,
                   facecolor="white", edgecolor="lightgray", framealpha=1, frameon=True)
    else:
        plt.legend(loc="lower right", facecolor="white", edgecolor="lightgray", framealpha=1, frameon=True)

impacts_to_remove = []
if len(impacts_to_remove) < len(impact_numbers_list):
    impacts_to_remove += [[] for _ in range(len(impact_numbers_list) - len(impacts_to_remove))]

impact_numbers_percents = []
resistance_numbers_percents = []
masks_excluded = []

for i in range(len(impact_numbers_list)):
    xi = impact_numbers_list[i]
    yi = resistance_numbers_list[i]
    n = len(xi)
    if n == 0:
        impact_numbers_percents.append([])
        resistance_numbers_percents.append([])
        masks_excluded.append([])
        continue

    removes = set(impacts_to_remove[i]) if i < len(impacts_to_remove) else set()
    removes.update(impacts_to_exclude.get(board_names[i], []))

    mask = [False] * n
    for idx, imp in enumerate(xi):
        if imp in removes or imp == 0 or imp == 1 or idx == (n - 1):
            mask[idx] = True

    valid_indices = [idx for idx, m in enumerate(mask) if not m]
    if not valid_indices:
        impact_numbers_percents.append([np.nan] * n)
        resistance_numbers_percents.append([np.nan] * n)
        masks_excluded.append(mask)
        continue

    x_valid = [xi[idx] for idx in valid_indices]
    y_valid = [yi[idx] for idx in valid_indices]

    xmin, xmax = min(x_valid), max(x_valid)
    ymin, ymax = min(y_valid), max(y_valid)

    if np.isclose(xmax, xmin):
        x_norm_all = [0.0 for _ in xi]
    else:
        x_norm_all = [((x - xmin) / (xmax - xmin)) * 100 for x in xi]

    if np.isclose(ymax, ymin):
        y_norm_all = [0.0 for _ in yi]
    else:
        y_norm_all = [((y - ymin) / (ymax - ymin)) * 100 for y in yi]

    for idx in range(n):
        if mask[idx]:
            y_norm_all[idx] = np.nan

    impact_numbers_percents.append(x_norm_all)
    resistance_numbers_percents.append(y_norm_all)
    masks_excluded.append(mask)

# anchored exponential fit using only valid (non-nan) points, sorted and explicit
def anchored_eq(x, b):
    return 100 * (1 - np.exp(-b * x)) / (1 - np.exp(-100 * b))

class AnchoredExpRegressor(BaseEstimator, RegressorMixin):
    def __init__(self, b_init=0.05, min_points=3):
        self.b_init = b_init
        self.b_ = None
        self.min_points = min_points
    def fit(self, X, y):
        X = np.asarray(X).ravel()
        y = np.asarray(y).ravel()
        # select only finite (non-nan) entries
        mask = np.isfinite(X) & np.isfinite(y)
        Xf = X[mask]
        yf = y[mask]
        if len(Xf) < self.min_points:
            # not enough data to fit reliably -> fallback to initial guess
            self.b_ = self.b_init
            return self
        # ensure Xf is sorted (curve_fit benefits from monotonic X)
        order = np.argsort(Xf)
        Xf_sorted = Xf[order]
        yf_sorted = yf[order]
        try:
            params, _ = curve_fit(anchored_eq, Xf_sorted, yf_sorted, p0=[self.b_init], maxfev=30000)
            self.b_ = params[0]
        except Exception:
            self.b_ = self.b_init
        return self
    def predict(self, X):
        X = np.asarray(X).ravel()
        return anchored_eq(X, self.b_)

# generate models and corresponding fit lines (explicitly using only non-excluded points)
models = []
fit_line_x_values = []
fit_line_y_values = []
for i in range(len(impact_numbers_percents)):
    X_all = np.array(impact_numbers_percents[i], dtype=float)  # x for every impact (may contain valid numbers)
    Y_all = np.array(resistance_numbers_percents[i], dtype=float)  # y with np.nan for excluded
    model = AnchoredExpRegressor(b_init=0.05, min_points=3)
    model.fit(X_all, Y_all)  # fit uses only finite pairs
    models.append(model)
    xs = np.linspace(0, 100, 1000)
    fit_line_x_values.append(xs)
    fit_line_y_values.append(model.predict(xs))

plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 10

colors = itertools.cycle(plt.cm.tab10.colors)
plt.figure(figsize=(6, 5))
for i in range(len(board_names)):
    if board_selected(i):
        x = impact_numbers_percents[i]
        y = resistance_numbers_percents[i]
        if x and y:
            plt.plot(x, y, marker='.', linestyle='', linewidth=0.8, label=board_names[i], color=next(colors))
plt.xlabel("impact percent")
plt.ylabel("resistance percent")
plt.grid(True)
set_legend(outside=True, below=True)
plt.tight_layout(rect=[0, 0.05, 1, 1])
plt.savefig(os.path.join(save_path, "combined_data_only.png"), dpi=300, bbox_inches='tight')
plt.show()

colors = itertools.cycle(plt.cm.tab10.colors)
plt.figure(figsize=(6.5, 5))
legend_handles, legend_labels = [], []
for i in range(len(board_names)):
    if board_selected(i):
        color = next(colors)
        x = impact_numbers_percents[i]
        y = resistance_numbers_percents[i]
        if x and y:
            plt.plot(x, y, marker='.', linestyle='', linewidth=0.5, color=color)
        if i < len(fit_line_x_values):
            plt.plot(fit_line_x_values[i], fit_line_y_values[i], linewidth=0.8, color=color)
        handle = Line2D([0], [0], marker='.', color=color, linestyle='-', markersize=6, linewidth=0.5)
        legend_handles.append(handle)
        legend_labels.append(board_names[i])
plt.xlabel("impact percent")
plt.ylabel("resistance percent")
plt.grid(True)
plt.legend(legend_handles, legend_labels, bbox_to_anchor=(0.5, -0.25), loc="upper center",
           facecolor="white", edgecolor="lightgray", framealpha=1, frameon=True, ncol=3)
plt.tight_layout(rect=[0, 0.05, 1, 1])
plt.savefig(os.path.join(save_path, "combined_data_and_trendlines.png"), dpi=300, bbox_inches='tight')
plt.show()

colors = itertools.cycle(plt.cm.tab10.colors)
plt.figure(figsize=(6, 5))
for i in range(len(board_names)):
    if board_selected(i) and i < len(fit_line_x_values):
        plt.plot(fit_line_x_values[i], fit_line_y_values[i], linewidth=0.8, label=board_names_trendline[i], color=next(colors))
plt.xlabel("impact percent")
plt.ylabel("resistance percent")
plt.grid(True)
set_legend(outside=True, below=True)
plt.tight_layout(rect=[0, 0.05, 1, 1])
plt.savefig(os.path.join(save_path, "trendlines_only.png"), dpi=300, bbox_inches='tight')
plt.show()

for i in range(len(board_names)):
    if not board_selected(i):
        continue
    x = impact_numbers_percents[i]
    y = resistance_numbers_percents[i]
    xs_fit = fit_line_x_values[i] if i < len(fit_line_x_values) else []
    ys_fit = fit_line_y_values[i] if i < len(fit_line_y_values) else []

    plt.figure(figsize=(6, 3))
    if x and y:
        plt.plot(x, y, marker='.', linestyle='', linewidth=0.8, label=board_names[i])
    if len(xs_fit) and len(ys_fit):
        plt.plot(xs_fit, ys_fit, linewidth=0.8, label=board_names_trendline[i])

    y_arr = np.array(y, dtype=float)
    valid_mask = ~np.isnan(y_arr)
    if np.any(valid_mask):
        y_min = np.nanmin(y_arr[valid_mask])
        y_max = np.nanmax(y_arr[valid_mask])
        pad = 0.05 * (y_max - y_min) if (y_max > y_min) else 1.0
        plt.ylim(y_min - pad, y_max + pad)

    plt.xlabel("impact percent")
    plt.ylabel("resistance percent")
    set_legend(outside=True)
    plt.grid(True)
    plt.tight_layout()
    save_fname = os.path.join(board_save_paths[i], f"{board_names[i]}_data_and_trendline.png")
    plt.savefig(save_fname, dpi=300, bbox_inches='tight')
    plt.show()

print("Included boards (with exclusions):")
for i, name in enumerate(board_names):
    if board_selected(i):
        excluded = impacts_to_exclude.get(name, [])
        if excluded:
            print(f" {i}: {name} (excluded impacts = {excluded})")
        else:
            print(f" {i}: {name}")
