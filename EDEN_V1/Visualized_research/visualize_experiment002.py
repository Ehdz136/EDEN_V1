"""EDEN v1.1.1 — Research Dashboard.

Reads data/experiment_002.csv from the project directory and plots daily averages
across seeds. Uses only Python's standard library (Tkinter, csv, statistics).
Run this file directly; it does not modify the EDEN simulation or visualizer.
"""
import csv
import statistics
import tkinter as tk
from collections import defaultdict
from pathlib import Path
from tkinter import messagebox

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_FILE = PROJECT_ROOT / "data" / "experiment_002.csv"
METRICS = [
    ('average_trust', 'Average trust', 'Trust score'),
    ('friends', 'Friendships', 'Directed relationships'),
    ('rivals', 'Rivalries', 'Directed relationships'),
    ('average_hunger', 'Average hunger', 'Hunger level'),
]
COLORS = {'Abundant': '#2bbf9a', 'Scarce': '#f08a73', 'Scarce + Cooperative': '#a99bff'}
BACKGROUND = '#101821'
PANEL = '#192431'
TEXT = '#eaf1f7'
MUTED = '#9aaabc'
GRID = '#344250'


def read_data(path):
    if not path.exists():
        raise FileNotFoundError(
            f'Cannot find {path.name} in:\n{path.parent}\n\n'
            'Run experiment_002.py first, or copy experiment_002.csv into '
            'the data folder beside visualize_experiment_002.py.'
        )
    grouped = defaultdict(list)
    with path.open(newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        needed = {'scenario', 'seed', 'day'} | {metric[0] for metric in METRICS}
        missing = needed - set(reader.fieldnames or [])
        if missing:
            raise ValueError('CSV is missing columns: ' + ', '.join(sorted(missing)))
        for row in reader:
            scenario = row['scenario'].strip()
            day = int(row['day'])
            seed = row['seed'].strip()
            for metric, _, _ in METRICS:
                grouped[(scenario, day, metric)].append((seed, float(row[metric])))
    if not grouped:
        raise ValueError('The CSV contains no measurements.')
    # Each (scenario, day) point averages the observed seeds for that day.
    means = {key: statistics.mean(value for _, value in readings)
             for key, readings in grouped.items()}
    scenarios = sorted({key[0] for key in means},
                       key=lambda s: (s != 'Abundant', s != 'Scarce', s))
    days = sorted({key[1] for key in means})
    seeds = {scenario: len({seed for (s, day, _), readings in grouped.items()
                            if s == scenario and day == days[-1]
                            for seed, _ in readings}) for scenario in scenarios}
    return means, scenarios, days, seeds


class ResearchDashboard:
    def __init__(self, root, means, scenarios, days, seeds):
        self.root = root
        self.means = means
        self.scenarios = scenarios
        self.days = days
        self.seeds = seeds
        self.hover = None
        self.root.title('EDEN | Experiment Lab — Research Dashboard')
        self.root.geometry('1150x800')
        self.root.minsize(760, 560)
        self.root.configure(bg=BACKGROUND)

        heading = tk.Frame(root, bg=BACKGROUND)
        heading.pack(fill='x', padx=22, pady=(18, 4))
        tk.Label(heading, text='EDEN  /  EXPERIMENT LAB', bg=BACKGROUND,
                 fg=TEXT, font=('Segoe UI', 20, 'bold')).pack(anchor='w')
        tk.Label(heading,
                 text=f'100-day cooperation experiment  •  {len(scenarios)} scenarios  •  '
                      f'{len(days)} recorded days  •  means across seeds',
                 bg=BACKGROUND, fg=MUTED, font=('Segoe UI', 10)).pack(anchor='w')

        legend = tk.Frame(root, bg=BACKGROUND)
        legend.pack(fill='x', padx=24, pady=(5, 9))
        for scenario in scenarios:
            color = COLORS.get(scenario, '#a9a0ff')
            tk.Label(legend, text='━', bg=BACKGROUND, fg=color,
                     font=('Segoe UI', 15, 'bold')).pack(side='left')
            tk.Label(legend, text=f'{scenario} ({seeds[scenario]} seeds)   ',
                     bg=BACKGROUND, fg=TEXT,
                     font=('Segoe UI', 10)).pack(side='left')

        self.canvas = tk.Canvas(root, bg=BACKGROUND, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True, padx=12, pady=(0, 6))
        self.canvas.bind('<Configure>', lambda _: self.draw())
        self.canvas.bind('<Motion>', self.on_hover)
        self.canvas.bind('<Leave>', lambda _: self.clear_hover())
        self.status = tk.Label(root,
                               text='Hover over a chart to inspect the average values at a simulated day.',
                               bg=BACKGROUND, fg=MUTED, anchor='w',
                               font=('Segoe UI', 10))
        self.status.pack(fill='x', padx=24, pady=(0, 15))
        self.plots = []

    def draw(self):
        canvas = self.canvas
        canvas.delete('all')
        self.plots = []
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width < 100 or height < 100:
            return
        margin, gap = 10, 14
        panel_w = (width - 2 * margin - gap) / 2
        panel_h = (height - 2 * margin - gap) / 2
        for i, (metric, title, unit) in enumerate(METRICS):
            col, row = i % 2, i // 2
            x0 = margin + col * (panel_w + gap)
            y0 = margin + row * (panel_h + gap)
            self.draw_panel(x0, y0, panel_w, panel_h, metric, title, unit)

    def draw_panel(self, x0, y0, w, h, metric, title, unit):
        c = self.canvas
        c.create_rectangle(x0, y0, x0 + w, y0 + h,
                           fill=PANEL, outline=PANEL)
        c.create_text(x0 + 17, y0 + 22, anchor='w', text=title,
                      fill=TEXT, font=('Segoe UI', 12, 'bold'))
        left, right = x0 + 62, x0 + w - 20
        top, bottom = y0 + 57, y0 + h - 43
        if right <= left or bottom <= top:
            return
        values = [value for (scenario, day, name), value in self.means.items()
                  if name == metric]
        low, high = min(values), max(values)
        low = min(0.0, low)
        if high == low:
            high = low + 1
        padding = (high - low) * 0.08
        low -= padding
        high += padding
        min_day, max_day = self.days[0], self.days[-1]
        span = max(1, max_day - min_day)

        def x_coord(day):
            return left + (day - min_day) / span * (right - left)

        def y_coord(value):
            return bottom - (value - low) / (high - low) * (bottom - top)

        for j in range(5):
            val = low + j * (high - low) / 4
            y = y_coord(val)
            c.create_line(left, y, right, y, fill=GRID, dash=(2, 4))
            c.create_text(left - 9, y, anchor='e', text=f'{val:.0f}' if abs(val) >= 10 else f'{val:.1f}',
                          fill=MUTED, font=('Segoe UI', 8))
        for j in range(5):
            day = min_day + j * span / 4
            x = x_coord(day)
            c.create_text(x, bottom + 17, text=f'{day:.0f}',
                          fill=MUTED, font=('Segoe UI', 8))
        c.create_text((left + right) / 2, y0 + h - 11, text='Simulated day',
                      fill=MUTED, font=('Segoe UI', 8))
        for scenario in self.scenarios:
            points = [(day, self.means[(scenario, day, metric)])
                      for day in self.days if (scenario, day, metric) in self.means]
            coords = [v for day, value in points for v in (x_coord(day), y_coord(value))]
            if len(coords) >= 4:
                c.create_line(*coords, fill=COLORS.get(scenario, '#a9a0ff'),
                              width=2.6, smooth=False)
            elif len(coords) == 2:
                c.create_oval(coords[0]-2, coords[1]-2, coords[0]+2, coords[1]+2,
                              fill=COLORS.get(scenario, '#a9a0ff'), outline='')
        self.plots.append((left, top, right, bottom, metric, min_day, max_day))

    def clear_hover(self):
        self.canvas.delete('hover')
        self.status.config(text='Hover over a chart to inspect the average values at a simulated day.')

    def on_hover(self, event):
        self.canvas.delete('hover')
        for left, top, right, bottom, metric, first, last in self.plots:
            if left <= event.x <= right and top <= event.y <= bottom:
                target = first + (event.x - left) / (right - left) * (last - first)
                day = min(self.days, key=lambda d: abs(d - target))
                x = left + (day - first) / max(1, last - first) * (right - left)
                self.canvas.create_line(x, top, x, bottom, fill='#c5d0dc',
                                        dash=(3, 3), tags='hover')
                parts = [f'Day {day}  |  {metric.replace("_", " ").title()}']
                for scenario in self.scenarios:
                    value = self.means.get((scenario, day, metric))
                    if value is not None:
                        parts.append(f'{scenario}: {value:.2f}')
                self.status.config(text='    •    '.join(parts))
                return
        self.clear_hover()


def main():
    root = tk.Tk()
    try:
        means, scenarios, days, seeds = read_data(CSV_FILE)
    except (OSError, ValueError, KeyError) as exc:
        root.withdraw()
        messagebox.showerror('EDEN — Data error', str(exc))
        root.destroy()
        return
    ResearchDashboard(root, means, scenarios, days, seeds)
    root.mainloop()


if __name__ == '__main__':
    main()
