# main.py
"""
Main driver script for EvoLife Sandbox.
Handles application lifecycle, input dispatching, and frame ticks.
"""

import sys

import pygame

import config
from renderer import Renderer
from world import World


SIM_SPEEDS = (1, 2, 4, 8)


def next_speed(current_speed):
    """Cycle through the available simulation speed multipliers."""
    try:
        index = SIM_SPEEDS.index(current_speed)
    except ValueError:
        return SIM_SPEEDS[0]

    return SIM_SPEEDS[(index + 1) % len(SIM_SPEEDS)]


def main():
    pygame.init()
    pygame.display.set_caption("EvoLife Sandbox — Ecosystem & Genetic Evolution")

    screen = pygame.display.set_mode((config.WORLD_WIDTH, config.WORLD_HEIGHT))
    clock = pygame.time.Clock()

    world = World()
    renderer = Renderer()

    is_paused = False
    sim_speed = config.DEFAULT_SIMULATION_SPEED
    show_vision = config.DEFAULT_SHOW_VISION
    show_graph = config.DEFAULT_SHOW_HUD

    running = True

    while running:
        clock.tick(config.TARGET_FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    is_paused = not is_paused
                elif event.key == pygame.K_f:
                    sim_speed = next_speed(sim_speed)
                elif event.key == pygame.K_v:
                    show_vision = not show_vision
                elif event.key == pygame.K_g:
                    show_graph = not show_graph
                elif event.key == pygame.K_r:
                    world.reset()
                    renderer.selected_creature = None

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                mods = pygame.key.get_mods()

                if event.button == 1:
                    clicked_creature = renderer.handle_click(mouse_pos, world)
                    if not clicked_creature:
                        if mods & pygame.KMOD_SHIFT:
                            world.add_carnivore_at(mouse_pos[0], mouse_pos[1])
                        else:
                            world.add_grass_at(mouse_pos[0], mouse_pos[1])

                elif event.button == 3:
                    world.add_herbivore_at(mouse_pos[0], mouse_pos[1])

        if not is_paused:
            world.update(dt=1.0 / config.TARGET_FPS, sim_speed=sim_speed)

        season = world.get_current_season()
        bg_color = config.SEASON_MODIFIERS[season]["bg_color"]
        screen.fill(bg_color)

        renderer.draw_regions(screen)
        renderer.draw_particles(screen, season)
        renderer.draw_world(screen, world, show_vision)
        renderer.draw_hud(screen, world, sim_speed, is_paused, show_graph)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
