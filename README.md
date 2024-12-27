# Lands-RL

## File Structure
  envs - directory with all the environments

  lands_vars.py - contains macros

  lands_game.py - lands game object

  players.py - lands players

## TO-DOs
- Implement game mechanics
  - move validation function
  - playing a card
    - yellow
    - fire
    - green
    - dark (random)
    - water (no effect)
- env necessities
  - reward function
  - get obs
  - step function
- rendering

## Scratch space

Order of Operation

yellow, fire, green, dark(random cards), ->  water(type 1) -> water (type 2) -> dark

Possible observation space with reaction

[
  [3,1,0,1,0],
  [1,0,1,0,0],
  [0,2,0,0,0],
  [previous action]
]

Invalid move -> negative reward and terminate the game

Next step
- action masking