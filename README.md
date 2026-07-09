# EvoLife Sandbox

A Python/Pygame ecosystem sandbox where grass, herbivores, and carnivores interact inside a small evolving world.

The simulation includes:

- regional grass growth across forest, plains, and desert zones
- seasonal modifiers for grass growth, grass energy, metabolism, background color, and particles
- herbivore behavior: eat grass, flee carnivores, wander
- carnivore behavior: chase and eat herbivores, wander
- genetic inheritance with mutation across generations
- real-time HUD, population graph, and creature inspector

## Requirements

- Python 3.10+
- Pygame 2.5+

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Controls

| Input | Action |
| --- | --- |
| Space | Pause / resume |
| F | Change simulation speed |
| V | Toggle vision circles |
| G | Toggle population graph |
| R | Reset the world |
| Left click creature | Inspect creature |
| Left click empty area | Add grass |
| Shift + left click | Add carnivore |
| Right click | Add herbivore |
| Esc | Quit |

## What evolves?

Each creature carries genes:

- `speed`
- `vision`
- `size`
- `energy_efficiency`
- `fear`
- `aggression`
- `reproduction_threshold`
- `turn_rate`

When a creature has enough energy, it reproduces. The child inherits the parent's genome with random mutations. Over time, the population shifts toward traits that work better in the current ecosystem.

## Current stability improvements

This version includes safeguards for longer-running simulations:

- population caps for herbivores and carnivores
- vision queries that use squared-distance checks before returning a target
- spatial-grid refresh after herbivore movement so carnivores chase fresh positions
- configurable grass energy instead of hard-coded seasonal energy values
- safer child spawn positions near world boundaries
- bounded telemetry history length

## Suggested next improvements

- add terrain movement costs for forest, plains, and desert
- export gene statistics to CSV
- add a small neural-network brain as an optional behavior mode
- add save/load for worlds and notable lineages
- add species clustering and genealogy visualization
