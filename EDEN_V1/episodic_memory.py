"""Structured episodic memory for EDEN. No external dependencies."""
from dataclasses import dataclass, asdict
from typing import Optional
from collections import deque
import json

@dataclass(frozen=True)
class Episode:
    day: int
    kind: str
    description: str
    other_id: Optional[int] = None
    importance: int = 1

class EpisodicMemory:
    def __init__(self, capacity=200):
        self.events = deque(maxlen=capacity)

    def remember(self, day, kind, description, other_id=None, importance=1):
        self.events.append(Episode(day, kind, description, other_id, importance))

    def recall(self, kind=None, other_id=None, limit=10):
        events = [e for e in self.events
                  if (kind is None or e.kind == kind)
                  and (other_id is None or e.other_id == other_id)]
        return events[-limit:]

    def journal(self, limit=12):
        entries = self.recall(limit=limit)
        if not entries:
            return "No recorded experiences yet."
        return "\n".join(f"Day {e.day}: {e.description}" for e in entries)

    def export_json(self, path):
        from pathlib import Path
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps([asdict(e) for e in self.events], indent=2),
                        encoding="utf-8")
