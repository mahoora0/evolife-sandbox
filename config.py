# config.py
"""
Configuration settings and balance constants for the EvoLife Sandbox simulation.
"""

# World Dimensions
WORLD_WIDTH = 1200
WORLD_HEIGHT = 800
TARGET_FPS = 60

# Initial Population Sizes
INITIAL_GRASS = 250
MAX_GRASS = 600
GRASS_SPAWN_RATE = 4  # Frames between automatic grass spawns

INITIAL_HERBIVORES = 45
INITIAL_CARNIVORES = 10

# Safety caps keep long simulations from collapsing into runaway population spikes.
MAX_HERBIVORES = 220
MAX_CARNIVORES = 90

# Base Energy Values
GRASS_ENERGY = 35.0
HERBIVORE_START_ENERGY = 120.0
CARNIVORE_START_ENERGY = 160.0

HERBIVORE_REPRODUCTION_COST = 80.0
CARNIVORE_REPRODUCTION_COST = 140.0

# Mutation Settings
HERBIVORE_MUTATION_RATE = 0.15
CARNIVORE_MUTATION_RATE = 0.12

# Gene Limits (min_value, max_value)
GENE_LIMITS = {
    "speed": (0.5, 6.0),
    "vision": (30.0, 250.0),
    "size": (4.0, 20.0),
    "energy_efficiency": (0.4, 1.8),
    "fear": (0.0, 2.0),
    "aggression": (0.0, 2.0),
    "reproduction_threshold": (80.0, 300.0),
    "turn_rate": (0.02, 0.25),
}

# Mutation Strengths (standard deviation for gaussian mutation)
MUTATION_STRENGTH = {
    "speed": 0.25,
    "vision": 12.0,
    "size": 1.0,
    "energy_efficiency": 0.08,
    "fear": 0.15,
    "aggression": 0.15,
    "reproduction_threshold": 12.0,
    "turn_rate": 0.02,
}

# Energy Consumption Mappings (Metabolism)
# Base formula: metabolism_cost = base_metabolism + speed_cost + vision_cost + size_cost
# Adjusted to scale with size/efficiency: energy_cost = metabolism_cost / energy_efficiency
BASE_METABOLISM = 0.03
SPEED_COST_MULTIPLIER = 0.015
VISION_COST_MULTIPLIER = 0.00008
SIZE_COST_MULTIPLIER = 0.004

# Seasons configuration (cycle duration in seconds)
SEASON_DURATION = 35.0  # seconds per season
SEASONS = ["Spring", "Summer", "Autumn", "Winter"]

# Seasonal modifiers (Grass Growth, Grass Energy, Base Metabolism)
SEASON_MODIFIERS = {
    "Spring": {
        "grass_spawn_multiplier": 1.8,
        "grass_energy_multiplier": 1.0,
        "metabolism_multiplier": 1.0,
        "bg_color": (210, 240, 210),  # Light vibrant green
        "particle_type": "petal",
    },
    "Summer": {
        "grass_spawn_multiplier": 1.0,
        "grass_energy_multiplier": 1.2,
        "metabolism_multiplier": 1.0,
        "bg_color": (245, 245, 200),  # Warm yellow-green
        "particle_type": "pollen",
    },
    "Autumn": {
        "grass_spawn_multiplier": 0.6,
        "grass_energy_multiplier": 1.5,
        "metabolism_multiplier": 1.1,
        "bg_color": (240, 220, 190),  # Warm amber/orange tint
        "particle_type": "leaf",
    },
    "Winter": {
        "grass_spawn_multiplier": 0.2,
        "grass_energy_multiplier": 0.8,
        "metabolism_multiplier": 1.4,  # Cold weather burns more energy
        "bg_color": (220, 230, 245),  # Ice blue
        "particle_type": "snow",
    },
}

# Telemetry
HISTORY_LIMIT = 360

# Interactive Config Toggles
DEFAULT_SHOW_VISION = False
DEFAULT_SHOW_HUD = True
DEFAULT_SIMULATION_SPEED = 1  # 1x, 2x, 4x, etc.
