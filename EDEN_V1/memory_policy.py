"""EDEN v1.2.2: transparent, rule-based memory-informed social decisions.

Only recorded social episodes affect the modifier. The output is a probability
adjustment, not a learned model or a claim about agents' emotions.
"""

POSITIVE_KINDS = {"positive_encounter", "shared_food_knowledge"}
NEGATIVE_KINDS = {"disagreement"}

def memory_influence(agent, other_id, limit=5):
    """Return a bounded modifier between -0.08 and +0.08.

    More recent recorded social events count more heavily. This deliberately
    does not replace the existing trust score; it adds a short-term history
    signal that can differ even when two agents have similar overall trust.
    """
    events = agent.episodes.recall(other_id=other_id, limit=limit)
    total = 0.0
    weight_total = 0.0
    for index, episode in enumerate(events, start=1):
        if episode.kind in POSITIVE_KINDS:
            value = 1.0
        elif episode.kind in NEGATIVE_KINDS:
            value = -1.0
        else:
            continue
        weight = index  # newest event has the greatest weight
        total += value * weight
        weight_total += weight
    if not weight_total:
        return 0.0
    return round(0.08 * total / weight_total, 4)
