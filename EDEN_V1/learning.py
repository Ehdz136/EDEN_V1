
"""EDEN v1.3.0 — Tabular Q-learning engine."""

import random

ACTIONS = ("explore", "rest", "find_food")


class QLearner:
    def __init__(self, learning_rate=0.15, discount=0.90, epsilon=0.20):
        self.learning_rate = learning_rate
        self.discount = discount
        self.epsilon = epsilon
        self.q_table = {}
        self.updates = 0

    @staticmethod
    def state(agent):
        def level(value):
            if value < 34:
                return "low"
            if value < 67:
                return "medium"
            return "high"

        return (
            level(agent.hunger),
            level(agent.energy),
            bool(agent.food_memory),
        )

    def value(self, state, action):
        return self.q_table.get((state, action), 0.0)

    def choose_action(self, state):
        # Explore occasionally rather than always choosing
        # the action with the highest estimated value.
        if random.random() < self.epsilon:
            return random.choice(ACTIONS)

        values = [self.value(state, action) for action in ACTIONS]
        best = max(values)

        # Randomize ties to avoid always favoring "explore".
        tied = [
            action
            for action, value in zip(ACTIONS, values)
            if value == best
        ]
        return random.choice(tied)

    def update(self, state, action, reward, next_state):
        old = self.value(state, action)

        future = max(
            self.value(next_state, candidate)
            for candidate in ACTIONS
        )

        target = reward + self.discount * future

        self.q_table[(state, action)] = (
            old + self.learning_rate * (target - old)
        )

        self.updates += 1
        return self.q_table[(state, action)]
