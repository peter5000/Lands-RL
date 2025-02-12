import numpy as np
import lands_vars as lv
from itertools import combinations_with_replacement

def parse_action_data(action_tuple):
  action_type, action_data = action_tuple
  res = {
    "action": action_type,
    "play_card": None,
    "counter": None,
    "reveal": None,
    "resolve_card": None
  }
  res[action_type] = action_data
  return res

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
    self.revealed_cards = np.zeros((1, lv.NUM_ELEMENTS)) 

    # cards played over course of turn
    self.playing = []

    self.countered = False

    self.scryed_card = None

    self.possible_actions = self.cards_to_play_choices(self.turn)



  def play_move(self, action_data):
    action = action_data["action"]
    action_data = action_data[action]

    # needs to manage state of the game
    match action:
      case "play_card":
        # action_data will be the card played

        self.playing = [action_data]
        # update subturn to the player who has a chance to counter
        self.pass_sub_turn()
        # opponent has a chance to counter
        self.possible_actions = self.counter_choices(self.sub_turn)
      
      case "counter":
        # action_data will be 0 or 1

        if action_data == 1:
          self.counter(self.sub_turn)
          # other player has a chance to counter
          self.pass_sub_turn()
          self.possible_actions = self.counter_choices(self.sub_turn)

        else:
          # if it is the same player's turn and self.countered is true, then the counter went through
          # and it becomes the next player's turn
          if self.turn == self.sub_turn and self.countered:
            self._move_x_to_x(self.turn, "hand", "discard", self.playing[0])
            self.pass_turn()
            
          # if it is the same player's turn and self.countered is false, then the card goes through
          else:
            self.resolve_card_init()
          
      case "reveal":
        # action_data will be a list of 5 integers representing the number of each card to reveal

        # TODO verify moves
        self.revealed_cards = action_data
        # update subturn to the player who has to pick
        self.sub_turn = self.turn
        # player must pick from revealed cards
        self.possible_actions = self.pick_from_revealed_choices(self.turn)

      case "resolve_card":
        # action_data will be the card to resolve

        self.resolve_card_final(action_data)
    return (self.possible_actions, self.turn, self.sub_turn)

        


  def resolve_card_init(self):
    self.sub_turn = self.turn
    self._move_x_to_x(self.turn, "hand", "field", self.playing[0])

    # resolve the card
    match self.playing[0]:
      case lv.GRASS:
        if np.any(self.players[self.turn]["discard"] > 0):
          self.possible_actions = self.green_choices(self.turn)
        else:
          self.pass_turn()
      case lv.YELLOW:
        self.draw_n(self.turn, n=1)
        self.pass_turn()
      case lv.FIRE:
        if np.any(self.players[1-self.turn]["field"] > 0):
          self.possible_actions = self.fire_choices(self.turn)
        else:
          self.pass_turn()
      case lv.DARK:
        if np.any(self.players[1-self.turn]["hand"] > 0):
          # playing black so opponent has to reveal cards
          self.pass_sub_turn()
          self.possible_actions = self.reveal_card_choices(self.sub_turn)
        else:
          self.pass_turn()
      case lv.WATER:
        # playing water so you scry
        self.possible_actions = self.scry_choices(self.turn)

  def resolve_card_final(self, action_data):
    match self.playing[0]:
      case lv.GRASS:
        self._move_x_to_x(self.turn, "discard", "hand", action_data)
      case lv.FIRE:
        self._move_x_to_x(1-self.turn, "field", "discard", action_data)
      case lv.DARK:
        self._move_x_to_x(1-self.turn, "hand", "discard", action_data)
      case lv.WATER:
        if action_data == 1:
          self.move_top_card_to_bottom(self.turn)
    
    self.pass_turn()

  def pass_turn(self):
    # TODO: check for win condition and endgame

    # check for win condition
    winner = self.win()
    if winner is not None:
      print(f"Player {winner} wins!")
      self.gameover = True
      return
    self.turn = 1 - self.turn
    self.sub_turn = self.turn
    self.playing = []
    self.countered = False
    self.scryed_card = None
    self.revealed_cards = np.zeros((1, lv.NUM_ELEMENTS))
    self.draw_n(self.turn, n=1)
    self.possible_actions = self.cards_to_play_choices(self.turn)

  def pass_sub_turn(self):  
    self.sub_turn = 1 - self.sub_turn

  def cards_to_play_choices(self, player):
    return [("play_card", i) for i in range(self.num_elements) if self.players[player]["hand"][i] > 0]

  def counter_choices(self, player):
    legal_moves = []
    # if the player has a water card and the card the opponent played
    if self.players[player]["hand"][lv.WATER] > 0 and self.players[player]["hand"][self.playing[-1]] > 0:
      legal_moves.append(("counter", 1))
    legal_moves.append(("counter", 0))
    return legal_moves
    
  # counter a card played by the opponent
  def counter(self, player):
    
    # discard the cards used to counter
    self._move_x_to_x(player, "hand", "discard", self.playing[-1])
    self._move_x_to_x(player, "hand", "discard", lv.WATER)

    # add water to playing
    self.playing.append(lv.WATER)

    # if it is the same player's turn, then the counter was countered
    if self.turn == self.sub_turn:
      self.countered = False
    # if it is the opponent's turn, then the counter was successful
    else:
      self.countered = True

  # playing water and you scry
  def scry_choices(self, player):
    if len(self.players[player]["deck"]) < 1:
      self._put_discard_to_deck(player)
      assert len(self.players[player]["deck"]) > 0    # We want deck to contain at least 1 card
    self.scryed_card = self.players[player]["deck"][0]

    return [("resolve_card", i) for i in range(2)]


  # opponent is playing black and you have to reveal 3 cards
  def reveal_card_choices(self, player):
    legal_moves = []
   
    hand_counts = [int(self.players[player]["hand"][i]) for i in range(5)]
    max_reveal = min(3, sum(hand_counts))

    for comb in combinations_with_replacement(range(5), max_reveal):
      reveal = [0] * 5
      for idx in comb:
        if reveal[idx] < hand_counts[idx]:
          reveal[idx] += 1
      if sum(reveal) == max_reveal:
        legal_moves.append(("reveal", reveal.copy()))
    return legal_moves

  # playing dark and you have to pick a card to move from discard to hand
  def pick_from_revealed_choices(self, player):

    # return a list of the cards that can be picked
    return [
      ("resolve_card", i) for i in range(self.num_elements)
        if self.revealed_cards[i] > 0
      ]

  # playing grass and you have to choose a card to move from discard to hand
  def green_choices(self, player):
    return [
      ("resolve_card", i) for i in range(self.num_elements)
        if self.players[player]["discard"][i] > 0
      ]

  # playing fire and you have to choose a card to move from opponent's field to discard
  def fire_choices(self, player):
    return [("resolve_card", i) for i in range(self.num_elements)
        if self.players[1-player]["field"][i] > 0
      ]
  
  # move the top card to the bottom of the deck
  def move_top_card_to_bottom(self, player):
    self.players[player]["deck"] = np.append(self.players[player]["deck"], self.players[player]["deck"][0])
    self.players[player]["deck"] = self.players[player]["deck"][1:]

  # Shuffle the deck
  def _shuffle_deck(self, player):
    np.random.shuffle(self.players[player]["deck"])

  # Initialize deck
  def _init_deck(self, player):
    self.players[player]["deck"] = np.array([i//(self.num_cards) + 1 for i in range(self.num_elements*self.num_cards)], dtype=np.int8)
    self._shuffle_deck(player)

  # Add all cards in discard pile to the deck and shuffle
  # return (new_deck, new_discard)
  def _put_discard_to_deck(self, player):
    discard_cards = []
    for n, i in enumerate(self.players[player]["discard"]):
      discard_cards.extend([n+1] * int(i))
    self.players[player]["deck"] = np.append(self.players[player]["deck"], discard_cards)
    self.players[player]["discard"].fill(0)
    self._shuffle_deck(player)

  # Draw n cards from the deck to the hand
  def draw_n(self, player, n=1):
    if len(self.players[player]["deck"]) < 1:
      self._put_discard_to_deck(player)
      assert len(self.players[player]["deck"]) > 0    # We want deck to contain at least 1 card
    for i in range(n):
      self.players[player]["hand"][self.players[player]["deck"][i]-1] += 1
    self.players[player]["deck"] = self.players[player]["deck"][n:]

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
    self.gameover = False
    # self._reset_states(self.p1)
    # self._reset_states(self.p2)

  # Retrieve the board in a format:
  # row 1: player 1's hand,
  # row 2: player 1's field
  # row 3: player 2's field
  # row 4: player 2's hand,
  def _get_board(self):

    return np.stack((self.players[0]["hand"], self.players[0]["field"], self.players[1]["field"], self.players[1]["hand"]))

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
        print(f"Player {player+1} doesn't have {lv.ELEMENTS[element]} at {start}")

  def __repr__(self):
    return "board: " + str(self._get_board())
  
