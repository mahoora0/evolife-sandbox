# renderer.py
"""
Rendering helpers for EvoLife Sandbox.
Draws regions, particles, creatures, HUD, selection inspector, and graph.
"""

import math
import random

import pygame

import config


class Particle:
    def __init__(self, particle_type):
        self.reset(particle_type)
        self.y = random.uniform(0, config.WORLD_HEIGHT)

    def reset(self, particle_type):
        self.x = random.uniform(0, config.WORLD_WIDTH)
        self.y = random.uniform(-60, 0)
        self.size = random.uniform(2.0, 6.0)
        self.speed_y = random.uniform(0.4, 1.8)
        self.speed_x = random.uniform(-0.8, 0.8)
        self.angle = random.uniform(0, 360)
        self.rot_speed = random.uniform(-2.0, 2.0)

        if particle_type == "petal":
            self.color = (255, random.randint(185, 215), random.randint(205, 230))
            self.size = random.uniform(3.0, 7.0)
        elif particle_type == "pollen":
            self.color = (random.randint(230, 255), random.randint(205, 235), random.randint(60, 130))
            self.size = random.uniform(1.5, 3.5)
            self.speed_y = random.uniform(0.15, 0.7)
        elif particle_type == "leaf":
            self.color = (random.randint(190, 240), random.randint(90, 160), random.randint(30, 70))
            self.size = random.uniform(4.0, 9.0)
            self.rot_speed = random.uniform(-4.0, 4.0)
        else:
            self.color = (random.randint(235, 255), random.randint(245, 255), 255)
            self.size = random.uniform(2.0, 5.0)
            self.speed_y = random.uniform(0.8, 2.3)

    def update(self, particle_type):
        self.x += self.speed_x
        self.y += self.speed_y
        self.angle += self.rot_speed

        if self.y > config.WORLD_HEIGHT + 10 or self.x < -20 or self.x > config.WORLD_WIDTH + 20:
            self.reset(particle_type)


class Renderer:
    def __init__(self):
        pygame.font.init()
        self.font_title = pygame.font.SysFont("arial", 20, bold=True)
        self.font_body = pygame.font.SysFont("arial", 14)
        self.font_body_bold = pygame.font.SysFont("arial", 14, bold=True)
        self.font_small = pygame.font.SysFont("arial", 11)

        self.selected_creature = None
        self.current_particle_type = "petal"
        self.particles = [Particle(self.current_particle_type) for _ in range(70)]

    def draw_circle_alpha(self, surface, color, center, radius):
        if radius <= 0:
            return

        radius = int(radius)
        temp = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(temp, color, (radius, radius), radius)
        surface.blit(temp, (int(center[0]) - radius, int(center[1]) - radius))

    def draw_rect_alpha(self, surface, color, rect, border_radius=0):
        temp = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(temp, color, temp.get_rect(), border_radius=border_radius)
        surface.blit(temp, rect.topleft)

    def draw_regions(self, surface):
        forest_rect = pygame.Rect(0, 0, 450, 350)
        desert_rect = pygame.Rect(750, 450, 450, 350)

        self.draw_rect_alpha(surface, (45, 130, 45, 28), forest_rect, border_radius=16)
        self.draw_rect_alpha(surface, (180, 120, 35, 28), desert_rect, border_radius=16)

        surface.blit(self.font_body_bold.render("Forest: fertile", True, (45, 85, 45)), (25, 20))
        surface.blit(self.font_body_bold.render("Plains: balanced", True, (80, 80, 80)), (515, 380))
        surface.blit(self.font_body_bold.render("Desert: sparse", True, (120, 75, 25)), (780, 470))

    def draw_particles(self, surface, current_season):
        particle_type = config.SEASON_MODIFIERS[current_season]["particle_type"]

        if particle_type != self.current_particle_type:
            self.current_particle_type = particle_type
            for particle in self.particles:
                particle.reset(particle_type)

        for particle in self.particles:
            particle.update(particle_type)

            if particle_type in ("snow", "pollen"):
                alpha = 190 if particle_type == "snow" else 150
                self.draw_circle_alpha(surface, particle.color + (alpha,), (particle.x, particle.y), particle.size)
            elif particle_type == "petal":
                petal = pygame.Surface((max(1, int(particle.size * 2)), max(1, int(particle.size))), pygame.SRCALPHA)
                pygame.draw.ellipse(petal, particle.color + (145,), petal.get_rect())
                surface.blit(pygame.transform.rotate(petal, particle.angle), (int(particle.x), int(particle.y)))
            else:
                leaf = pygame.Surface((max(1, int(particle.size)), max(1, int(particle.size * 1.5))), pygame.SRCALPHA)
                points = [
                    (particle.size / 2, 0),
                    (particle.size, particle.size * 0.75),
                    (particle.size / 2, particle.size * 1.5),
                    (0, particle.size * 0.75),
                ]
                pygame.draw.polygon(leaf, particle.color + (150,), points)
                surface.blit(pygame.transform.rotate(leaf, particle.angle), (int(particle.x), int(particle.y)))

    def draw_world(self, surface, world, show_vision):
        for grass in world.grasses:
            self.draw_circle_alpha(surface, (80, 220, 80, 55), (grass.x, grass.y), grass.radius * 2)
            pygame.draw.circle(surface, (30, 145, 30), (int(grass.x), int(grass.y)), int(grass.radius))

        for creature in world.herbivores + world.carnivores:
            if not creature.alive:
                continue

            if show_vision or creature is self.selected_creature:
                vision_color = (95, 220, 115, 28) if creature.type == "herbivore" else (230, 90, 90, 24)
                self.draw_circle_alpha(surface, vision_color, (creature.x, creature.y), creature.vision)
                pygame.draw.circle(surface, vision_color[:3], (int(creature.x), int(creature.y)), int(creature.vision), 1)

            body_color = creature.color
            age_ratio = min(1.0, creature.age / max(1, creature.max_age))
            if age_ratio > 0.82:
                fade = (age_ratio - 0.82) / 0.18
                body_color = tuple(int(body_color[i] * (1.0 - fade * 0.45) + 120 * fade * 0.45) for i in range(3))

            if creature.type == "herbivore":
                outline = (0, 185, 220)
                outline_width = 2 if creature.fear >= 1.0 else 1
            else:
                outline = (125, 0, 0)
                outline_width = 2 if creature.aggression >= 1.0 else 1

            self.draw_circle_alpha(surface, outline + (35,), (creature.x, creature.y), creature.size + 4)
            pygame.draw.circle(surface, body_color, (int(creature.x), int(creature.y)), int(creature.size))
            pygame.draw.circle(surface, outline, (int(creature.x), int(creature.y)), int(creature.size), outline_width)

            energy_ratio = max(0.0, min(1.0, creature.energy / max(1.0, creature.reproduction_threshold)))
            pygame.draw.circle(surface, (255, 255, 255), (int(creature.x), int(creature.y)), max(2, int(creature.size * energy_ratio)), 1)

            nose_x = creature.x + math.cos(creature.angle) * (creature.size + 4)
            nose_y = creature.y + math.sin(creature.angle) * (creature.size + 4)
            pygame.draw.line(surface, (20, 20, 20), (int(creature.x), int(creature.y)), (int(nose_x), int(nose_y)), 2)

            if creature is self.selected_creature and creature.target_x is not None:
                color = (0, 210, 0) if creature.type == "herbivore" else (220, 0, 0)
                pygame.draw.line(surface, color, (int(creature.x), int(creature.y)), (int(creature.target_x), int(creature.target_y)), 1)

        if self.selected_creature and not self.selected_creature.alive:
            self.selected_creature = None

    def draw_hud(self, surface, world, sim_speed, is_paused, show_graph):
        margin = 15
        season = world.get_current_season()
        season_pct = world.season_timer / config.SEASON_DURATION

        panel = pygame.Rect(margin, margin, 260, 104)
        self.draw_rect_alpha(surface, (10, 10, 10, 135), panel, border_radius=10)
        surface.blit(self.font_title.render(f"Season: {season}", True, (255, 255, 255)), (margin + 14, margin + 12))

        bar_rect = pygame.Rect(margin + 14, margin + 42, 225, 9)
        pygame.draw.rect(surface, (60, 60, 60), bar_rect, border_radius=4)
        filled = pygame.Rect(bar_rect.left, bar_rect.top, int(bar_rect.width * season_pct), bar_rect.height)
        pygame.draw.rect(surface, (230, 230, 230), filled, border_radius=4)

        step_text = self.font_body.render(f"Steps: {world.time_steps} | Births: {world.birth_count}", True, (225, 225, 225))
        speed_text = "PAUSED" if is_paused else f"Speed: x{sim_speed}"
        speed_surf = self.font_body_bold.render(speed_text, True, (255, 120, 120) if is_paused else (130, 255, 130))
        surface.blit(step_text, (margin + 14, margin + 61))
        surface.blit(speed_surf, (margin + 14, margin + 80))

        pop_panel = pygame.Rect(config.WORLD_WIDTH - 210, margin, 195, 94)
        self.draw_rect_alpha(surface, (10, 10, 10, 135), pop_panel, border_radius=10)
        counts = [
            (f"Herbivores: {len(world.herbivores)}", (130, 245, 130)),
            (f"Carnivores: {len(world.carnivores)}", (245, 130, 130)),
            (f"Grass: {len(world.grasses)}", (150, 230, 150)),
        ]
        for index, (text, color) in enumerate(counts):
            label = self.font_body_bold.render(text, True, color)
            surface.blit(label, (config.WORLD_WIDTH - 195, margin + 13 + index * 24))

        self.draw_gene_panel(surface, world)

        if self.selected_creature:
            self.draw_inspector_panel(surface, self.selected_creature)

        if show_graph and len(world.history) > 1:
            self.draw_population_graph(surface, world)

    def draw_gene_panel(self, surface, world):
        margin = 15
        panel = pygame.Rect(margin, config.WORLD_HEIGHT - 168, 330, 153)
        self.draw_rect_alpha(surface, (10, 10, 10, 145), panel, border_radius=10)
        surface.blit(self.font_title.render("Gene Averages", True, (255, 255, 255)), (margin + 14, config.WORLD_HEIGHT - 160))

        if not world.history:
            surface.blit(self.font_body.render("Collecting data...", True, (225, 225, 225)), (margin + 14, config.WORLD_HEIGHT - 130))
            return

        last = world.history[-1]
        lines = [
            (f"H speed {last['avg_h_speed']:.2f}", (185, 255, 185), 0),
            (f"H vision {last['avg_h_vision']:.0f}", (185, 255, 185), 1),
            (f"H size {last['avg_h_size']:.1f}", (185, 255, 185), 2),
            (f"H fear {last['avg_h_fear']:.2f}", (185, 255, 185), 3),
            (f"C speed {last['avg_c_speed']:.2f}", (255, 185, 185), 0),
            (f"C vision {last['avg_c_vision']:.0f}", (255, 185, 185), 1),
            (f"C size {last['avg_c_size']:.1f}", (255, 185, 185), 2),
            (f"C aggression {last['avg_c_agg']:.2f}", (255, 185, 185), 3),
        ]

        for index, (text, color, row) in enumerate(lines):
            x = margin + 14 if index < 4 else margin + 170
            y = config.WORLD_HEIGHT - 130 + row * 22
            surface.blit(self.font_body.render(text, True, color), (x, y))

    def draw_inspector_panel(self, surface, creature):
        panel = pygame.Rect(config.WORLD_WIDTH - 305, 125, 290, 305)
        border = (120, 255, 120) if creature.type == "herbivore" else (255, 120, 120)
        self.draw_rect_alpha(surface, (15, 20, 15, 180), panel, border_radius=10)
        pygame.draw.rect(surface, border, panel, 1, border_radius=10)
        surface.blit(self.font_title.render(f"Inspect: {creature.type.title()}", True, border), (panel.left + 14, panel.top + 12))

        lines = [
            f"ID: {creature.id}",
            f"Gen: {creature.generation} | Parent: {creature.parent_id or 'None'}",
            f"Age: {creature.age}/{creature.max_age}",
            f"Energy: {creature.energy:.1f}",
            f"State: {creature.current_action}",
            "",
            "Genome",
        ]
        for index, line in enumerate(lines):
            font = self.font_body_bold if line == "Genome" else self.font_body
            surface.blit(font.render(line, True, (240, 240, 240)), (panel.left + 14, panel.top + 45 + index * 20))

        gene_names = [
            "speed",
            "vision",
            "size",
            "energy_efficiency",
            "fear" if creature.type == "herbivore" else "aggression",
            "reproduction_threshold",
            "turn_rate",
        ]
        for index, gene_name in enumerate(gene_names):
            value = creature.genes.get(gene_name)
            y = panel.top + 190 + index * 15
            surface.blit(self.font_small.render(gene_name.replace("_", " ").title(), True, (195, 200, 220)), (panel.left + 14, y))
            surface.blit(self.font_small.render(f"{value:.2f}", True, (255, 255, 255)), (panel.right - 70, y))

    def draw_population_graph(self, surface, world):
        width = 320
        height = 155
        x = config.WORLD_WIDTH - width - 15
        y = config.WORLD_HEIGHT - height - 15
        panel = pygame.Rect(x, y, width, height)
        self.draw_rect_alpha(surface, (10, 10, 10, 145), panel, border_radius=10)
        surface.blit(self.font_title.render("Population History", True, (255, 255, 255)), (x + 14, y + 10))

        plot = pygame.Rect(x + 35, y + 38, width - 50, height - 58)
        pygame.draw.rect(surface, (60, 60, 60), plot, 1)

        history = world.history
        max_pop = max(max(pt["herbivores"], pt["carnivores"], pt["grass"] / 2.0) for pt in history)
        max_pop = max(max_pop, 20.0)

        def build_points(key, scale=1.0):
            points = []
            step_x = plot.width / (len(history) - 1)
            for index, item in enumerate(history):
                px = plot.left + index * step_x
                value = item[key] / scale
                py = plot.bottom - (value / max_pop) * plot.height
                points.append((int(px), int(max(plot.top, min(plot.bottom, py)))))
            return points

        pygame.draw.lines(surface, (130, 240, 130), False, build_points("herbivores"), 2)
        pygame.draw.lines(surface, (240, 130, 130), False, build_points("carnivores"), 2)
        pygame.draw.lines(surface, (130, 160, 255), False, build_points("grass", scale=2.0), 1)

    def handle_click(self, mouse_pos, world):
        mx, my = mouse_pos
        self.selected_creature = None
        best_match = None
        min_dist = 26.0

        for creature in world.herbivores + world.carnivores:
            if not creature.alive:
                continue
            dist = math.hypot(creature.x - mx, creature.y - my)
            if dist < min_dist:
                min_dist = dist
                best_match = creature

        if best_match:
            self.selected_creature = best_match
            return True

        return False
