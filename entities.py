# entities.py
"""
Entity models and behaviors for the EvoLife Sandbox simulation.
Implements Grass, Creature base class, Herbivore, and Carnivore.
"""

import math
import random
import uuid
from genes import Genome
import config


def clamp(value, low, high):
    """Clamp a number between two bounds."""
    return max(low, min(high, value))


def wrap_angle(angle):
    """Normalize an angle into the [0, 2π) range."""
    return angle % (2 * math.pi)


def clamped_child_position(parent_x, parent_y, radius):
    """Return a nearby spawn point that stays inside the world."""
    offset_angle = random.uniform(0, 2 * math.pi)
    cx = parent_x + math.cos(offset_angle) * radius
    cy = parent_y + math.sin(offset_angle) * radius

    return (
        clamp(cx, 10.0, config.WORLD_WIDTH - 10.0),
        clamp(cy, 10.0, config.WORLD_HEIGHT - 10.0),
    )


class Grass:
    def __init__(self, x, y, energy=None):
        self.x = x
        self.y = y
        self.energy = energy if energy is not None else config.GRASS_ENERGY
        self.radius = 3.0
        self.alive = True


class Creature:
    def __init__(self, x, y, genes=None, parent_id=None, generation=1, type_name="creature"):
        self.id = str(uuid.uuid4())[:8]
        self.parent_id = parent_id
        self.generation = generation
        self.type = type_name

        self.x = x
        self.y = y
        self.angle = random.uniform(0, 2 * math.pi)
        self.wander_angle = 0.0
        self.alive = True

        # Genetics
        if genes is None:
            self.genes = Genome()
        else:
            self.genes = genes

        # Unpack genes
        self.speed = self.genes.get("speed")
        self.vision = self.genes.get("vision")
        self.size = self.genes.get("size")
        self.energy_efficiency = self.genes.get("energy_efficiency")
        self.reproduction_threshold = self.genes.get("reproduction_threshold")
        self.turn_rate = self.genes.get("turn_rate")

        # Energy & Age
        if self.type == "herbivore":
            self.energy = config.HERBIVORE_START_ENERGY
            self.color = self.genes.get_herbivore_color()
        else:
            self.energy = config.CARNIVORE_START_ENERGY
            self.color = self.genes.get_carnivore_color()

        self.age = 0
        self.max_age = 1200 + int(self.energy_efficiency * 800)  # 1500-2600 frames life span
        self.current_action = "wandering"
        self.target_x = None
        self.target_y = None

    def calculate_metabolism(self, metabolism_multiplier=1.0):
        """Calculate energy drain per frame based on genes and current environment factors."""
        base = config.BASE_METABOLISM * metabolism_multiplier
        speed_c = self.speed * config.SPEED_COST_MULTIPLIER
        vision_c = self.vision * config.VISION_COST_MULTIPLIER
        size_c = self.size * config.SIZE_COST_MULTIPLIER

        # Energy efficiency reduces the overall cost
        total_cost = (base + speed_c + vision_c + size_c) / self.energy_efficiency
        return max(0.01, total_cost)

    def steer_towards(self, tx, ty, turn_multiplier=1.0):
        """Calculates steering angle adjustment towards a target (tx, ty)."""
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        if dist < 0.1:
            return

        target_angle = math.atan2(dy, dx)

        # Find shortest angular path
        angle_diff = target_angle - self.angle
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi

        # Clamp to turn_rate
        max_turn = self.turn_rate * turn_multiplier
        steer = max(-max_turn, min(max_turn, angle_diff))
        self.angle = wrap_angle(self.angle + steer)

    def wander(self):
        """Random organic wandering behavior using a running wander angle."""
        self.current_action = "wandering"
        # Small changes to the wander target angle
        self.wander_angle += random.uniform(-0.3, 0.3)
        # Keep wander angle relative to current angle
        tx = self.x + math.cos(self.angle + self.wander_angle) * 100
        ty = self.y + math.sin(self.angle + self.wander_angle) * 100
        self.steer_towards(tx, ty, turn_multiplier=0.75)

    def avoid_boundaries(self):
        """Steers back to the center of the world if approaching borders."""
        margin = 60
        near_border = (
            self.x < margin
            or self.x > config.WORLD_WIDTH - margin
            or self.y < margin
            or self.y > config.WORLD_HEIGHT - margin
        )

        if near_border:
            # Force target to center of screen
            cx = config.WORLD_WIDTH / 2
            cy = config.WORLD_HEIGHT / 2
            self.steer_towards(cx, cy, turn_multiplier=1.6)
            return True

        return False

    def move(self, speed_multiplier=1.0):
        """Move the creature forward based on its angle and speed."""
        actual_speed = self.speed * speed_multiplier
        self.x += math.cos(self.angle) * actual_speed
        self.y += math.sin(self.angle) * actual_speed

        # Hard clamps to prevent going completely out of bounds
        self.x = clamp(self.x, 10.0, config.WORLD_WIDTH - 10.0)
        self.y = clamp(self.y, 10.0, config.WORLD_HEIGHT - 10.0)

    def update_base(self, metabolism_multiplier=1.0, speed_multiplier=1.0):
        """Updates age and base energy depletion. Returns True if alive."""
        self.age += 1
        self.energy -= self.calculate_metabolism(metabolism_multiplier)

        if self.energy <= 0 or self.age >= self.max_age:
            self.alive = False

        return self.alive


class Herbivore(Creature):
    def __init__(self, x, y, genes=None, parent_id=None, generation=1):
        super().__init__(x, y, genes, parent_id, generation, type_name="herbivore")
        self.fear = self.genes.get("fear")

    def update(self, world, metabolism_multiplier=1.0, speed_multiplier=1.0):
        if not self.update_base(metabolism_multiplier, speed_multiplier):
            return

        # 1. Flee from Carnivores (highest priority)
        nearest_predator, pred_dist = world.find_nearest_carnivore(self)
        if nearest_predator and pred_dist < self.vision:
            self.current_action = "fleeing"
            self.target_x = nearest_predator.x
            self.target_y = nearest_predator.y

            # Vector away from predator
            dx = self.x - nearest_predator.x
            dy = self.y - nearest_predator.y
            # Fear gene scales intensity. High fear makes it steer aggressively.
            away_x = self.x + dx * (45 * max(0.2, self.fear))
            away_y = self.y + dy * (45 * max(0.2, self.fear))
            self.steer_towards(away_x, away_y, turn_multiplier=1.0 + min(self.fear, 1.5) * 0.35)

        # 2. Search for food
        else:
            nearest_grass, grass_dist = world.find_nearest_grass(self)
            if nearest_grass and grass_dist < self.vision:
                self.current_action = "seeking food"
                self.target_x = nearest_grass.x
                self.target_y = nearest_grass.y
                self.steer_towards(nearest_grass.x, nearest_grass.y)

                # Check eating collision
                if grass_dist < (self.size + nearest_grass.radius + 1.0):
                    # Eat the grass
                    nearest_grass.alive = False
                    self.energy += nearest_grass.energy
                    self.current_action = "eating"
            else:
                # 3. Wander randomly (if border avoidance doesn't trigger)
                if not self.avoid_boundaries():
                    self.wander()
                    self.target_x = None
                    self.target_y = None

        self.move(speed_multiplier)

    def reproduce(self):
        """Spawns an offspring herbivore, splitting energy and mutating."""
        # Reproduce cost
        self.energy -= config.HERBIVORE_REPRODUCTION_COST

        # Create mutated child genome
        child_genes = Genome(parent_genes=self.genes.genes, mutation_rate=config.HERBIVORE_MUTATION_RATE)

        # Position slightly offset, safely inside the world
        cx, cy = clamped_child_position(self.x, self.y, self.size * 2)

        child = Herbivore(cx, cy, genes=child_genes, parent_id=self.id, generation=self.generation + 1)
        # Share initial energy
        child.energy = config.HERBIVORE_REPRODUCTION_COST * 0.8

        return child


class Carnivore(Creature):
    def __init__(self, x, y, genes=None, parent_id=None, generation=1):
        super().__init__(x, y, genes, parent_id, generation, type_name="carnivore")
        self.aggression = self.genes.get("aggression")

    def update(self, world, metabolism_multiplier=1.0, speed_multiplier=1.0):
        if not self.update_base(metabolism_multiplier, speed_multiplier):
            return

        # 1. Search for Herbivore prey
        nearest_prey, prey_dist = world.find_nearest_herbivore(self)
        if nearest_prey and prey_dist < self.vision:
            self.current_action = "chasing"
            self.target_x = nearest_prey.x
            self.target_y = nearest_prey.y

            # Aggression gene makes predators commit harder to turns while chasing.
            self.steer_towards(
                nearest_prey.x,
                nearest_prey.y,
                turn_multiplier=1.0 + min(self.aggression, 1.6) * 0.30,
            )

            # Check attack collision
            if prey_dist < (self.size + nearest_prey.size):
                # Kill and eat prey
                nearest_prey.alive = False
                # Carnivore gains energy proportional to the prey's size (large prey is meatier).
                earned_energy = 40.0 + nearest_prey.size * 6.0 + max(0.0, nearest_prey.energy * 0.25)
                self.energy += earned_energy
                self.current_action = "eating"
        else:
            # 2. Wander
            if not self.avoid_boundaries():
                self.wander()
                self.target_x = None
                self.target_y = None

        self.move(speed_multiplier)

    def reproduce(self):
        """Spawns an offspring carnivore, splitting energy and mutating."""
        self.energy -= config.CARNIVORE_REPRODUCTION_COST

        child_genes = Genome(parent_genes=self.genes.genes, mutation_rate=config.CARNIVORE_MUTATION_RATE)

        cx, cy = clamped_child_position(self.x, self.y, self.size * 2)

        child = Carnivore(cx, cy, genes=child_genes, parent_id=self.id, generation=self.generation + 1)
        child.energy = config.CARNIVORE_REPRODUCTION_COST * 0.8

        return child
