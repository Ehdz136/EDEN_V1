import random
from agent import Agent
from memory_policy import memory_influence
from config import WORLD_SIZE, NUM_AGENTS, NUM_FOOD, DAYS_PER_SEASON, MAX_FOOD, FOOD_GROWTH


class World:
    def __init__(self, seed=None, learning_mode="rule_based"):
        valid_modes = {"rule_based", "learning", "mixed"}
        if learning_mode not in valid_modes:
            raise ValueError(f"learning_mode must be one of {sorted(valid_modes)}")
        if seed is not None:
            random.seed(seed)
        self.learning_mode = learning_mode
        self.day = 0
        self.season = "Spring"
        self.agents = [
            Agent(
                agent_id,
                random.randrange(WORLD_SIZE),
                random.randrange(WORLD_SIZE),
                learning_enabled=(
                    learning_mode == "learning"
                    or (learning_mode == "mixed" and agent_id % 2 == 0)
                ),
            )
            for agent_id in range(NUM_AGENTS)
        ]
        self.food = set()
        self.spawn_food(NUM_FOOD)
        self.social_events = []

    def spawn_food(self, amount):
        for _ in range(amount):
            if len(self.food) >= MAX_FOOD:
                break
            available = [
                (x, y)
                for x in range(WORLD_SIZE)
                for y in range(WORLD_SIZE)
                if (x, y) not in self.food
            ]
            if not available:
                break
            self.food.add(random.choice(available))

    def update_season(self):
        seasons = ["Spring", "Summer", "Autumn", "Winter"]
        self.season = seasons[((self.day - 1) // DAYS_PER_SEASON) % len(seasons)]

    def interact(self, first, second):
        difference = (
            abs(first.curiosity - second.curiosity)
            + abs(first.sociability - second.sociability)
            + abs(first.cooperation - second.cooperation)
        ) / 3
        compatibility = 1 - difference
        scarcity = 1 - len(self.food) / max(1, MAX_FOOD)
        hunger_pressure = (first.hunger + second.hunger) / 200
        prior_trust = (
            first.relationships[second.id]["trust"]
            + second.relationships[first.id]["trust"]
        ) / 200

        positive_chance = (
            0.25 + 0.30 * compatibility
            + 0.15 * ((first.cooperation + second.cooperation) / 2)
            + 0.10 * prior_trust
            - 0.20 * scarcity * hunger_pressure
        )
        history_modifier = (
            memory_influence(first, second.id)
            + memory_influence(second, first.id)
        ) / 2
        positive_chance += history_modifier
        positive_chance = max(0.10, min(0.90, positive_chance))

        if random.random() < positive_chance:
            first_gain = random.uniform(2, 6) * (0.6 + first.sociability)
            second_gain = random.uniform(2, 6) * (0.6 + second.sociability)
            first.adjust_trust(second.id, first_gain, "Positive encounter")
            second.adjust_trust(first.id, second_gain, "Positive encounter")
            event = "positive encounter"

            share_chance = 0.15 + 0.40 * ((first.cooperation + second.cooperation) / 2)
            if random.random() < share_chance:
                first_known = first.food_memory & self.food
                second_known = second.food_memory & self.food
                first.food_memory.update(second_known)
                second.food_memory.update(first_known)
                first.long_term_memory.update(second_known)
                second.long_term_memory.update(first_known)
                first.adjust_trust(second.id, 2, "Shared food knowledge")
                second.adjust_trust(first.id, 2, "Shared food knowledge")
                event = "shared food knowledge"
        else:
            first_loss = random.uniform(1, 5) * (0.7 + hunger_pressure)
            second_loss = random.uniform(1, 5) * (0.7 + hunger_pressure)
            first.adjust_trust(second.id, -first_loss, "Disagreement")
            second.adjust_trust(first.id, -second_loss, "Disagreement")
            event = "disagreement"

        for agent, other in ((first, second), (second, first)):
            agent.episodes.remember(
                self.day, event.replace(" ", "_"),
                f"Had a {event} with Subject {other.id:03d}; "
                f"trust is now {agent.relationships[other.id]['trust']:+.1f}.",
                other.id, 3 if event == "disagreement" else 2)

        self.social_events.append(f"Subjects {first.id:03d} and {second.id:03d}: {event}")

    def simulate_day(self):
        self.day += 1
        self.update_season()
        self.spawn_food(FOOD_GROWTH[self.season])

        for agent in self.agents:
            agent.act(self)

        for agent in self.agents:
            agent.perceive_agents(self)

        self.social_events = []
        for i, first in enumerate(self.agents):
            for second in self.agents[i + 1:]:
                if second.id in first.nearby_agents:
                    self.interact(first, second)

        print(f"\nDAY {self.day} | {self.season}")
        for agent in self.agents:
            print(agent.status())
        print(f"Food remaining: {len(self.food)}")
        print(f"Total food collected: {sum(a.food_collected for a in self.agents)}")
        if self.agents:
            print(f"Average hunger: {sum(a.hunger for a in self.agents) / len(self.agents):.1f}")
        for event in self.social_events:
            print("SOCIAL:", event)
