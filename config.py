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

# Stress
MAX_STRESS = 100.0
STRESS_DECAY_RATE = 3.0        # natural stress reduction per second
DENSITY_RADIUS = 50.0          # neighbor detection radius (pixels)
STRESS_PER_NEIGHBOR = 4.0      # stress gain per nearby agent per second

# Stress thresholds
STRESS_THRESHOLD_MEDIUM = 35.0
STRESS_THRESHOLD_HIGH = 70.0

# Behavioral degradation
STRESS_JITTER_MEDIUM = 0.3     # extra wander noise multiplier at medium stress
STRESS_JITTER_HIGH = 0.8       # extra wander noise multiplier at high stress
STRESS_SEEK_PENALTY_MEDIUM = 0.7   # steer strength multiplier at medium stress
STRESS_SEEK_PENALTY_HIGH = 0.3     # steer strength multiplier at high stress
STRESS_WANDER_CHANCE_HIGH = 0.4    # chance of wandering instead of seeking at high stress

# Reproduction
MATING_RADIUS = 15.0               # max distance for mating (pixels)
REPRODUCTION_COOLDOWN = 15.0       # seconds before agent can reproduce again
REPRODUCTION_STRESS_MAX = 60.0     # stress must be below this to reproduce
REPRODUCTION_HUNGER_MAX = 40.0     # hunger must be below this to reproduce
MAX_POPULATION = 400               # hard cap on total agents
REPRODUCTION_DENSITY_PENALTY = 0.1 # per-neighbor reduction in reproduction chance
BASE_REPRODUCTION_CHANCE = 0.3     # base probability per eligible pair per second
CHILD_SPEED_VARIATION = 0.1        # ±10% speed variation for inheritance
BIRTH_FLASH_DURATION = 0.3         # seconds the birth flash is visible
BIRTH_FLASH_RADIUS = 8             # pixel radius of the flash circle

# Colors (R, G, B)
BACKGROUND_COLOR = (15, 15, 25)
AGENT_COLOR = (100, 200, 255)
FOOD_COLOR = (100, 220, 80)

# Sprites
MOUSE_SPRITE_PATH = "assets/mouse.png"
FOOD_SPRITE_PATH = "assets/food.png"
MOUSE_SPRITE_SIZE = (16, 16)
FOOD_SPRITE_SIZE = (10, 10)

# Zones  (type, x, y, width, height)
ZONES = [
    {"type": "feeding", "x": 250, "y": 220, "width": 200, "height": 200},
    {"type": "feeding", "x": 830, "y": 220, "width": 200, "height": 200},
    {"type": "nesting", "x": 490, "y": 530, "width": 300, "height": 150},
]
FEEDING_ZONE_COLOR = (30, 60, 30)    # dark green overlay
NESTING_ZONE_COLOR = (40, 30, 50)    # dark purple overlay
