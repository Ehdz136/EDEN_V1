"""EDEN Experiment 003 — Research Dashboard.

Reads data/experiment_003.csv produced by Experiments/experiment_003.py.
No external dependencies beyond matplotlib and standard-library Tkinter.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_ROOT / "data" / "experiment_003.csv"

MODES = ("rule_based", "learning", "mixed")
LABELS = {"rule_based": "Rule-Based", "learning": "Learning", "mixed": "Mixed"}
COLORS = {"rule_based": "#e9a35a", "learning": "#67d7c4", "mixed": "#a5a5f5"}
METRICS = (
    ("avg_hunger", "Average Hunger", "Hunger (lower is better)"),
    ("avg_energy", "Average Energy", "Energy (higher is better)"),
    ("avg_food_collected", "Food Collected per Agent", "Cumulative food per agent"),
    ("q_updates", "Q-Learning Updates", "Cumulative updates per civilization"),
)


def load_data(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Could not find {path}\n\nRun Experiments/experiment_003.py first.")

    grouped = defaultdict(list)
    seeds = defaultdict(set)
    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        required = {"mode", "seed", "day"} | {metric[0] for metric in METRICS}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError("Missing CSV columns: " + ", ".join(sorted(missing)))
        for row in reader:
            mode = row["mode"].strip()
            if mode not in MODES:
                continue
            day = int(row["day"])
            seed = row["seed"]
            values = {metric: float(row[metric]) for metric, _, _ in METRICS}
            grouped[(mode, day)].append(values)
            seeds[mode].add(seed)

    if not grouped:
        raise ValueError("The CSV contains no recognized experiment modes.")

    averaged = {}
    for key, rows in grouped.items():
        averaged[key] = {
            metric: sum(row[metric] for row in rows) / len(rows)
            for metric, _, _ in METRICS
        }
    return averaged, seeds


class ResearchDashboard:
    def __init__(self, root, data, seeds):
        self.root = root
        self.data = data
        self.seeds = seeds
        root.title("EDEN | Experiment 003 — Learning vs Rules")
        root.geometry("1350x880")
        root.minsize(1000, 680)
        root.configure(bg="#101820")

        header = tk.Frame(root, bg="#101820")
        header.pack(fill="x", padx=24, pady=(18, 8))
        tk.Label(header, text="EDEN  /  RESEARCH ARCHIVE", font=("Segoe UI", 11, "bold"),
                 fg="#67d7c4", bg="#101820").pack(anchor="w")
        tk.Label(header, text="EXPERIMENT 003 — LEARNING VS. RULES",
                 font=("Segoe UI", 21, "bold"), fg="#f1f5f9", bg="#101820").pack(anchor="w", pady=(4, 0))
        counts = ", ".join(f"{LABELS[mode]}: {len(seeds[mode])} seeds" for mode in MODES)
        tk.Label(header, text=f"Mean values across simulation seeds  •  {counts}",
                 font=("Segoe UI", 10), fg="#aab8c5", bg="#101820").pack(anchor="w", pady=(4, 0))

        fig = Figure(figsize=(12, 7), dpi=100, facecolor="#101820")
        axes = fig.subplots(2, 2)
        for ax, (metric, title, ylabel) in zip(axes.flat, METRICS):
            ax.set_facecolor("#182530")
            for mode in MODES:
                days = sorted(day for m, day in data if m == mode)
                values = [data[(mode, day)][metric] for day in days]
                if days:
                    ax.plot(days, values, label=LABELS[mode], color=COLORS[mode], linewidth=2)
            ax.set_title(title, color="#f1f5f9", fontsize=12, fontweight="bold", pad=12)
            ax.set_xlabel("Simulation Day", color="#aab8c5", fontsize=9)
            ax.set_ylabel(ylabel, color="#aab8c5", fontsize=9)
            ax.tick_params(colors="#aab8c5", labelsize=9)
            ax.grid(color="#3b5060", alpha=0.35)
            for spine in ax.spines.values():
                spine.set_color("#3b5060")
            legend = ax.legend(loc="best", fontsize=8, facecolor="#182530", edgecolor="#3b5060")
            for label in legend.get_texts():
                label.set_color("#f1f5f9")
        fig.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.09, hspace=0.40, wspace=0.25)

        plot_frame = tk.Frame(root, bg="#101820")
        plot_frame.pack(fill="both", expand=True, padx=16)
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        footer = tk.Frame(root, bg="#101820")
        footer.pack(fill="x", padx=24, pady=(4, 16))
        final_day = max(day for _, day in data)
        summaries = []
        for mode in MODES:
            row = data.get((mode, final_day))
            if row:
                summaries.append(
                    f"{LABELS[mode]}  |  Hunger {row['avg_hunger']:.2f}  "
                    f"Energy {row['avg_energy']:.2f}  Food/agent {row['avg_food_collected']:.2f}"
                )
        tk.Label(footer, text=f"DAY {final_day} SUMMARY", fg="#67d7c4", bg="#101820",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        for summary in summaries:
            tk.Label(footer, text=summary, fg="#f1f5f9", bg="#101820",
                     font=("Consolas", 10)).pack(anchor="w", pady=1)
        tk.Label(footer, text="Note: Results are descriptive averages; Q-updates measure training activity, not learning quality.",
                 fg="#aab8c5", bg="#101820", font=("Segoe UI", 9)).pack(anchor="w", pady=(5, 0))


def main():
    root = tk.Tk()
    try:
        data, seeds = load_data(CSV_PATH)
    except (OSError, ValueError) as exc:
        root.withdraw()
        messagebox.showerror("EDEN Research Dashboard", str(exc))
        root.destroy()
        return
    ResearchDashboard(root, data, seeds)
    root.mainloop()


if __name__ == "__main__":
    main()
