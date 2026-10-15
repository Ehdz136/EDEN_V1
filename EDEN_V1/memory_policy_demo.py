"""Quick check: compare the same seed with and without memory influence."""
import contextlib
import io
import world as world_module
from world import World
from memory_policy import memory_influence

def run(seed):
    simulation = World(seed=seed)
    with contextlib.redirect_stdout(io.StringIO()):
        for _ in range(30):
            simulation.simulate_day()
    a = simulation.agents[0]
    print(f"Seed {seed} | Day {simulation.day} | Agent 000 episodes: {len(a.episodes.events)}")
    for other_id in sorted(a.relationships)[:5]:
        print(f"  Subject {other_id:03d}: trust={a.relationships[other_id]['trust']:+.1f}, "
              f"memory modifier={memory_influence(a, other_id):+.3f}")
    return simulation

if __name__ == "__main__":
    run(42)
