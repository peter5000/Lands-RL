# Lands-RL

## File Structure
  envs - directory with all the environments

  lands_vars.py - contains macros
  lands_game.py - lands game object
  players.py - lands players

```python
from pettingzoo.utils import TerminateIllegalWrapper
```

Update TerminateIllegalWrapper to handle multidiscrete action mask

```python
63     self._was_dead_step(action)  # pyright: ignore[reportGeneralTypeIssues]
64 elif (
65     not self.terminations[self.agent_selection]
66     and not self.truncations[self.agent_selection]
67     # and not _prev_action_mask[action]
68     and not _prev_action_mask[0][action[0]] # new
69     and not _prev_action_mask[1][action[1]] # new
70 ):
71     EnvLogger.warn_on_illegal_move()
```
