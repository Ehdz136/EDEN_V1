
from learning import QLearner

learner = QLearner()

state = ("high", "medium", True)
next_state = ("medium", "medium", True)

print("Initial Q-value:", learner.value(state, "find_food"))

learner.update(
    state=state,
    action="find_food",
    reward=10,
    next_state=next_state,
)

print("Updated Q-value:", learner.value(state, "find_food"))
print("Total updates:", learner.updates)
