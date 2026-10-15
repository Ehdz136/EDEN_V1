"""EDEN v1.1: measurements and CSV export (standard library only)."""
import csv
from pathlib import Path

FIELDS = [
    'scenario', 'seed', 'day', 'season', 'population', 'food_available',
    'average_hunger', 'average_energy', 'average_trust', 'friends', 'rivals',
    'positive_interactions', 'negative_interactions', 'food_collected_total',
]


def measure(world, scenario, seed):
    agents = world.agents
    trust_values = [rel['trust'] for a in agents for rel in a.relationships.values()]
    friends = sum(rel['trust'] >= 25 for a in agents for rel in a.relationships.values())
    rivals = sum(rel['trust'] <= -40 for a in agents for rel in a.relationships.values())
    positive = sum(rel['positive'] for a in agents for rel in a.relationships.values())
    negative = sum(rel['negative'] for a in agents for rel in a.relationships.values())
    return {
        'scenario': scenario,
        'seed': seed,
        'day': world.day,
        'season': world.season,
        'population': len(agents),
        'food_available': len(world.food),
        'average_hunger': round(sum(a.hunger for a in agents) / len(agents), 2) if agents else 0,
        'average_energy': round(sum(a.energy for a in agents) / len(agents), 2) if agents else 0,
        'average_trust': round(sum(trust_values) / len(trust_values), 2) if trust_values else 0,
        'friends': friends,
        'rivals': rivals,
        'positive_interactions': positive,
        'negative_interactions': negative,
        'food_collected_total': sum(a.food_collected for a in agents),
    }


def save_csv(rows, filename):
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return path
