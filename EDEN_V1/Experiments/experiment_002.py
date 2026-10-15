"""EDEN Experiment 002: Does a more cooperative disposition buffer scarcity?

Uses the existing World/Agent logic. No existing EDEN files need editing.
"""
import contextlib
import io
import random
from pathlib import Path

from config import MAX_FOOD
from world import World
from research import measure, save_csv

DAYS = 100
SEEDS = (42, 43, 44, 45, 46)
COOPERATION_BONUS = 0.35
SCENARIOS = {
    'Abundant': {'initial_food': 30, 'daily_food_multiplier': 2.0, 'cooperation_bonus': 0.0},
    'Scarce': {'initial_food': 6, 'daily_food_multiplier': 0.25, 'cooperation_bonus': 0.0},
    'Scarce + Cooperative': {'initial_food': 6, 'daily_food_multiplier': 0.25,
                             'cooperation_bonus': COOPERATION_BONUS},
}


class ExperimentWorld(World):
    """Control food spawning and starting cooperation, not social interaction rules."""

    def __init__(self, initial_food, daily_food_multiplier, cooperation_bonus):
        self._initial_food = initial_food
        self._daily_food_multiplier = daily_food_multiplier
        self._initializing = True
        super().__init__()
        self._initializing = False
        if cooperation_bonus:
            for agent in self.agents:
                # Keep values in the existing personality range [0, 1].
                agent.cooperation = min(1.0, agent.cooperation + cooperation_bonus)

    def spawn_food(self, amount):
        if self._initializing:
            amount = self._initial_food
        else:
            amount = round(amount * self._daily_food_multiplier)
        super().spawn_food(max(0, min(MAX_FOOD, amount)))


def run_one(scenario, settings, seed):
    # Seed BEFORE world creation, matching the original experiment's design.
    random.seed(seed)
    world = ExperimentWorld(**settings)
    rows = [measure(world, scenario, seed)]
    for _ in range(DAYS):
        with contextlib.redirect_stdout(io.StringIO()):
            world.simulate_day()
        rows.append(measure(world, scenario, seed))
    return rows


def main():
    all_rows = []
    print('EDEN / EXPERIMENT 002 — COOPERATION UNDER SCARCITY\n')
    print('Intervention: +0.35 to starting cooperation, capped at 1.0.')
    print('Food settings are identical for both scarce scenarios.\n')
    for seed in SEEDS:
        for name, settings in SCENARIOS.items():
            rows = run_one(name, settings, seed)
            all_rows.extend(rows)
            final = rows[-1]
            print(f"{name:20s} | seed={seed} | day={final['day']} | "
                  f"hunger={final['average_hunger']:5.1f} | "
                  f"trust={final['average_trust']:+6.1f} | "
                  f"friends={final['friends']:2d} | rivals={final['rivals']:2d}")
    output = Path(__file__).resolve().parent.parent / 'data' / 'experiment_002.csv'
    path = save_csv(all_rows, output)
    print(f'\nSaved {len(all_rows)} daily measurements to {path.resolve()}')
    print('Friend/rival counts are directed relationships.')
    print('Important: this tests a changed personality parameter, not learned cooperation.')


if __name__ == '__main__':
    main()
