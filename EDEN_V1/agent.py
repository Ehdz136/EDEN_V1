import random
from config import WORLD_SIZE
from episodic_memory import EpisodicMemory


class Agent:
    def __init__(self, agent_id, x, y):
        self.id = agent_id
        self.x = x
        self.y = y
        self.energy = 100
        self.hunger = 0
        self.curiosity = random.random()
        self.sociability = random.random()
        self.cooperation = random.random()
        self.food_memory = set()
        self.long_term_memory = set()
        self.vision_range = 2
        self.food_collected = 0
        self.last_action = "None"
        self.social_memory = {}
        self.nearby_agents = []
        self.relationships = {}
        self.episodes = EpisodicMemory(capacity=200)

    def perceive(self, world):
        for food_x, food_y in world.food:
            distance = abs(self.x - food_x) + abs(self.y - food_y)
            if distance <= self.vision_range:
                position = (food_x, food_y)
                self.food_memory.add(position)
                self.long_term_memory.add(position)
        for position in list(self.food_memory):
            distance = abs(self.x - position[0]) + abs(self.y - position[1])
            if distance <= self.vision_range and position not in world.food:
                self.food_memory.remove(position)

    def perceive_agents(self, world):
        self.nearby_agents = []
        for other in world.agents:
            if other.id == self.id:
                continue
            distance = abs(self.x - other.x) + abs(self.y - other.y)
            if distance <= self.vision_range:
                self.nearby_agents.append(other.id)
                if other.id not in self.social_memory:
                    self.social_memory[other.id] = {
                        "encounters": 0,
                        "first_met": world.day,
                        "last_seen": -1,
                    }
                    self.episodes.remember(
                        world.day, "first_meeting",
                        f"First encountered Subject {other.id:03d}.",
                        other.id, 2)
                memory = self.social_memory[other.id]
                if memory["last_seen"] != world.day:
                    memory["encounters"] += 1
                    memory["last_seen"] = world.day
                self.relationships.setdefault(other.id, {
                    "trust": 0.0,
                    "positive": 0,
                    "negative": 0,
                    "last_interaction": "None",
                })

    def relationship_label(self, other_id):
        relationship = self.relationships.get(other_id)
        if relationship is None:
            return "Stranger"
        trust = relationship["trust"]
        if trust >= 60:
            return "Close friend"
        if trust >= 25:
            return "Friend"
        if trust <= -40:
            return "Rival"
        if trust <= -15:
            return "Wary"
        return "Acquaintance"

    def adjust_trust(self, other_id, change, event):
        relationship = self.relationships.setdefault(other_id, {
            "trust": 0.0,
            "positive": 0,
            "negative": 0,
            "last_interaction": "None",
        })
        relationship["trust"] = round(max(-100, min(100, relationship["trust"] + change)), 1)
        if change > 0:
            relationship["positive"] += 1
        elif change < 0:
            relationship["negative"] += 1
        relationship["last_interaction"] = event

    def decide(self):
        explore_score = self.curiosity * 50
        rest_score = (100 - self.energy) * 1.5
        food_score = self.hunger * 1.5
        if self.food_memory:
            food_score += 20
        scores = {"explore": explore_score, "rest": rest_score, "find_food": food_score}
        return max(scores, key=scores.get)

    def move(self):
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.x = max(0, min(WORLD_SIZE - 1, self.x + dx))
        self.y = max(0, min(WORLD_SIZE - 1, self.y + dy))

    def move_toward(self, target):
        target_x, target_y = target
        if self.x < target_x:
            self.x += 1
        elif self.x > target_x:
            self.x -= 1
        elif self.y < target_y:
            self.y += 1
        elif self.y > target_y:
            self.y -= 1

    def act(self, world):
        self.perceive(world)
        action = self.decide()
        self.last_action = action

        if action == "explore":
            self.move()
            self.energy -= 5
            self.hunger += 3
        elif action == "rest":
            self.energy += 10
            self.hunger += 1
        elif action == "find_food":
            if self.food_memory:
                target = min(self.food_memory, key=lambda pos: abs(self.x - pos[0]) + abs(self.y - pos[1]))
                self.move_toward(target)
            else:
                self.move()
            self.energy -= 3
            self.hunger += 2

        position = (self.x, self.y)
        if position in world.food:
            world.food.remove(position)
            self.food_memory.discard(position)
            self.long_term_memory.add(position)
            self.hunger -= 30
            self.energy += 15
            self.food_collected += 1
            self.last_action = "eat"
            self.episodes.remember(
                world.day, "food",
                f"Found and ate food at ({self.x}, {self.y}).", importance=2)

        self.energy = max(0, min(100, self.energy))
        self.hunger = max(0, min(100, self.hunger))

    def status(self):
        return (
            f"Agent {self.id:02d} | Position: ({self.x}, {self.y}) | "
            f"Energy: {self.energy:3d} | Hunger: {self.hunger:3d} | "
            f"Food: {self.food_collected:2d} | "
            f"Known Food: {len(self.food_memory):2d} | "
            f"Past Locations: {len(self.long_term_memory):2d} | "
            f"Action: {self.last_action}"
        )
