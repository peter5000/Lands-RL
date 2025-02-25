# noqa: D212, D415
"""
# Connect Four

```{figure} classic_connect_four.gif
:width: 140px
:name: connect_four
```

This environment is part of the <a href='..'>classic environments</a>. Please read that page first for general information.

| Import             | `from pettingzoo.classic import connect_four_v3` |
|--------------------|--------------------------------------------------|
| Actions            | Discrete                                         |
| Parallel API       | Yes                                              |
| Manual Control     | No                                               |
| Agents             | `agents= ['player_0', 'player_1']`               |
| Agents             | 2                                                |
| Action Shape       | (1,)                                             |
| Action Values      | Discrete(7)                                      |
| Observation Shape  | (6, 7, 2)                                        |
| Observation Values | [0,1]                                            |


Connect Four is a 2-player turn based game, where players must connect four of their tokens vertically, horizontally or diagonally. The players drop their respective token in a column of a standing grid, where each token will fall until it reaches the bottom of the column or reaches an existing
token. Players cannot place a token in a full column, and the game ends when either a player has made a sequence of 4 tokens, or when all 7 columns have been filled.

### Observation Space

The observation is a dictionary which contains an `'observation'` element which is the usual RL observation described below, and an  `'action_mask'` which holds the legal moves, described in the Legal Actions Mask section.


The main observation space is 2 planes of a 6x7 grid. Each plane represents a specific agent's tokens, and each location in the grid represents the placement of the corresponding agent's token. 1 indicates that the agent has a token placed in that cell, and 0 indicates they do not have a token in
that cell. A 0 means that either the cell is empty, or the other agent has a token in that cell.


#### Legal Actions Mask

The legal moves available to the current agent are found in the `action_mask` element of the dictionary observation. The `action_mask` is a binary vector where each index of the vector represents whether the action is legal or not. The `action_mask` will be all zeros for any agent except the one
whose turn it is. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents.


### Action Space

The action space is the set of integers from 0 to 6 (inclusive), where the action represents which column a token should be dropped in.

### Rewards

If an agent successfully connects four of their tokens, they will be rewarded 1 point. At the same time, the opponent agent will be awarded -1 points.


### Version History

* v0: Initial versions (0.0.1)

"""
from __future__ import annotations

import os

import gymnasium
import numpy as np
import pygame
from gymnasium import spaces
from gymnasium.utils import EzPickle

from pettingzoo import AECEnv
from pettingzoo.utils import wrappers
from pettingzoo.utils.agent_selector import agent_selector as AgentSelector

import lands_game as lg
import lands_vars as lv


def get_image(path):
    from os import path as os_path

    import pygame

    cwd = os_path.dirname(__file__)
    image = pygame.image.load(cwd + "/" + path)
    sfc = pygame.Surface(image.get_size(), flags=pygame.SRCALPHA)
    sfc.blit(image, (0, 0))
    return sfc


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(AECEnv, EzPickle):
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "name": "lands",
        "is_parallelizable": False,
        "render_fps": 2,
    }

    def __init__(self, render_mode: str | None = None, screen_scaling: int = 9):
        EzPickle.__init__(self, render_mode, screen_scaling)
        super().__init__()
        # 6 rows x 7 columns
        # blank space = 0
        # agent 0 -- 1
        # agent 1 -- 2
        # flat representation in row major order
        self.screen = None
        self.render_mode = render_mode
        self.screen_scaling = screen_scaling

        self.agents = ["player_0", "player_1"]
        self.possible_agents = self.agents[:]

        self.last_action = None

        self.game = lg.LandsGame()

        self.action_spaces = {
            i: spaces.MultiDiscrete(
                [4, 55]
            )
            for i in self.agents
        }
        self.observation_spaces = {
            i: spaces.Dict(
                {
                    "observation": spaces.Box(
                        low=0, high=6, shape=(7,5), dtype=np.int8
                    ),
                    "action_mask": spaces.MultiDiscrete(
                        [4, 55]
                    ),
                }
            )
            for i in self.agents
        }

        if self.render_mode == "human":
            self.clock = pygame.time.Clock()

    # Key
    # ----
    # blank space = 0
    # agent 0 = 1
    # agent 1 = 2
    # An observation is list of lists, where each list represents a row
    #
    # array([[0, 1, 1, 2, 0, 1, 0],
    #        [1, 0, 1, 2, 2, 2, 1],
    #        [0, 1, 0, 0, 1, 2, 1],
    #        [1, 0, 2, 0, 1, 1, 0],
    #        [2, 0, 0, 0, 1, 1, 0],
    #        [1, 1, 2, 1, 0, 1, 0]], dtype=int8)
    def observe(self, agent):
        cur_player = self.possible_agents.index(agent)
        opp_player = (cur_player + 1) % 2
        legal_moves = self._legal_moves()
        curr_hand = self.game.players[cur_player]["hand"]
        curr_field = self.game.players[cur_player]["field"]
        opp_field = self.game.players[opp_player]["field"]
        # curr_discard = self.game.players[cur_player]["discard"]
        # opp_discard = self.game.players[opp_player]["discard"]
        curr_action = [self.game.playing[0] if self.game.playing else 5] * 5
        scryed_card = [0]*5
        if self.game.scryed_card:
            scryed_card[self.game.scryed_card] = 1
        revealed = [0]*5
        if self.game.revealed_cards:
            for i in self.game.revealed_cards:
                revealed[i] += 1
        counter = [1 if self.game.countered else 0] * 5
        observation = np.array([curr_hand, curr_field, opp_field, curr_action, revealed, counter, scryed_card])

        return {"observation": observation, "action_mask": legal_moves}

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def _legal_moves(self):
        action_mask = (np.array([0]*4, dtype=np.int8), np.array([0]*55, dtype=np.int8))
        for action in self.game.possible_actions:
            action_choice = action[0]
            action_data = action[1]

            action_mask[0][action_choice] = 1
            action_mask[1][action_data] = 1
        return action_mask

    # action in this case is a value from 0 to 6 indicating position to move on the flat representation of the connect4 board
    def step(self, action):
        if (
            self.truncations[self.agent_selection]
            or self.terminations[self.agent_selection]
        ):
            return self._was_dead_step(action)
        
        self.game.play_move(action)

        self.last_action = action

        winner = self.game.win()

        # check if there is a winner
        if winner:
            self.rewards[self.possible_agents[winner - 1]] += 1
            self.rewards[self.possible_agents[winner - 2]] -= 1
            self.terminations = {i: True for i in self.agents}

        self.agent_selection = self.possible_agents[self.game.sub_turn]

        self._accumulate_rewards()

        if self.render_mode == "human":
            self.render()

    def reset(self, seed=None, options=None):
        # reset environment
   
        self.game.reset_game()

        self.last_action = None

        self.agents = self.possible_agents[:]
        self.rewards = {i: 0 for i in self.agents}
        self._cumulative_rewards = {name: 0 for name in self.agents}
        self.terminations = {i: False for i in self.agents}
        self.truncations = {i: False for i in self.agents}
        self.infos = {i: {} for i in self.agents}

        self._agent_selector = AgentSelector(self.agents)

        self.agent_selection = self._agent_selector.reset()

    def close(self):
        if self.screen is not None:
            pygame.quit()
            self.screen = None


    def render(self):
        if self.render_mode is None:
            gymnasium.logger.warn(
                "You are calling render method without specifying any render mode."
            )
            return
        
        print("-"*50)
        print(f"Current Turn: {self.game.turn}")
        print(f"Current Sub Turn: {self.game.sub_turn}")
        print(f"Last Action: {self.last_action}")
        print(f"Current Playing: {self.game.playing[0] if self.game.playing else None}")
        print(f"Current Counter Status: {self.game.countered}")
        print(f"Current Revealed Cards: {self.game.revealed_cards}")
        print(f"Current Scryed Card: {self.game.scryed_card}")
        print(f"Current Possible Actions: {self.game.possible_actions}")
        print("-" * 50)
        print(f"{'Player':<10}{'Hand':<20}{'Field':<20}{'Discard':<20}")
        print(f"{'-'*10}{'-'*20}{'-'*20}{'-'*20}")
        print(lv.ELEMENTS)
        for i in range(2):
            print(f"{f'Player_{i}':<10}{str(self.game.players[i]['hand']):<20}{str(self.game.players[i]['field']):<20}{str(self.game.players[i]['discard']):<20}")
        


