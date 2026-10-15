"""Run a small EDEN simulation and inspect one agent's recorded life events."""
import contextlib
import io
from pathlib import Path
from world import World

world = World(seed=42)
with contextlib.redirect_stdout(io.StringIO()):
    for _ in range(30):
        world.simulate_day()

subject = world.agents[0]
print('EDEN / SUBJECT 000 / EPISODIC MEMORY')
print(f'Day {world.day} | {len(subject.episodes.events)} recorded events\n')
print(subject.episodes.journal(limit=20))

output = Path(__file__).resolve().parent / 'data' / 'subject_000_episodes.json'
subject.episodes.export_json(output)
print(f'\nSaved episode archive to {output}')
