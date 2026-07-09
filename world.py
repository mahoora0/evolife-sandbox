# world.py
"""
World simulation coordinator for EvoLife Sandbox.
Manages entities, grid-based spatial partitioning, seasons, and genetic telemetry.
"""

import math
import random
from config import (
    WORLD_WIDTH, WORLD_HEIGHT, INITIAL_GRASS, MAX_GRASS,
    INITIAL_HERBIVORES, INITIAL_CARNIVORES, MAX_HERBIVORES,
    MAX_CARNIVORES, SEASON_DURATION, SEASONS, SEASON_MODIFIERS,
    GRASS_SPAWN_RATE, GRASS_ENERGY, HISTORY_LIMIT
)
from entities import Grass, Herbivore, Carnivore


class World:
    def __init__(self):
        self.width = WORLD_WIDTH
        self.height = WORLD_HEIGHT

        self.grasses = []
        self.herbivores = []
        self.carnivores = []

        # Spatial Grid Settings
        self.cell_size = 80
        self.grid = {}

        # Season Tracking
        self.season_timer = 0.0
        self.current_season_idx = 0

        # Spawning controls
        self.grass_tick = 0

        # Statistics History
        self.time_steps = 0
        self.birth_count = INITIAL_HERBIVORES + INITIAL_CARNIVORES
        self.history = []

        # Initialize population
        self.reset()

    def reset(self):
        """Clears all entities and repopulates the simulation."""
        self.grasses.clear()
        self.herbivores.clear()
        self.carnivores.clear()
        self.history.clear()

        self.season_timer = 0.0
        self.current_season_idx = 0
        self.grass_tick = 0
        self.time_steps = 0
        self.birth_count = INITIAL_HERBIVORES + INITIAL_CARNIVORES

        # Spawn initial grass (uniformly spread initially)
        for _ in range(INITIAL_GRASS):
            x = random.uniform(20, self.width - 20)
            y = random.uniform(20, self.height - 20)
            self.grasses.append(Grass(x, y))

        # Spawn initial herbivores
        for _ in range(INITIAL_HERBIVORES):
            x = random.uniform(50, self.width - 50)
            y = random.uniform(50, self.height - 50)
            self.herbivores.append(Herbivore(x, y))

        # Spawn initial carnivores
        for _ in range(INITIAL_CARNIVORES):
            x = random.uniform(50, self.width - 50)
            y = random.uniform(50, self.height - 50)
            self.carnivores.append(Carnivore(x, y))

        self.update_spatial_grid()
        self.record_history()

    def get_current_season(self):
        return SEASONS[self.current_season_idx]

    def get_season_mods(self):
        return SEASON_MODIFIERS[self.get_current_season()]

    def get_region_at(self, x, y):
        """
        Determines the ecological region of a coordinate.
        - Forest (Top-Left): Fertile, high growth, high tree cover.
        - Desert (Bottom-Right): Dry, low growth.
        - Plains (Middle): Normal.
        """
        if x < 450 and y < 350:
            return "Forest"
        elif x > 750 and y > 450:
            return "Desert"
        else:
            return "Plains"

    def spawn_grass_regional(self, energy_val):
        """Spawns a single grass based on region fertility weights."""
        # Regional selection: Forest (60% weight), Plains (35% weight), Desert (5% weight)
        roll = random.random()
        if roll < 0.60:
            # Forest bounds: x: [20, 440], y: [20, 340]
            x = random.uniform(20, 440)
            y = random.uniform(20, 340)
        elif roll < 0.95:
            # Plains covers standard central area, or random anywhere outside the extremes
            x = random.uniform(20, self.width - 20)
            y = random.uniform(20, self.height - 20)
        else:
            # Desert bounds: x: [760, self.width-20], y: [460, self.height-20]
            x = random.uniform(760, self.width - 20)
            y = random.uniform(460, self.height - 20)

        self.grasses.append(Grass(x, y, energy=energy_val))

    def update_spatial_grid(self):
        """Re-registers all active entities into localized cell buckets."""
        self.grid.clear()

        # Grid registration helper
        def register(entity, etype):
            cx = int(entity.x // self.cell_size)
            cy = int(entity.y // self.cell_size)
            cell = self.grid.setdefault((cx, cy), {"grass": [], "herbivore": [], "carnivore": []})
            cell[etype].append(entity)

        for g in self.grasses:
            if g.alive:
                register(g, "grass")
        for h in self.herbivores:
            if h.alive:
                register(h, "herbivore")
        for c in self.carnivores:
            if c.alive:
                register(c, "carnivore")

    def find_nearest_in_grid(self, creature, target_type):
        """
        Uses spatial grid partition to query nearby entities,
        greatly reducing search operations from O(N) to a local neighborhood scan.
        """
        cx = int(creature.x // self.cell_size)
        cy = int(creature.y // self.cell_size)

        # Calculate search radius in terms of grid cells based on creature's vision
        cell_radius = int(creature.vision // self.cell_size) + 1
        vision_sq = creature.vision * creature.vision

        nearest = None
        min_dist_sq = vision_sq

        # Check all cells within the vision cell radius
        for dx in range(-cell_radius, cell_radius + 1):
            for dy in range(-cell_radius, cell_radius + 1):
                cell_key = (cx + dx, cy + dy)
                if cell_key in self.grid:
                    entities = self.grid[cell_key][target_type]
                    for entity in entities:
                        if entity is creature or not entity.alive:
                            continue

                        ddx = entity.x - creature.x
                        ddy = entity.y - creature.y
                        dist_sq = ddx * ddx + ddy * ddy
                        if dist_sq < min_dist_sq:
                            min_dist_sq = dist_sq
                            nearest = entity

        if nearest is None:
            return None, float("inf")

        return nearest, math.sqrt(min_dist_sq)

    # Interfaces for entities querying neighbor entities
    def find_nearest_grass(self, creature):
        return self.find_nearest_in_grid(creature, "grass")

    def find_nearest_herbivore(self, creature):
        return self.find_nearest_in_grid(creature, "herbivore")

    def find_nearest_carnivore(self, creature):
        return self.find_nearest_in_grid(creature, "carnivore")

    def update(self, dt=1.0 / 60.0, sim_speed=1):
        """Runs the simulation logic for one or more logic frames."""
        for _ in range(sim_speed):
            self.time_steps += 1

            # 1. Update Season timer
            self.season_timer += dt
            if self.season_timer >= SEASON_DURATION:
                self.season_timer = 0.0
                self.current_season_idx = (self.current_season_idx + 1) % len(SEASONS)

            # Get current seasonal adjustments
            mods = self.get_season_mods()
            spawn_multiplier = mods["grass_spawn_multiplier"]
            base_grass_energy = mods["grass_energy_multiplier"] * GRASS_ENERGY
            metabolism_multiplier = mods["metabolism_multiplier"]

            # 2. Spawning Grass
            self.grass_tick += 1
            adjusted_spawn_rate = max(1, int(GRASS_SPAWN_RATE / spawn_multiplier))
            if self.grass_tick >= adjusted_spawn_rate:
                self.grass_tick = 0
                if len(self.grasses) < MAX_GRASS:
                    self.spawn_grass_regional(base_grass_energy)

            # 3. Update spatial grid before herbivore decisions.
            self.update_spatial_grid()

            # 4. Update Herbivores
            new_herbivores = []
            projected_herbivore_count = len(self.herbivores)
            for h in self.herbivores:
                h.update(self, metabolism_multiplier, speed_multiplier=1.0)

                # Check for reproduction, capped to avoid runaway population spikes.
                if (
                    h.alive
                    and h.energy > h.reproduction_threshold
                    and projected_herbivore_count + len(new_herbivores) < MAX_HERBIVORES
                ):
                    child = h.reproduce()
                    new_herbivores.append(child)
                    self.birth_count += 1

            self.herbivores.extend(new_herbivores)

            # Herbivore movement and grass eating changed positions/alive flags.
            # Refresh before carnivores query nearby prey.
            self.grasses = [g for g in self.grasses if g.alive]
            self.update_spatial_grid()

            # 5. Update Carnivores
            new_carnivores = []
            projected_carnivore_count = len(self.carnivores)
            for c in self.carnivores:
                c.update(self, metabolism_multiplier, speed_multiplier=1.0)

                # Check for reproduction, capped to keep frame time stable.
                if (
                    c.alive
                    and c.energy > c.reproduction_threshold
                    and projected_carnivore_count + len(new_carnivores) < MAX_CARNIVORES
                ):
                    child = c.reproduce()
                    new_carnivores.append(child)
                    self.birth_count += 1

            self.carnivores.extend(new_carnivores)

            # 6. Filter dead entities
            self.grasses = [g for g in self.grasses if g.alive]
            self.herbivores = [h for h in self.herbivores if h.alive]
            self.carnivores = [c for c in self.carnivores if c.alive]

            # 7. Record History telemetry every 60 steps (approx 1s of simulated time)
            if self.time_steps % 60 == 0:
                self.record_history()

    def record_history(self):
        """Records average genetics and counts for history analytics."""
        h_count = len(self.herbivores)
        c_count = len(self.carnivores)

        # Calculate herbivore averages
        avg_h_speed = sum(h.speed for h in self.herbivores) / h_count if h_count > 0 else 0.0
        avg_h_vision = sum(h.vision for h in self.herbivores) / h_count if h_count > 0 else 0.0
        avg_h_size = sum(h.size for h in self.herbivores) / h_count if h_count > 0 else 0.0
        avg_h_fear = sum(h.fear for h in self.herbivores) / h_count if h_count > 0 else 0.0

        # Calculate carnivore averages
        avg_c_speed = sum(c.speed for c in self.carnivores) / c_count if c_count > 0 else 0.0
        avg_c_vision = sum(c.vision for c in self.carnivores) / c_count if c_count > 0 else 0.0
        avg_c_size = sum(c.size for c in self.carnivores) / c_count if c_count > 0 else 0.0
        avg_c_agg = sum(c.aggression for c in self.carnivores) / c_count if c_count > 0 else 0.0

        self.history.append({
            "step": self.time_steps,
            "herbivores": h_count,
            "carnivores": c_count,
            "grass": len(self.grasses),
            "avg_h_speed": avg_h_speed,
            "avg_h_vision": avg_h_vision,
            "avg_h_size": avg_h_size,
            "avg_h_fear": avg_h_fear,
            "avg_c_speed": avg_c_speed,
            "avg_c_vision": avg_c_vision,
            "avg_c_size": avg_c_size,
            "avg_c_agg": avg_c_agg,
        })

        # Limit history length to prevent memory inflation
        if len(self.history) > HISTORY_LIMIT:
            self.history.pop(0)

    # Manual spawn overrides for interactive UI sandbox functionality
    def add_grass_at(self, x, y):
        if len(self.grasses) < MAX_GRASS:
            # Base energy from season mods
            base_grass_energy = self.get_season_mods()["grass_energy_multiplier"] * GRASS_ENERGY
            self.grasses.append(Grass(x, y, energy=base_grass_energy))
            self.update_spatial_grid()

    def add_herbivore_at(self, x, y):
        if len(self.herbivores) >= MAX_HERBIVORES:
            return

        h = Herbivore(x, y)
        self.herbivores.append(h)
        self.birth_count += 1
        self.update_spatial_grid()

    def add_carnivore_at(self, x, y):
        if len(self.carnivores) >= MAX_CARNIVORES:
            return

        c = Carnivore(x, y)
        self.carnivores.append(c)
        self.birth_count += 1
        self.update_spatial_grid()
