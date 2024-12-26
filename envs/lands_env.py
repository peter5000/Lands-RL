import numpy as np
import gymnasium as gym
from gymnasium.spaces import Box, Dict, Discrete, MultiDiscrete
import json
import traceback

class LandsEnv(gym.Env):
    # TODO: action space and other initializations
    def __init__(
        self,
        # Params
    ):
        # 5 colors, 5 cards, own hand + 2 fields
        self.observation_space = Box(low=0, high=5, shape=(3,5), dtype=np.int8)

        # 0=Green, 1=Yellow, 2=Red, 3=Dark, 4=Water, 5=Pass
        # Prob need tuple or something for card effects
        self.action_space = Discrete(6)

        # self.board = init_board()

        # self.render_mode = None
        # self.num_steps = 0
        # self.max_steps = max_steps

    # TODO: unimplemented
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self._setup_input_file(
            inference_mode=False if options is None else options["inference_mode"]
        )
        self.prev_obs = [self._grid_lists.copy()]
        self.num_steps = 0
        return self._get_obs(), self._get_info()

    # TODO: unimplemented
    def _get_info(self):
        return {}

    # TODO: unimplemented
    def _get_obs(self):
        return self.board

    # TODO: unimplemented, change to game finished or is_win
    def _is_solution(self):
        return None

    # TODO: unimplemented
    def step(self, action):
        (
            assignment_type,
            grid_list_index,
            grid_index,
            rhs_function,
            rhs_arg1,
            rhs_arg2,
        ) = action
        # update state

        # get observation
        observation = self._get_obs()
        terminated = self._is_solution()
        if terminated:
            reward = 1
        else:
            reward = 0

        # self.num_steps += 1

        truncated = self.num_steps >= self.max_steps
        info = self._get_info()
        return (observation, reward, terminated, truncated, info)

    def __repr__():
        return "Hello World"
