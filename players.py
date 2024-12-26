import numpy as np
import lands_vars as lv

class BasePlayer():
  # Initialize hand, discard and deck
  def __init__(self, num_elements=5, num_cards=5, start_hand=5):
    # Meta variables
    self.num_elements = num_elements
    self.num_cards = num_cards
    self.start_hand = start_hand

    # Game states
    self.hand = np.zeros(num_elements, dtype=np.int64)
    self.discard = np.zeros(self.num_elements, dtype=np.int64)
    self._init_deck()
    self.draw_n(self.start_hand)

  # Shuffle the deck
  def _shuffle_deck(self):
    np.random.shuffle(self.deck)

  # Initialize deck
  def _init_deck(self):
    self.deck = np.array([(i)//(self.num_cards) + 1 for i in range(self.num_elements*self.num_cards)])
    self._shuffle_deck()

  # Add all cards in discard pile to the deck and shuffle
  def putDiscardToDeck(self):
    self.deck.append(np.array([[n+1]*i for n, i in enumerate(self.discard)]).reshape(-1))
    self.discard.fill(0)
    self._shuffle_deck()

  # Draw one card from the deck to the hand
  def draw_n(self, n=1):
    if len(self.deck) < 1:
      self.putDiscardToDeck()
      assert len(self.deck) > 0    # We want deck to contain at least 1 card
    for i in range(n):
      self.hand[self.deck[i]-1] += 1
    self.deck = self.deck[n:]

  def resetStates(self):
    self.hand.fill(0)
    self.discard.fill(0)
    self._init_deck()
    self.draw_n(self.start_hand)

  # TODO:
  def play(self, element):
    # Validate input
    assert element <= self.num_elements and element > 0

    # remove from hand

    # put it to discard

    # Have game logic on board?
    # match element:
    #   case lv.GRASS:
    #     pass
    #   case lv.YELLOW:
    #     pass
    #   case lv.FIRE:
    #     pass
    #   cass lv.

# TODO: Define diff object between human/agents