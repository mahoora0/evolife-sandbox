# genes.py
"""
Genetic system for the EvoLife Sandbox simulation.
Handles genome creation, mutation, clamping, and color/size visual mappings.
"""

import random
from config import GENE_LIMITS, MUTATION_STRENGTH

class Genome:
    def __init__(self, parent_genes=None, mutation_rate=0.0):
        self.genes = {}
        if parent_genes is None:
            # Generate random initial genes within limits
            for gene_name, (min_val, max_val) in GENE_LIMITS.items():
                self.genes[gene_name] = random.uniform(min_val, max_val)
        else:
            # Copy parent genes and apply mutation
            for gene_name, parent_val in parent_genes.items():
                val = parent_val
                if random.random() < mutation_rate:
                    strength = MUTATION_STRENGTH[gene_name]
                    val += random.gauss(0, strength)
                
                # Clamp within limits
                min_val, max_val = GENE_LIMITS[gene_name]
                self.genes[gene_name] = max(min_val, min(max_val, val))

    def get(self, name):
        return self.genes.get(name, 0.0)

    def get_herbivore_color(self):
        """
        Herbivore: Green base.
        - Higher speed adds red (makes it more yellow).
        - Higher fear adds blue (makes it more cyan/teal).
        - Higher efficiency makes it brighter overall.
        """
        speed = self.get("speed")
        fear = self.get("fear")
        efficiency = self.get("energy_efficiency")
        
        # Base green
        g = int(140 + (efficiency - 0.4) * 50)  # 140 - 210
        g = max(50, min(255, g))
        
        # Speed maps to Red (Yellowish)
        # speed range (0.5 to 6.0)
        speed_ratio = (speed - 0.5) / 5.5
        r = int(20 + speed_ratio * 180)  # 20 - 200
        
        # Fear maps to Blue
        # fear range (0.0 to 2.0)
        fear_ratio = fear / 2.0
        b = int(20 + fear_ratio * 200)  # 20 - 220
        
        # Safety clamp
        return (max(10, min(240, r)), max(100, min(255, g)), max(10, min(240, b)))

    def get_carnivore_color(self):
        """
        Carnivore: Red base.
        - Higher speed adds green (makes it orange/yellow).
        - Higher aggression adds purple/magenta (adds blue) and keeps red deep.
        - Higher size keeps it darker and bulkier.
        """
        speed = self.get("speed")
        aggression = self.get("aggression")
        
        # Base Red
        r = 210
        
        # Speed maps to Green (adds orange tint)
        # speed range (0.5 to 6.0)
        speed_ratio = (speed - 0.5) / 5.5
        g = int(10 + speed_ratio * 120)  # 10 - 130
        
        # Aggression maps to Blue (makes it crimson/purple)
        # aggression range (0.0 to 2.0)
        agg_ratio = aggression / 2.0
        b = int(10 + agg_ratio * 140)  # 10 - 150
        
        return (max(150, min(255, r)), max(10, min(220, g)), max(10, min(220, b)))

    def copy(self):
        copied = Genome()
        copied.genes = self.genes.copy()
        return copied
