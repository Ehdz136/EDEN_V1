
from config import (
    WORLD_SIZE,
    NUM_AGENTS,
    NUM_FOOD,
    SIMULATION_DAYS
)
from world import World


def main():
    world = World()

    print("=" * 50)
    print("WELCOME TO EDEN")
    print("Artificial Civilization Simulation")
    print("=" * 50)

    print(f"\nWorld size: {WORLD_SIZE}x{WORLD_SIZE}")
    print(f"Population: {NUM_AGENTS}")
    print(f"Initial food locations: {NUM_FOOD}")
    print(f"Simulation length: {SIMULATION_DAYS} days")

    for _ in range(SIMULATION_DAYS):
        world.simulate_day()

    print("\n" + "=" * 50)
    print("EDEN GENESIS SIMULATION COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    main()
