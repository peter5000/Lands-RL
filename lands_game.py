import numpy as np
import lands_vars as lv
from itertools import combinations_with_replacement

class LandsGame():
  def __init__(self, num_elements=lv.NUM_ELEMENTS, num_cards=lv.NUM_CARDS, start_hand=lv.START_HAND, player_count = lv.PLAYER_COUNT):
    # Game meta variables initialization
    self.num_elements = num_elements
    self.num_cards = num_cards
    self.start_hand = start_hand
    self.player_count = player_count

    # gameover flag
    self.gameover = False

    # 0 = player1, 1 = player2
    self.turn = 0

    # 0 = player1, 1 = player2
    self.sub_turn = 0

    # intialize players and states
    self.players = [
          {
            "field": np.zeros((lv.NUM_ELEMENTS)),
            "hand": np.zeros((lv.NUM_ELEMENTS)),
            "discard": np.zeros((lv.NUM_ELEMENTS)),
            "deck": None
          } 
        for _ in range(self.player_count) ]
    
    # initialize deck and draw starting hands
    for i in range(self.player_count):
      self._init_deck(i)
      self.draw_n(i, self.start_hand)

    # quantity of each card revealed for black
    self.revealed_cards = None

    # cards played over course of turn
    self.playing = []

    self.countered = False

    self.scryed_card = None

    self.possible_actions = self.cards_to_play_choices(self.turn)



  def play_move(self, action):
    """
    Play a move in the game

    Args:
    action: list of integers, the action to play
    """
    action_choice = action[0] # the type of action
    action_data = action[1] # the data associated with the action

    # update the game state based on the action
    match action_choice:

      # case the player plays a card
      # action_data is the type of card played
      case lv.PLAY_CARD:
        self.playing = [action_data] # set the card played
        self.pass_sub_turn() # update subturn to the player who has a chance to counter
        self.possible_actions = self.counter_choices(self.sub_turn) # give opponent a chance to counter
      
      # case the player takes a counter action
      # action_data is 1 if the player chooses to counter, 0 if not
      case lv.COUNTER:
        if action_data == 1: # if the player chooses to counter
          self.counter(self.sub_turn) # counter the card
          self.pass_sub_turn() # update subturn to the player who has a chance to counter
          self.possible_actions = self.counter_choices(self.sub_turn) # give opponent a chance to counter
        else: # if the player chooses not to counter
          if self.turn == self.sub_turn and self.countered: # if the counter went through
            self._move_x_to_x(self.turn, "hand", "discard", self.playing[0])  # discard the card played that was countered
            self.pass_turn() # pass the turn
          else: # if the counter doesn't go through
            self.resolve_card_init() # resolve the card played
          
      # case a player reveals cards
      # action_data is a combination index tied to the cards revealed
      case lv.REVEAL:
        self.revealed_cards = lv.IDX_TO_COMBINATION[action_data] # set the cards revealed
        self.sub_turn = self.turn # update subturn to the player who has to pick a card
        self.possible_actions = self.pick_from_revealed_choices() # player must pick from the revealed cards

      # case a player resolves a card
      # action_data is the choice associated with the card resolution
      case lv.RESOLVE_CARD:
        self.resolve_card_final(action_data) # resolve the card played

    return (self.possible_actions, self.turn, self.sub_turn)

  def resolve_card_init(self):
    """
    Resolve the card played
    """
    self.sub_turn = self.turn # update subturn to the player who has to resolve the card
    self._move_x_to_x(self.turn, "hand", "field", self.playing[0]) # move the card played to the field

    # resolve the card
    match self.playing[0]:

      # case the player plays a grass card
      case lv.GRASS:
        if np.any(self.players[self.turn]["discard"] > 0): # if the player has cards in the discard pile
          self.possible_actions = self.green_choices(self.turn) # player must choose a card to move from discard to hand
        else: # if the player has no cards in the discard pile
          self.pass_turn() # pass the turn

      # case the player plays a yellow card
      case lv.YELLOW:
        self.draw_n(self.turn, n=1) # draw a card
        self.pass_turn() # pass the turn

      # case the player plays a fire card
      case lv.FIRE:
        if np.any(self.players[1-self.turn]["field"] > 0): # if the opponent has cards in play
          self.possible_actions = self.fire_choices(self.turn) # player must choose a card to discard from the opponent's field
        else: # if the opponent has no cards in play
          self.pass_turn() # pass the turn

      # case the player plays a dark card
      case lv.DARK:
        if np.any(self.players[1-self.turn]["hand"] > 0): # if the opponent has cards in their hand
          self.pass_sub_turn() # update subturn to the player who has to reveal cards
          self.possible_actions = self.reveal_card_choices(self.sub_turn) # player must reveal cards
        else: # if the opponent has no cards in their hand
          self.pass_turn() # pass the turn

      # case the player plays a water card
      case lv.WATER:
        if np.any(self.players[self.turn]["deck"] > 0) or np.any(self.players[self.turn]["discard"] > 0): # if the player has cards in the deck or discard pile
          self.possible_actions = self.scry_choices(self.turn) # player must scry
        else: # if the player has no cards in the deck or discard pile
          self.pass_turn() # pass the turn


  def resolve_card_final(self, action_data):

    # resolve the card
    match self.playing[0]:

      # case the player plays a grass card
      case lv.GRASS:
        self._move_x_to_x(self.turn, "discard", "hand", action_data) # move the choosen card from discard to hand

      # case the player plays a fire card
      case lv.FIRE:
        self._move_x_to_x(1-self.turn, "field", "discard", action_data) # discard the card selected from the opponent's field

      # case the player plays a dark card
      case lv.DARK:
        self._move_x_to_x(1-self.turn, "hand", "discard", action_data) # discard the card selected from the opponent's hand

      # case the player plays a water card
      case lv.WATER:
        if action_data == 1: # if the player chooses to moves the card
          self.move_top_card_to_bottom(self.turn) # move the top card to the bottom of the deck
    try:
      self.pass_turn() # pass the turn
    except:
      print(self._get_board())
      print(action_data)
      print(self.playing)
      print(self.turn)
      print(self.sub_turn)
      print(self.possible_actions)

  def pass_turn(self):
    winner = self.win() # check for a win con
    if winner is not None: # if there is a winner
      self.gameover = True  # set the gameover flag
      return
    self.turn = 1 - self.turn # switch the turn
    self.sub_turn = self.turn  # update subturn to the current player
    self.reset_vars() # reset the game state variables
    self.draw_n(self.turn, n=1) # draw a card for turn
    self.possible_actions = self.cards_to_play_choices(self.turn) # set the opponent's choices

  def reset_vars(self):
    self.playing = []
    self.countered = False
    self.scryed_card = None
    self.revealed_cards = None

  # cards a player can play
  def cards_to_play_choices(self, player):
    return [[lv.PLAY_CARD, i] for i in range(self.num_elements) # for each card type
            if self.players[player]["hand"][i] > 0] # if the player has the card in their hand they can play it

  # counter choices
  def counter_choices(self, player):
    legal_moves = [[lv.COUNTER, 0]] # player can choose not to counter
    countered_card = self.players[player]["hand"][self.playing[-1]] # card played by the opponent
    num_water = self.players[player]["hand"][lv.WATER] # number of water cards in the player's hand
    needed_water = 2 if self.playing[-1] == lv.WATER else 1 # number of water cards needed to counter
    if self.turn == self.sub_turn and self.playing[0] == lv.WATER: # if it is the current player's turn and the card played is water
      needed_water += 1 # the player needs an extra water card to counter
    if num_water >= needed_water and countered_card > 0: # if the player has enough water cards and the card played by the opponent is in the player's hand
      legal_moves.append([lv.COUNTER, 1]) # player can choose to counter
    return legal_moves # set the possible actions
    
  # counter a card played by the opponent
  def counter(self, player):
    self._move_x_to_x(player, "hand", "discard", self.playing[-1]) # discard the card played by the opponent
    self._move_x_to_x(player, "hand", "discard", lv.WATER) # discard water
    self.playing.append(lv.WATER) # add water to the cards played
    if self.turn == self.sub_turn: # if it is the currents player's turn
      self.countered = False # the counter was countered
    else: # if it is the opponent's turn
      self.countered = True # the counter went through

  # playing water and you scry (assumes you have cards in deck or discard)
  def scry_choices(self, player):
    if len(self.players[player]["deck"]) < 1: # if the deck is empty
      self._put_discard_to_deck(player) # put the discard pile back into the deck
    self.scryed_card = self.players[player]["deck"][0] # set the scryed card
    return [[lv.RESOLVE_CARD, i] for i in range(2)] # player can choose to keep the card on top or move it to the bottom

  # opponent is playing black and you have to reveal 3 cards
  def reveal_card_choices(self, player):
    legal_moves = [] # possible actions
    max_reveal = min(3, np.sum(self.players[player]["hand"])) # maximum number of cards the player can reveal
    for comb in combinations_with_replacement(range(5), int(max_reveal)): # for each combination of cards the player can reveal
      reveal = [0] * 5 # initialize the cards revealed
      for i in comb: # for each card in the combination
        if reveal[i] < int(self.players[player]["hand"][i]): # if the player has enough of the card in their hand
          reveal[i] += 1 # add the card to the cards revealed
      if sum(reveal) == max_reveal: # if the player has revealed enough cards
        legal_moves.append([lv.REVEAL, lv.COMBINATION_TO_IDX[comb]]) # add the combination to the possible actions
    return legal_moves # return the possible actions

  # playing dark and you have to choose a card to discard from the opponent's hand
  def pick_from_revealed_choices(self):
    return [[lv.RESOLVE_CARD, i] for i in set(self.revealed_cards)] # can pick any of the cards revealed

  # playing grass and you have to choose a card to move from discard to hand
  def green_choices(self, player):
    return [[lv.RESOLVE_CARD, i] for i in range(self.num_elements) # for each card type
        if self.players[player]["discard"][i] > 0 # if the player has the card in the discard pile they can choose it
      ]

  # playing fire and you have to choose a card to discard from the opponent's field 
  def fire_choices(self, player):
    return [[lv.RESOLVE_CARD, i] for i in range(self.num_elements) # for each card type
        if self.players[1-player]["field"][i] > 0 # if the opponent has the card in play you can choose it
      ]
  
  def pass_sub_turn(self):  
    self.sub_turn = 1 - self.sub_turn
  
  # move the top card to the bottom of the deck
  def move_top_card_to_bottom(self, player):
    self.players[player]["deck"] = np.append(self.players[player]["deck"], self.players[player]["deck"][0])
    self.players[player]["deck"] = self.players[player]["deck"][1:]

  # Shuffle the deck
  def _shuffle_deck(self, player):
    np.random.shuffle(self.players[player]["deck"])

  # Initialize deck
  def _init_deck(self, player):
    self.players[player]["deck"] = np.array([i//(self.num_cards) for i in range(self.num_elements*self.num_cards)], dtype=np.int8)
    self._shuffle_deck(player)

  # Add all cards in discard pile to the deck and shuffle
  def _put_discard_to_deck(self, player):
    discard_cards = []
    for n, i in enumerate(self.players[player]["discard"]):
      discard_cards.extend([n] * int(i))
    self.players[player]["deck"] = np.append(self.players[player]["deck"], discard_cards)
    self.players[player]["discard"].fill(0)
    self._shuffle_deck(player)

  # Draw n cards from the deck to the hand
  def draw_n(self, player, n=1):
    for _ in range(n): # draw n cards
      if len(self.players[player]["deck"]) < 1: # if the deck is empty
        self._put_discard_to_deck(player) # put the discard pile back into the deck
      if len(self.players[player]["deck"]) < 1: # if the deck is still empty
        return # stop drawing
      self.players[player]["hand"][self.players[player]["deck"][0]] += 1 # draw the card
      self.players[player]["deck"] = self.players[player]["deck"][1:] # remove the card from the deck

  # Reset the state of a given player
  def _reset_states(self, player):
    self.players[player]["hand"].fill(0)
    self.players[player]["field"].fill(0)
    self.players[player]["discard"].fill(0)
    self._init_deck(player)
    self.draw_n(player, self.start_hand)

  # Reset the game
  def reset_game(self):
    for i in range(self.player_count):
      self._reset_states(i)
    self.turn = 0
    self.sub_turn = self.turn
    self.gameover = False
    self.reset_vars()
    self.possible_actions = self.cards_to_play_choices(self.turn)


  # Retrieve the board in a format:
  # row 1: player 1's hand,
  # row 2: player 1's field
  # row 3: player 2's field
  # row 4: player 2's hand,
  def _get_board(self):
    return np.stack(
      (
        self.players[0]["hand"],
        self.players[0]["field"],
        self.players[1]["field"],
        self.players[1]["hand"]
      )
    )

  # check for a win con and return a player number of the winner else none
  def win(self):
    if np.any(self.players[0]["field"] == self.num_cards) or np.all(self.players[0]["field"] > 0):
      return 1
    elif np.any(self.players[1]["field"] == self.num_cards) or np.all(self.players[1]["field"] > 0):
      return 2
    return None

  # Move a card from one place to the other
  # ex) self._move_x_to_x(player, "hand", "field", lv.FIRE) will move FIRE element in player's hand to the player's field
  def _move_x_to_x(self, player, start, dest, element):
      if self.players[player][start][element] > 0:
        self.players[player][start][element] -= 1
        self.players[player][dest][element] += 1
      else:
        print(f"Player_{player} doesn't have {lv.ELEMENTS[element]} at {start}")

  def __repr__(self):
    return "board: " + str(self._get_board())
  
