# genes.py
"""
Genetic system for the EvoLife Sandbox simulation.
Handles genome creation, mutation, clamping, and color mappings.
"""

import random

from config import GENE_LIMITS, MUTATION_STRENGTH


def clamp(value, low, high):
    """Clamp a number between two bounds."""
    return max(low, min(high, value))


def ratio(value, low, high):
    """Map a value inside a range to 0..1."""
    if high == low:
        return 0.0
    return clamp((value - low) / (high - low), 0.0, 1.0)


class Genome:
    def __init__(self, parent_genes=None, mutation_rate=0.0):
        self.genes = {}

        if parent_genes is None:
            for gene_name, (min_val, max_val) in GENE_LIMITS.items():
                self.genes[gene_name] = random.uniform(min_val, max_val)
        else:
            for gene_name, (min_val, max_val) in GENE_LIMITS.items():
                parent_val = parent_genes.get(gene_name, random.uniform(min_val, max_val))
                value = parent_val

                if random.random() < mutation_rate:
                    value += random.gauss(0, MUTATION_STRENGTH[gene_name])

                self.genes[gene_name] = clamp(value, min_val, max_val)

    def get(self, name):
        return self.genes.get(name, 0.0)

    def get_herbivore_color(self):
        """
        Herbivore: green base.
        Higher speed adds yellow, higher fear adds cyan/blue.
        """
        speed_min, speed_max = GENE_LIMITS["speed"]
        fear_min, fear_max = GENE_LIMITS["fear"]
        eff_min, eff_max = GENE_LIMITS["energy_efficiency"]

        speed_ratio = ratio(self.get("speed"), speed_min, speed_max)
        fear_ratio = ratio(self.get("fear"), fear_min, fear_max)
        efficiency_ratio = ratio(self.get("energy_efficiency"), eff_min, eff_max)

        red = int(30 + speed_ratio * 170)
        green = int(145 + efficiency_ratio * 90)
        blue = int(35 + fear_ratio * 190)

        return (
            clamp(red, 10, 240),
            clamp(green, 100, 255),
            clamp(blue, 10, 240),
        )

    def get_carnivore_color(self):
        """
        Carnivore: red base.
        Higher speed adds orange, higher aggression adds purple.
        """
        speed_min, speed_max = GENE_LIMITS["speed"]
        agg_min, agg_max = GENE_LIMITS["aggression"]

        speed_ratio = ratio(self.get("speed"), speed_min, speed_max)
        aggression_ratio = ratio(self.get("aggression"), agg_min, agg_max)

        red = 215
        green = int(20 + speed_ratio * 120)
        blue = int(20 + aggression_ratio * 140)

        return (
            clamp(red, 150, 255),
            clamp(green, 10, 220),
            clamp(blue, 10, 220),
        )

    def copy(self):
        copied = Genome()
        copied.genes = self.genes.copy()
        return copied
