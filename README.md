# EvoLife Sandbox

A small Python/Pygame ecosystem simulation where herbivores and carnivores survive, reproduce, and mutate over time.

The project is designed as a lightweight evolution sandbox:

- grass spawns across the world
- herbivores search for grass and flee predators
- carnivores chase herbivores
- creatures spend energy based on speed, vision, size, age, and efficiency
- successful creatures reproduce with mutated genes
- population and average gene statistics are shown in real time

## Requirements

- Python 3.11+
- Pygame 2.5+

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

Because the source code lives under `src/`, run with `PYTHONPATH=src`:

```bash
PYTHONPATH=src python main.py
```

Windows PowerShell:

```powershell
$env:PYTHONPATH="src"
python main.py
```

## Controls

| Input | Action |
| --- | --- |
| Space | Pause / resume |
| F | Change simulation speed |
| V | Toggle vision circles |
| R | Reset the world |
| S | Save recent stats to `evolife_stats.csv` |
| Left click | Add grass |
| Right click | Add herbivore |
| Shift + right click | Add carnivore |
| Esc | Quit |

## What evolves?

Each creature carries genes:

- `speed`
- `vision`
- `size`
- `efficiency`
- `fear`
- `aggression`
- `reproduction_threshold`
- `turn_rate`

When a creature has enough energy, it creates a child. The child inherits the parent's genes with small random mutations. Over time, the visible population changes as different traits become more or less useful.

## Suggested next improvements

- add terrain zones such as forest, desert, and water
- replace rule-based behavior with a small neural network brain
- add save/load for worlds and best lineages
- add species clustering and genealogy visualization
- add charts for gene distributions
