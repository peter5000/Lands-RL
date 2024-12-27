import numpy as np
import gymnasium as gym
from gymnasium.spaces import Box, Dict, Discrete, MultiDiscrete
import json
import traceback
import lands_vars as lv

class LandsEnv(gym.Env):
    # TODO: action space and other initializations
    def __init__(
        self,
        num_elements=5,
        num_cards=5,
        start_hand=5
        # Params
    ):
        # 5 colors, 5 cards, own hand + 2 fields
        self.observation_space = Box(low=0, high=5, shape=(3,5), dtype=np.int8)

        # 0=Pass, 1=Green, 2=Yellow, 3=Red, 4=Dark, 5=Water
        # Prob need tuple or something for card effects
        self.action_space = Box(low=0, high=5, shape=(2), dtype=np.int8)

        # 0=p1, 1=p2
        self.turn = 0

        # self.render_mode = None
        # self.num_steps = 0
        # self.max_steps = max_steps

        # Game meta variables initialization
        self.num_elements = num_elements
        self.num_cards = num_cards
        self.start_hand = start_hand

        # Game variables initialization
        self.field = np.zeros((2, lv.NUM_ELEMENTS))       # p1 = first row, p2 = second row
        self.p1 = {"field": np.zeros(lv.NUM_ELEMENTS), "hand": np.zeros((lv.NUM_ELEMENTS)), "discard": np.zeros((lv.NUM_ELEMENTS)), "deck": None}
        self.p2 = {"field": np.zeros(lv.NUM_ELEMENTS), "hand": np.zeros((lv.NUM_ELEMENTS)), "discard": np.zeros((lv.NUM_ELEMENTS)), "deck": None}
        self._init_deck(self.p1)
        self._init_deck(self.p2)
        self._draw_n(self.p1, self.start_hand)
        self._draw_n(self.p2, self.start_hand)

    # Shuffle the deck
    def _shuffle_deck(self, player):
        np.random.shuffle(player["deck"])

    # Initialize deck
    def _init_deck(self, player):
        player["deck"] = np.array([(i)//(self.num_cards) + 1 for i in range(self.num_elements*self.num_cards)])
        self._shuffle_deck(player)

    # Add all cards in discard pile to the deck and shuffle
    # return (new_deck, new_discard)
    def _put_discard_to_deck(self, player):
        player["deck"].append(np.array([[n+1]*i for n, i in enumerate(player["discard"])]).reshape(-1))
        player["discard"].fill(0)
        self._shuffle_deck(player)

    # Draw one card from the deck to the hand
    def _draw_n(self, player, n=1):
        if len(player["deck"]) < 1:
            self._put_discard_to_deck(player)
            assert len(player["deck"]) > 0    # We want deck to contain at least 1 card
        for i in range(n):
            player["hand"][player["deck"][i]-1] += 1
        player["deck"] = player["deck"][n:]

    # reset state of a player
    def _reset_states(self, player):
        player["hand"].fill(0)
        player["discard"].fill(0)
        self._init_deck(player)
        self._draw_n(player, self.start_hand)

    # TODO: Move validation function

    # TODO: Play a card

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
