"""EDEN v1.1: compare resource conditions with paired random seeds.

Run this file in Visual Studio 2022. It does not modify the Tkinter dashboard.
"""
import contextlib
import io
import random

from world import World
from config import MAX_FOOD
from research import measure, save_csv

DAYS = 100
SEEDS = [42, 43, 44, 45, 46]
SCENARIOS = {
    'Abundant': {'initial_food': 30, 'daily_food_multiplier': 2.0},
    'Scarce': {'initial_food': 6, 'daily_food_multiplier': 0.25},
}


class ExperimentWorld(World):
    """Override only food spawning, leaving existing EDEN behavior unchanged."""

    def __init__(self, initial_food, daily_food_multiplier):
        self._initial_food = initial_food
        self._daily_food_multiplier = daily_food_multiplier
        self._initializing = True
        super().__init__()
        self._initializing = False

    def spawn_food(self, amount):
        if self._initializing:
            target = self._initial_food
        else:
            target = round(amount * self._daily_food_multiplier)
        # Honor the world capacity, even if the preset asks for more.
        super().spawn_food(max(0, min(MAX_FOOD, target)))


def run_experiment(scenario_name, settings, seed, days=DAYS):
    # Works with the current World() and with World(seed=None).
    # This uses Python's global random generator, as current EDEN does.
    random.seed(seed)
    world = ExperimentWorld(**settings)
    rows = [measure(world, scenario_name, seed)]
    for _ in range(days):
        # The existing simulation prints every agent each day. Suppress that
        # output for batch experiments without changing world.py.
        with contextlib.redirect_stdout(io.StringIO()):
            world.simulate_day()
        rows.append(measure(world, scenario_name, seed))
    return rows


def main():
    all_rows = []
    for seed in SEEDS:
        for name, settings in SCENARIOS.items():
            rows = run_experiment(name, settings, seed)
            all_rows.extend(rows)
            final = rows[-1]
            print(f"{name:8s} | seed={seed} | day={final['day']} | "
                  f"hunger={final['average_hunger']:5.1f} | "
                  f"trust={final['average_trust']:+6.1f} | "
                  f"friends={final['friends']:2d} | rivals={final['rivals']:2d}")
    path = save_csv(all_rows, 'data/experiment_001.csv')
    print(f'\nSaved {len(all_rows)} daily measurements to {path.resolve()}')
    print('Note: friend/rival counts are directed agent-to-agent relationships.')


if __name__ == '__main__':
    main()
