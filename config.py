# ── Universe 25 Simulation Configuration ──────────────────────────────────────

# Window
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Universe 25 Simulation"
FPS = 60

# Agents
AGENT_COUNT = 150
AGENT_RADIUS = 4
MAX_SPEED = 120.0          # pixels per second
WANDER_STRENGTH = 200.0    # random acceleration magnitude (pixels/s²)

# Hunger
HUNGER_RATE = 5.0              # hunger increase per second
HUNGER_THRESHOLD = 50.0        # hunger level that triggers food-seeking
MAX_HUNGER = 100.0             # maximum hunger value
HUNGER_RESTORE = 60.0          # hunger reduction when eating
SEEK_SPEED_MULTIPLIER = 1.3    # speed boost when seeking food

# Food
FOOD_COUNT = 75
FOOD_RADIUS = 3
EAT_DISTANCE = 10.0           # proximity required to consume food

# Colors (R, G, B)
BACKGROUND_COLOR = (15, 15, 25)
AGENT_COLOR = (100, 200, 255)
FOOD_COLOR = (100, 220, 80)
