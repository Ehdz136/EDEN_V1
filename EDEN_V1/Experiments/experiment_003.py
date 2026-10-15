
"""EDEN Experiment 003: Rule-Based vs Learning vs Mixed."""

import csv
import os
import sys
from statistics import mean

# Allow scripts in Experiments/ to import project modules.
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from world import World

SEEDS = [42, 101, 202, 303, 404]
DAYS = 100
MODES = ["rule_based", "learning", "mixed"]

PROJECT_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
OUTPUT_DIR = os.path.join(PROJECT_DIR, "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "experiment_003.csv")


def collect_metrics(world, mode, seed):
    agents = world.agents
    learners = [
        agent for agent in agents
        if agent.learning_enabled
    ]

    return {
        "mode": mode,
        "seed": seed,
        "day": world.day,
        "avg_hunger": mean(a.hunger for a in agents),
        "avg_energy": mean(a.energy for a in agents),
        "total_food_collected": sum(
            a.food_collected for a in agents
        ),
        "avg_food_collected": mean(
            a.food_collected for a in agents
        ),
        "learning_agents": len(learners),
        "q_updates": sum(
            a.learner.updates for a in learners
        ),
    }


def run_experiment():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    results = []

    # Avoid flooding the console with daily agent reports.
    import contextlib
    import io

    for mode in MODES:
        for seed in SEEDS:
            print(f"Running {mode}, seed {seed}...")

            world = World(
                seed=seed,
                learning_mode=mode,
            )

            results.append(
                collect_metrics(world, mode, seed)
            )

            for _ in range(DAYS):
                with contextlib.redirect_stdout(io.StringIO()):
                    world.simulate_day()

                results.append(
                    collect_metrics(world, mode, seed)
                )

    with open(
        OUTPUT_FILE, "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=list(results[0].keys())
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSaved {len(results)} rows to:")
    print(OUTPUT_FILE)

    print("\nDAY 100 RESULTS — AVERAGED ACROSS SEEDS")
    print("-" * 70)

    for mode in MODES:
        final_rows = [
            row for row in results
            if row["mode"] == mode and row["day"] == DAYS
        ]

        print(f"\n{mode.upper()}")
        print(
            f"Average hunger: "
            f"{mean(r['avg_hunger'] for r in final_rows):.2f}"
        )
        print(
            f"Average energy: "
            f"{mean(r['avg_energy'] for r in final_rows):.2f}"
        )
        print(
            f"Food per agent: "
            f"{mean(r['avg_food_collected'] for r in final_rows):.2f}"
        )
        print(
            f"Total Q-updates: "
            f"{mean(r['q_updates'] for r in final_rows):.0f}"
        )


if __name__ == "__main__":
    run_experiment()
