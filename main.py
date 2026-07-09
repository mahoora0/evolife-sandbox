# main.py
"""
Main driver script for EvoLife Sandbox.
Handles application lifecycle, input dispatching, time accumulation, and frame ticks.
"""

import sys
import pygame
import config
from world import World
from renderer import Renderer

def main():
    pygame.init()
    pygame.display.set_caption("EvoLife Sandbox — Ecosystem & Genetic Evolution")
    
    # Create window
    screen = pygame.display.set_mode((config.WORLD_WIDTH, config.WORLD_HEIGHT))
    clock = pygame.time.Clock()
    
    # Simulation Systems
    world = World()
    renderer = Renderer()
    
    # UI Toggles & States
    is_paused = False
    sim_speed = config.DEFAULT_SIMULATION_SPEED  # 1, 2, 4
    show_vision = config.DEFAULT_SHOW_VISION
    show_graph = config.DEFAULT_SHOW_HUD
    
    running = True
    
    while running:
        dt = clock.tick(config.TARGET_FPS) / 1000.0
        
        # 1. Handle Input Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    is_paused = not is_paused
                elif event.key == pygame.K_f:
                    # Toggle speed (1x -> 2x -> 4x -> 1x)
                    if sim_speed == 1:
                        sim_speed = 2
                    elif sim_speed == 2:
                        sim_speed = 4
                    else:
                        sim_speed = 1
                elif event.key == pygame.K_v:
                    show_vision = not show_vision
                elif event.key == pygame.K_g:
                    show_graph = not show_graph
                elif event.key == pygame.K_r:
                    world.reset()
                    renderer.selected_creature = None
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check clicks
                if event.button == 1:  # Left Click
                    # Attempt selection first
                    clicked_creature = renderer.handle_click(mouse_pos, world)
                    if not clicked_creature:
                        # Shift + Left click spawns Carnivore
                        mods = pygame.key.get_mods()
                        if mods & pygame.KMOD_SHIFT:
                            world.add_carnivore_at(mouse_pos[0], mouse_pos[1])
                        else:
                            # Standard Left click spawns Grass
                            world.add_grass_at(mouse_pos[0], mouse_pos[1])
                            
                elif event.button == 3:  # Right Click
                    # Right click spawns Herbivore
                    world.add_herbivore_at(mouse_pos[0], mouse_pos[1])
                    
        # 2. Logic Update
        if not is_paused:
            # Pass sim_speed to run world updates multiple times per frame if sped up
            world.update(dt=1.0/config.TARGET_FPS, sim_speed=sim_speed)
            
        # 3. Blit seasonal background color with smooth transition
        current_season = world.get_current_season()
        current_mod = config.SEASON_MODIFIERS[current_season]
        next_season = config.SEASONS[(world.current_season_idx + 1) % len(config.SEASONS)]
        next_mod = config.SEASON_MODIFIERS[next_season]
        
        # Transition over the last 5 seconds of the season duration
        transition_time = 5.0
        time_left = config.SEASON_DURATION - world.season_timer
        if time_left < transition_time:
            t = (transition_time - time_left) / transition_time
            bg_color = tuple(
                int(current_mod["bg_color"][i] * (1.0 - t) + next_mod["bg_color"][i] * t)
                for i in range(3)
            )
        else:
            bg_color = current_mod["bg_color"]
            
        screen.fill(bg_color)
        
        # 4. Render World Elements
        renderer.draw_regions(screen)
        renderer.draw_particles(screen, current_season)
        renderer.draw_world(screen, world, show_vision)
        renderer.draw_hud(screen, world, sim_speed, is_paused, show_graph)
        
        # 5. Flip Screen
        pygame.display.flip()
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
