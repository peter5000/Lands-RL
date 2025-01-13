import numpy as np
import lands_vars as lv

class LandsGame():
  def __init__(self, num_elements=lv.NUM_ELEMENTS, num_cards=lv.NUM_CARDS, start_hand=lv.START_HAND, player_count = lv.PLAYER_COUNT):
    # Game meta variables initialization
    self.num_elements = num_elements
    self.num_cards = num_cards
    self.start_hand = start_hand
    self.player_count = player_count
    self.gameover = False
    # 0 = player1, 1 = player2
    self.turn = 0

    # Game variables initialization
    # self.field = np.zeros((2, lv.NUM_ELEMENTS))       # p1 = first row, p2 = second row
    self.players = [{"field": np.zeros(self.num_elements, dtype=np.int8), "hand": np.zeros((self.num_elements), dtype=np.int8), "discard": np.zeros((self.num_elements), dtype=np.int8), "deck": None} for i in range(self.player_count)]
    for i in range(self.player_count):
      self._init_deck(i)
      self.draw_n(i, self.start_hand)

    # self.p1 = {"field": np.zeros(lv.NUM_ELEMENTS), "hand": np.zeros((lv.NUM_ELEMENTS)), "discard": np.zeros((lv.NUM_ELEMENTS)), "deck": None}
    # self.p2 = {"field": np.zeros(lv.NUM_ELEMENTS), "hand": np.zeros((lv.NUM_ELEMENTS)), "discard": np.zeros((lv.NUM_ELEMENTS)), "deck": None}
    # self._init_deck(self.p1)
    # self._init_deck(self.p2)
    # self._draw_n(self.p1, self.start_hand)
    # self._draw_n(self.p2, self.start_hand)

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
    self.players[player]["deck"] = np.append(self.players[player]["deck"], np.concatenate([[n+1]*i for n, i in enumerate(self.players[player]["discard"])]).reshape(-1))
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

  # Given an action (tuple), first element is a card played, second element is a card chosen (if appropriate)
  def validate_move(self, action, player):
    # Assert action in bound of elements range and action card in player's hand
    if (action[0] > self.num_elements or action[0] < lv.GRASS or action[1] > self.num_elements or action[1] < lv.GRASS) or self.players[player]["hand"][action[0]-1] <= 0:
      return False

    match action:
      case lv.GRASS, target:
        return True if self.players[player]["discard"][target-1] > 0 else False
      case lv.YELLOW, target:
        return True
      case lv.FIRE, target:
        return True if self.players[1-player]["field"][target-1] > 0 else False
      case lv.DARK, target:
        return True
      case lv.WATER, target:
        return True
      case _:
        return False

  # Given a player (0 for player1 and 1 for player2), return list of valid actions(tuple)
  def valid_moves(self, player):
    moves = []
    for i in range(1,self.num_elements+1):
      if self.players[player]["hand"][i-1] > 0:
        match i:
          case lv.GRASS:
            valid_moves = [(lv.GRASS, j+1) for j in range(self.num_elements) if self.players[player]["discard"][j] > 0]
          case lv.YELLOW:
            valid_moves = [(lv.YELLOW, j) for j in range(1, self.num_elements+1)]
          case lv.FIRE:
            valid_moves = [(lv.FIRE, j+1) for j in range(self.num_cards) if self.players[1-player]["field"][j] > 0]
          case lv.DARK:
            valid_moves = [(lv.DARK, j) for j in range(1, self.num_elements+1)]
          case lv.WATER:
            valid_moves = [(lv.WATER, j) for j in range(1, self.num_elements+1)]
        moves.extend(valid_moves)
    return moves

  # check for a win con and return a player number of the winner else none
  def win(self):
    if np.any(self.players[0]["field"] == self.num_cards) or np.all(self.players[0]["field"] > 0):
      return 1
    elif np.any(self.players[1]["field"] == self.num_cards) or np.all(self.players[1]["field"] > 0):
      return 2
    return None

  # plays a card and change the state of the game accordingly
  # action must be a tuple of integers
  def play_card(self, action):
    if self.gameover:
      print("Please restart the game!")
      return self._get_board()

    curr_player = self.turn
    if self.validate_move(action, curr_player):
      match action:
        case lv.GRASS, target:
          if self.players[curr_player]["discard"][target-1] > 0:
            self._move_x_to_x(curr_player, "discard", "hand", action[1])
          else:
            print("INVALID MOVE")
            self.gameover = True
            return self._get_board()
        case lv.YELLOW, target:
          self.draw_n(curr_player)
        case lv.FIRE, target:
          if self.players[1-curr_player]["field"][target-1] > 0:
            self._move_x_to_x(1-curr_player, "field", "discard", target)
          else:
            print("INVALID MOVE")
            self.gameover = True
            return self._get_board()
        # TODO Make it selectable
        case lv.DARK, target:
          num_cards = np.sum(self.players[1-curr_player]["hand"])
          if num_cards > 0:
            idx = np.random.randint(num_cards)
            total = 0
            for i in range(self.num_elements):
              total += self.players[1-curr_player]["hand"][i]
              if total > idx:
                element = i + 1
                break
            self._move_x_to_x(1-curr_player, "hand", "discard", element)
        # TODO implement
        case lv.WATER, target:
          pass
        case _: # invalid move
          print("INVALID MOVE!!")
          self.gameover = True
    else:
      self.gameover = True

    # If game has not ended by invalid move, play the card to the field
    if not self.gameover:
      self._move_x_to_x(curr_player, "hand", "field", action[0])
      self.turn = 1-curr_player
      # player["hand"][action[0]-1] -= 1
      # player["field"][action[0]-1] += 1

    # Check for a win
    win = self.win()
    if win is not None:
      print(f"Player {win} won!")

    return self._get_board()  # Return board for a debugging purpose

  # Move a card from one place to the other
  # ex) self._move_x_to_x(player, "hand", "field", lv.FIRE) will move FIRE element in player's hand to the player's field
  def _move_x_to_x(self, player, start, dest, element):
      if self.players[player][start][element-1] > 0:
        self.players[player][start][element-1] -= 1
        self.players[player][dest][element-1] += 1
      else:
        print(f"Player {player+1} doesn't have {lv.ELEMENTS[element-1]} at {start}")

  def __repr__(self):
    return "board: " + str(self._get_board())