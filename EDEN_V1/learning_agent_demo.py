
from world import World

world = World(seed=42)

# Enable learning for Subject 000 only.
agent = world.agents[0]
agent.learning_enabled = True

from learning import QLearner
agent.learner = QLearner()

print("EDEN LEARNING AGENT TEST")
print("------------------------")

for _ in range(30):
    world.simulate_day()

print("\nLEARNING RESULTS")
print("Subject:", agent.id)
print("Last decision:", agent.last_decision)
print("Last reward:", agent.last_reward)
print("Q-learning updates:", agent.learner.updates)
print("Learned state-action values:", len(agent.learner.q_table))

print("\nLEARNED Q-VALUES")
for (state, action), value in sorted(agent.learner.q_table.items()):
    print(f"{state} | {action:10s} | Q = {value:+.3f}")
