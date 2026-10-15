
# ==========================================
# EDEN - CONFIGURATION
# ==========================================

WORLD_SIZE = 10
NUM_AGENTS = 10
NUM_FOOD = 20
SIMULATION_DAYS = 60

# Each season lasts 10 simulation days
DAYS_PER_SEASON = 10

# Maximum food locations allowed in the world
MAX_FOOD = 35

# New food generated each day, by season
FOOD_GROWTH = {
    "Spring": 4,
    "Summer": 3,
    "Autumn": 2,
    "Winter": 1
}
