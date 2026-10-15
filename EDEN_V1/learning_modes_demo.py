from world import World

for mode in ("rule_based", "learning", "mixed"):
    world = World(seed=42, learning_mode=mode)
    learning_agents = [a for a in world.agents if a.learning_enabled]
    print(f"\nMODE: {mode}")
    print(f"Agents: {len(world.agents)} | Learning agents: {len(learning_agents)}")
    for _ in range(10):
        world.simulate_day()
    print(f"Total Q-updates: {sum(a.learner.updates for a in learning_agents)}")
