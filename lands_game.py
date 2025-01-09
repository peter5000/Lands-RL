import numpy as np
import lands_vars as lv

class LandsGame():
  def __init__(self, num_elements=5, num_cards=5, start_hand=5):
    # Game meta variables
    self.num_elements = num_elements
    self.num_cards = num_cards
    self.start_hand = start_hand

    # Game variables
    self.field = np.zeros((2, lv.NUM_ELEMENTS))       # p1 = first row, p2 = second row
    self.p1_hand = np.zeros((1, lv.NUM_ELEMENTS))
    self.p2_hand = np.zeros((1, lv.NUM_ELEMENTS))
    self.p1_discard = np.zeros((1, lv.NUM_ELEMENTS))
    self.p2_discard = np.zeros((1, lv.NUM_ELEMENTS))
    self.p1_deck = self._init_deck()
    self.p2_deck = self._init_deck()

  # Shuffle the deck
  def _shuffle_deck(self, deck):
    return np.random.permutation(deck)

  # Initialize deck
  def _init_deck(self):
    deck = np.array([(i)//(self.num_cards) + 1 for i in range(self.num_elements*self.num_cards)])
    return self._shuffle_deck(deck)

  # Add all cards in discard pile to the deck and shuffle
  # return (new_deck, new_discard)
  def putDiscardToDeck(self, discard, deck):
    deck.append(np.array([[n+1]*i for n, i in enumerate(discard)]).reshape(-1))
    discard.fill(0)
    return (self._shuffle_deck(deck), discard)

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

  def __repr__(self):
    pass