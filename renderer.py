# renderer.py
"""
Rendering module for EvoLife Sandbox.
Handles drawing the simulation, glassmorphism UI, seasons blending, particles, and charts.
"""

import math
import random
import pygame
import pygame.gfxdraw
import config

class Particle:
    def __init__(self, ptype):
        self.reset(ptype)
        # Random initial position to avoid clustering at top on start
        self.y = random.uniform(0, config.WORLD_HEIGHT)

    def reset(self, ptype):
        self.x = random.uniform(0, config.WORLD_WIDTH)
        self.y = 0
        self.size = random.uniform(2, 6)
        self.speed_y = random.uniform(0.5, 2.0)
        self.speed_x = random.uniform(-1.0, 1.0)
        self.angle = random.uniform(0, 360)
        self.rot_speed = random.uniform(-2.0, 2.0)
        
        # Color palettes based on particle types
        if ptype == "petal":  # Spring Pink/White Petals
            self.color = (random.randint(240, 255), random.randint(180, 210), random.randint(200, 225))
            self.size = random.uniform(3, 7)
        elif ptype == "pollen":  # Summer Gold Glowing sparks
            self.color = (random.randint(230, 255), random.randint(200, 230), random.randint(50, 120))
            self.speed_y = random.uniform(0.2, 0.8)
            self.speed_x = random.uniform(-0.5, 0.5)
            self.size = random.uniform(1.5, 3.5)
        elif ptype == "leaf":  # Autumn Amber Leaves
            self.color = (random.randint(190, 240), random.randint(90, 160), random.randint(30, 60))
            self.size = random.uniform(4, 9)
            self.rot_speed = random.uniform(-4.0, 4.0)
        else:  # Winter Snowflakes
            self.color = (random.randint(240, 255), random.randint(245, 255), 255)
            self.speed_y = random.uniform(0.8, 2.5)
            self.speed_x = random.uniform(-0.8, 0.8)

    def update(self, ptype):
        self.y += self.speed_y
        self.x += self.speed_x
        self.angle += self.rot_speed
        
        # Reset if out of screen bounds
        if self.y > config.WORLD_HEIGHT or self.x < 0 or self.x > config.WORLD_WIDTH:
            self.reset(ptype)


class Renderer:
    def __init__(self):
        pygame.font.init()
        # Load fonts
        try:
            self.font_title = pygame.font.SysFont("Outfit", 20, bold=True)
            self.font_body = pygame.font.SysFont("Inter", 13)
            self.font_body_bold = pygame.font.SysFont("Inter", 13, bold=True)
            self.font_small = pygame.font.SysFont("Inter", 10)
        except:
            # Fallback to standard fonts
            self.font_title = pygame.font.SysFont("arial", 20, bold=True)
            self.font_body = pygame.font.SysFont("arial", 13)
            self.font_body_bold = pygame.font.SysFont("arial", 13, bold=True)
            self.font_small = pygame.font.SysFont("arial", 10)

        # Selected creature tracking
        self.selected_creature = None
        
        # Initialize seasonal particles
        self.particles = [Particle("petal") for _ in range(80)]
        self.current_particle_type = "petal"

    def draw_circle_alpha(self, surface, color, center, radius):
        """Draws an anti-aliased circle with transparency support."""
        if radius <= 0:
            return
        cx, cy = int(center[0]), int(center[1])
        r = int(radius)
        
        # Create temp alpha surface
        temp_surface = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(temp_surface, color, (r, r), r)
        surface.blit(temp_surface, (cx - r, cy - r))

    def draw_rect_alpha(self, surface, color, rect, border_radius=0):
        """Draws a rectangle with transparency support."""
        temp_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(temp_surface, color, temp_surface.get_rect(), border_radius=border_radius)
        surface.blit(temp_surface, rect.topleft)

    def draw_regions(self, surface):
        """Draws soft, transparent highlights for ecological regions."""
        # Forest (Top-Left): x in [0, 450], y in [0, 350]
        forest_rect = pygame.Rect(0, 0, 450, 350)
        self.draw_rect_alpha(surface, (40, 120, 40, 20), forest_rect, border_radius=15)
        
        # Desert (Bottom-Right): x in [750, 1200], y in [450, 800]
        desert_rect = pygame.Rect(750, 450, 450, 350)
        self.draw_rect_alpha(surface, (180, 110, 30, 22), desert_rect, border_radius=15)
        
        # Region Labels
        txt_forest = self.font_title.render("Whispering Forest (Fertile)", True, (45, 90, 45, 120))
        surface.blit(txt_forest, (25, 20))
        
        txt_desert = self.font_title.render("Scorched Desert (Arid)", True, (120, 70, 20, 120))
        surface.blit(txt_desert, (775, 470))
        
        txt_plains = self.font_title.render("Sunlit Plains (Normal)", True, (80, 80, 80, 100))
        surface.blit(txt_plains, (500, 380))

    def draw_particles(self, surface, current_season):
        """Updates and renders seasonal particles for beautiful atmospheric effects."""
        ptype = config.SEASON_MODIFIERS[current_season]["particle_type"]
        
        # Reset particles list if season changes
        if ptype != self.current_particle_type:
            self.current_particle_type = ptype
            for p in self.particles:
                p.reset(ptype)
                
        for p in self.particles:
            p.update(ptype)
            
            # Render based on particle shape type
            if ptype == "snow":
                self.draw_circle_alpha(surface, p.color + (180,), (p.x, p.y), p.size)
            elif ptype == "pollen":
                self.draw_circle_alpha(surface, p.color + (200,), (p.x, p.y), p.size)
            elif ptype == "petal":
                # Render drifting oval petals
                petal_surf = pygame.Surface((int(p.size * 2), int(p.size)), pygame.SRCALPHA)
                pygame.draw.ellipse(petal_surf, p.color + (160,), petal_surf.get_rect())
                rotated_surf = pygame.transform.rotate(petal_surf, p.angle)
                surface.blit(rotated_surf, (int(p.x), int(p.y)))
            elif ptype == "leaf":
                # Render spinning diamond-like autumn leaves
                leaf_surf = pygame.Surface((int(p.size), int(p.size * 1.5)), pygame.SRCALPHA)
                pygame.draw.polygon(leaf_surf, p.color + (170,), [
                    (p.size / 2, 0), (p.size, p.size * 0.75), (p.size / 2, p.size * 1.5), (0, p.size * 0.75)
                ])
                rotated_surf = pygame.transform.rotate(leaf_surf, p.angle)
                surface.blit(rotated_surf, (int(p.x), int(p.y)))

    def draw_world(self, surface, world, show_vision):
        """Draws the ecosystem entities (grass, creatures)."""
        # Draw Grass
        for g in world.grasses:
            # Grass has a subtle green glow
            self.draw_circle_alpha(surface, (100, 235, 100, 60), (g.x, g.y), g.radius * 2)
            pygame.draw.circle(surface, (30, 150, 30), (int(g.x), int(g.y)), int(g.radius))
            
        # Draw Creatures
        all_creatures = world.herbivores + world.carnivores
        for c in all_creatures:
            if not c.alive:
                continue
                
            # If Selected, highlight vision boundary
            if c == self.selected_creature or show_vision:
                # Draw vision boundary
                vision_color = (130, 220, 130, 25) if c.type == "herbivore" else (220, 130, 130, 20)
                self.draw_circle_alpha(surface, vision_color, (c.x, c.y), c.vision)
                pygame.draw.circle(surface, (vision_color[0], vision_color[1], vision_color[2], 120), 
                                   (int(c.x), int(c.y)), int(c.vision), 1)
                
            # Calculate color based on age (fade to grey near death)
            base_color = c.color
            age_percent = c.age / c.max_age
            if age_percent > 0.8:
                # Interpolate towards grey
                grey_factor = (age_percent - 0.8) / 0.2  # 0 to 1
                base_color = tuple(
                    int(base_color[i] * (1.0 - grey_factor * 0.5) + 120 * (grey_factor * 0.5)) for i in range(3)
                )
                
            # Outer Ring based on species behavior outlines
            if c.type == "herbivore":
                # Fear color (cyan/blue glow)
                outline_color = (0, 190, 240)
                border_width = 1 if c.fear < 1.0 else 2
            else:
                # Aggression color (dark crimson glow)
                outline_color = (130, 0, 0)
                border_width = 1 if c.aggression < 1.0 else 2
                
            # 1. Glow effect
            self.draw_circle_alpha(surface, outline_color + (40,), (c.x, c.y), c.size + 4)
            # 2. Main body circle
            pygame.draw.circle(surface, base_color, (int(c.x), int(c.y)), int(c.size))
            # 3. Outer border
            pygame.draw.circle(surface, outline_color, (int(c.x), int(c.y)), int(c.size), border_width)
            
            # 4. Energy concentric ring (drawn inside body)
            energy_ratio = min(1.0, max(0.0, c.energy / c.reproduction_threshold))
            inner_r = max(1.5, c.size - 2.5)
            self.draw_circle_alpha(surface, (255, 255, 255, 140), (c.x, c.y), inner_r)
            self.draw_circle_alpha(surface, (255, 255, 255, 240), (c.x, c.y), inner_r * energy_ratio)
            
            # 5. Heading indicator (eyes or pointer nose)
            nose_len = c.size + 3.0
            nx = c.x + math.cos(c.angle) * nose_len
            ny = c.y + math.sin(c.angle) * nose_len
            
            # Eyes representation (two tiny black dots offset)
            eye_angle_offset = 0.4
            eye_dist = c.size - 1.0
            el_x = c.x + math.cos(c.angle - eye_angle_offset) * eye_dist
            el_y = c.y + math.sin(c.angle - eye_angle_offset) * eye_dist
            er_x = c.x + math.cos(c.angle + eye_angle_offset) * eye_dist
            er_y = c.y + math.sin(c.angle + eye_angle_offset) * eye_dist
            pygame.draw.circle(surface, (0, 0, 0), (int(el_x), int(el_y)), 2)
            pygame.draw.circle(surface, (0, 0, 0), (int(er_x), int(er_y)), 2)
            
            # Draw line to current target (if selected)
            if c == self.selected_creature and c.target_x is not None:
                line_color = (0, 220, 0, 160) if c.type == "herbivore" else (220, 0, 0, 160)
                # Dotted target line
                self.draw_dotted_line(surface, line_color, (c.x, c.y), (c.target_x, c.target_y))
                
        # If selection died, clear selection
        if self.selected_creature and not self.selected_creature.alive:
            self.selected_creature = None

    def draw_dotted_line(self, surface, color, start, end, dot_spacing=6):
        """Draws a dotted line between start and end coordinates."""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = math.hypot(dx, dy)
        if distance == 0:
            return
        
        dots = int(distance // dot_spacing)
        for i in range(dots):
            t = i / dots
            px = int(start[0] + dx * t)
            py = int(start[1] + dy * t)
            pygame.draw.circle(surface, color, (px, py), 2)

    def draw_hud(self, surface, world, sim_speed, is_paused, show_graph):
        """Draws status overlays, genetic charts, averages, and pause panel."""
        margin = 15
        
        # 1. Season Indicator Panel (Glassmorphic)
        season_panel = pygame.Rect(margin, margin, 240, 95)
        self.draw_rect_alpha(surface, (10, 10, 10, 120), season_panel, border_radius=10)
        
        season_name = world.get_current_season()
        season_pct = (world.season_timer / config.SEASON_DURATION) * 100
        
        txt_season = self.font_title.render(f"Season: {season_name}", True, (255, 255, 255))
        surface.blit(txt_season, (margin + 15, margin + 12))
        
        # Draw season progress bar
        bar_rect = pygame.Rect(margin + 15, margin + 40, 210, 8)
        pygame.draw.rect(surface, (60, 60, 60), bar_rect, border_radius=4)
        progress_rect = pygame.Rect(margin + 15, margin + 40, int(210 * (season_pct / 100)), 8)
        
        # Season Bar Color
        bar_colors = {"Spring": (100, 240, 100), "Summer": (240, 220, 50), "Autumn": (220, 130, 30), "Winter": (100, 180, 255)}
        pygame.draw.rect(surface, bar_colors[season_name], progress_rect, border_radius=4)
        
        # Simulation Telemetry
        txt_time = self.font_body.render(f"Sim Steps: {world.time_steps} | Births: {world.birth_count}", True, (220, 220, 220))
        surface.blit(txt_time, (margin + 15, margin + 55))
        
        # Speed Indicator
        speed_txt = f"{sim_speed}x Speed" if not is_paused else "PAUSED"
        txt_speed = self.font_body_bold.render(speed_txt, True, (255, 100, 100) if is_paused else (100, 255, 100))
        surface.blit(txt_speed, (margin + 15, margin + 72))
        
        # 2. Population Count Panel
        pop_panel = pygame.Rect(config.WORLD_WIDTH - 200, margin, 185, 95)
        self.draw_rect_alpha(surface, (10, 10, 10, 120), pop_panel, border_radius=10)
        
        txt_h_cnt = self.font_body_bold.render(f"Herbivores: {len(world.herbivores)}", True, (130, 240, 130))
        txt_c_cnt = self.font_body_bold.render(f"Carnivores: {len(world.carnivores)}", True, (240, 130, 130))
        txt_g_cnt = self.font_body_bold.render(f"Grass: {len(world.grasses)}", True, (150, 220, 150))
        
        surface.blit(txt_h_cnt, (config.WORLD_WIDTH - 185, margin + 12))
        surface.blit(txt_c_cnt, (config.WORLD_WIDTH - 185, margin + 35))
        surface.blit(txt_g_cnt, (config.WORLD_WIDTH - 185, margin + 58))
        
        # 3. Average Genetics Summary Panel (Lower Left)
        stats_panel = pygame.Rect(margin, config.WORLD_HEIGHT - 170, 310, 155)
        self.draw_rect_alpha(surface, (10, 10, 10, 140), stats_panel, border_radius=10)
        
        txt_stats_title = self.font_title.render("Evolving Gene Averages", True, (255, 255, 255))
        surface.blit(txt_stats_title, (margin + 15, config.WORLD_HEIGHT - 162))
        
        if world.history:
            last = world.history[-1]
            # Herbivore Genes
            txt_h_stats = [
                f"Herbivore Speed: {last['avg_h_speed']:.2f}",
                f"Herbivore Vision: {last['avg_h_vision']:.1f}px",
                f"Herbivore Size: {last['avg_h_size']:.1f}",
                f"Herbivore Fear: {last['avg_h_fear']:.2f}"
            ]
            # Carnivore Genes
            txt_c_stats = [
                f"Carnivore Speed: {last['avg_c_speed']:.2f}",
                f"Carnivore Vision: {last['avg_c_vision']:.1f}px",
                f"Carnivore Size: {last['avg_c_size']:.1f}",
                f"Carnivore Aggression: {last['avg_c_agg']:.2f}"
            ]
            
            # Print columns
            for i, line in enumerate(txt_h_stats):
                lbl = self.font_body.render(line, True, (180, 255, 180))
                surface.blit(lbl, (margin + 15, config.WORLD_HEIGHT - 135 + i * 20))
                
            for i, line in enumerate(txt_c_stats):
                lbl = self.font_body.render(line, True, (255, 180, 180))
                surface.blit(lbl, (margin + 165, config.WORLD_HEIGHT - 135 + i * 20))
        else:
            lbl = self.font_body.render("Calculating genetic history...", True, (200, 200, 200))
            surface.blit(lbl, (margin + 15, config.WORLD_HEIGHT - 135))
            
        # 4. Draw Selected Creature Details Panel (Center-Right sidebar)
        if self.selected_creature:
            self.draw_inspector_panel(surface, self.selected_creature)
            
        # 5. Draw Population History Graph (Bottom-Right corner)
        if show_graph and len(world.history) > 1:
            self.draw_population_graph(surface, world)

    def draw_inspector_panel(self, surface, c):
        """Draws details panel of selected creature with lineage and genome metrics."""
        panel = pygame.Rect(config.WORLD_WIDTH - 290, 125, 275, 320)
        self.draw_rect_alpha(surface, (15, 25, 15, 180), panel, border_radius=10)
        pygame.draw.rect(surface, (100, 255, 100) if c.type == "herbivore" else (255, 100, 100), panel, 1, border_radius=10)
        
        # Title Species
        stype = "HERBIVORE" if c.type == "herbivore" else "CARNIVORE"
        title_color = (150, 255, 150) if c.type == "herbivore" else (255, 150, 150)
        txt_title = self.font_title.render(f"Inspect: {stype}", True, title_color)
        surface.blit(txt_title, (config.WORLD_WIDTH - 275, 135))
        
        # Meta info
        lines = [
            f"ID: {c.id}",
            f"Gen: {c.generation}  | Parent: {c.parent_id or 'None'}",
            f"Age: {c.age}/{c.max_age} frames",
            f"Energy: {c.energy:.1f}",
            f"State: {c.current_action.capitalize()}"
        ]
        
        for i, line in enumerate(lines):
            lbl = self.font_body.render(line, True, (240, 240, 240))
            surface.blit(lbl, (config.WORLD_WIDTH - 275, 165 + i * 18))
            
        # Divider
        div_y = 260
        pygame.draw.line(surface, (100, 100, 100), (config.WORLD_WIDTH - 275, div_y), (config.WORLD_WIDTH - 30, div_y))
        
        # Genome Header
        txt_g_header = self.font_body_bold.render("Genome Profile", True, (220, 220, 255))
        surface.blit(txt_g_header, (config.WORLD_WIDTH - 275, div_y + 8))
        
        # Gene values list
        gene_names = ["speed", "vision", "size", "energy_efficiency", "fear" if c.type == "herbivore" else "aggression", "reproduction_threshold", "turn_rate"]
        for idx, gname in enumerate(gene_names):
            val = c.genes.get(gname)
            # Display name translation
            disp_name = gname.replace("_", " ").title()
            
            lbl_name = self.font_small.render(disp_name, True, (180, 180, 200))
            lbl_val = self.font_small.render(f"{val:.2f}", True, (255, 255, 255))
            
            y_pos = div_y + 28 + idx * 15
            surface.blit(lbl_name, (config.WORLD_WIDTH - 275, y_pos))
            surface.blit(lbl_val, (config.WORLD_WIDTH - 60, y_pos))

    def draw_population_graph(self, surface, world):
        """Draws population charts tracking Herbivores, Carnivores, and Grass."""
        g_width = 310
        g_height = 155
        g_x = config.WORLD_WIDTH - g_width - 15
        g_y = config.WORLD_HEIGHT - g_height - 15
        
        panel = pygame.Rect(g_x, g_y, g_width, g_height)
        self.draw_rect_alpha(surface, (10, 10, 10, 140), panel, border_radius=10)
        
        # Title
        txt_title = self.font_title.render("Population History", True, (255, 255, 255))
        surface.blit(txt_title, (g_x + 15, g_y + 10))
        
        # Draw frame
        plot_rect = pygame.Rect(g_x + 35, g_y + 35, g_width - 50, g_height - 55)
        pygame.draw.rect(surface, (50, 50, 50), plot_rect, 1)
        
        # Find max bounds in history
        history = world.history
        if not history:
            return
            
        max_pop = max(max(pt["herbivores"], pt["carnivores"], pt["grass"] / 2.0) for pt in history)
        max_pop = max(max_pop, 20.0)  # avoid division by zero or super small scales
        
        pts_count = len(history)
        if pts_count < 2:
            return
            
        # Draw axes labels
        lbl_max = self.font_small.render(f"{int(max_pop)}", True, (200, 200, 200))
        lbl_zero = self.font_small.render("0", True, (200, 200, 200))
        surface.blit(lbl_max, (g_x + 8, plot_rect.top))
        surface.blit(lbl_zero, (g_x + 20, plot_rect.bottom - 10))
        
        # Draw line coordinates
        h_points = []
        c_points = []
        g_points = []
        
        step_x = plot_rect.width / (pts_count - 1)
        for idx, pt in enumerate(history):
            px = plot_rect.left + idx * step_x
            
            # Map Y coordinate (flip vertically inside rect)
            hy = plot_rect.bottom - (pt["herbivores"] / max_pop) * plot_rect.height
            cy = plot_rect.bottom - (pt["carnivores"] / max_pop) * plot_rect.height
            # Divide Grass by 2.0 to scale it down so it fits nicely on the graph
            gy = plot_rect.bottom - ((pt["grass"] / 2.0) / max_pop) * plot_rect.height
            
            h_points.append((int(px), int(max(plot_rect.top, min(plot_rect.bottom, hy)))))
            c_points.append((int(px), int(max(plot_rect.top, min(plot_rect.bottom, cy)))))
            g_points.append((int(px), int(max(plot_rect.top, min(plot_rect.bottom, gy)))))
            
        # Plot lines
        pygame.draw.lines(surface, (130, 240, 130), False, h_points, 2)
        pygame.draw.lines(surface, (240, 130, 130), False, c_points, 2)
        pygame.draw.lines(surface, (150, 150, 255), False, g_points, 1)

    def handle_click(self, mouse_pos, world):
        """Checks if a creature was clicked to inspect its profile."""
        mx, my = mouse_pos
        self.selected_creature = None
        
        all_creatures = world.herbivores + world.carnivores
        best_match = None
        min_dist = 25.0  # click radius
        
        for c in all_creatures:
            if not c.alive:
                continue
            dist = math.hypot(c.x - mx, c.y - my)
            if dist < min_dist:
                min_dist = dist
                best_match = c
                
        if best_match:
            self.selected_creature = best_match
            return True
        return False
