import numpy as np
import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)
import lands_vars as lv
import lands_game as lg

game = lg.LandsGame()

# print the board state
# row 1: player 1's hand,
# row 2: player 1's field
# row 3: player 2's field
# row 4: player 2's hand,
print(game)

# -------------------------------------------------------
# Initialize game with correct deck and hand sizes
# -------------------------------------------------------
print(game.players)
assert len(game.players[0]["deck"]) == lv.NUM_CARDS * lv.NUM_ELEMENTS - lv.START_HAND
assert len(game.players[1]["deck"]) == lv.NUM_CARDS * lv.NUM_ELEMENTS - lv.START_HAND
assert np.sum(game.players[0]["hand"]) == 5
assert np.sum(game.players[1]["hand"]) == 5

# -------------------------------------------------------
# Drawing from the deck
# -------------------------------------------------------

# Base case
print("----------------------------------")
game.draw_n(0)
print(game.players)
assert len(game.players[0]["deck"]) == lv.NUM_CARDS * lv.NUM_ELEMENTS - lv.START_HAND - 1
assert len(game.players[1]["deck"]) == lv.NUM_CARDS * lv.NUM_ELEMENTS - lv.START_HAND
assert np.sum(game.players[0]["hand"]) == 6
assert np.sum(game.players[1]["hand"]) == 5

# Draw when there are no cards in the deck
print("----------------------------------")
game.players[0]["deck"] = np.array([], dtype=np.int8)
game.players[0]["discard"][0] = 5 - game.players[0]["hand"][0]
game.players[0]["discard"][1] = 5 - game.players[0]["hand"][1]
game.players[0]["discard"][2] = 5 - game.players[0]["hand"][2]
game.players[0]["discard"][3] = 5 - game.players[0]["hand"][3]
game.players[0]["discard"][4] = 5 - game.players[0]["hand"][4]
print("before drawing")
print(game.players[0])
game.draw_n(0)
print("after drawing")
print(game.players[0])

# -------------------------------------------------------
# reset_states correctly reset discard, hand and deck
# -------------------------------------------------------
print("----------------------------------")

game._reset_states(0)
game._reset_states(1)
print(game.players)
assert len(game.players[0]["deck"]) == lv.NUM_CARDS * lv.NUM_ELEMENTS - lv.START_HAND
assert len(game.players[1]["deck"]) == lv.NUM_CARDS * lv.NUM_ELEMENTS - lv.START_HAND
assert np.sum(game.players[0]["hand"]) == 5
assert np.sum(game.players[1]["hand"]) == 5

# -------------------------------------------------------
# reset_game correctly reset fields
# -------------------------------------------------------

print("----------------------------------")

game.players[0]["field"][0] += 1
game.players[1]["field"][0] += 1

game.reset_game()
print(game.players)
assert len(game.players[0]["deck"]) == lv.NUM_CARDS * lv.NUM_ELEMENTS - lv.START_HAND
assert len(game.players[1]["deck"]) == lv.NUM_CARDS * lv.NUM_ELEMENTS - lv.START_HAND
assert np.sum(game.players[0]["hand"]) == 5
assert np.sum(game.players[1]["hand"]) == 5

# -------------------------------------------------------
# Validate moves
# -------------------------------------------------------

print("----------------------------------")

print(game._get_board())

game.players[0]["hand"][lv.GRASS-1] += 1
game.players[0]["hand"][lv.FIRE-1] += 1
game.players[0]["discard"][lv.FIRE-1] += 1
game.players[1]["field"][lv.FIRE-1] += 1
print(game.players)

assert not (game.validate_move((lv.GRASS,lv.GRASS), 0))
assert (game.validate_move((lv.GRASS,lv.FIRE), 0))
assert not (game.validate_move((lv.GRASS,lv.WATER), 0))
assert not (game.validate_move((lv.FIRE,lv.GRASS), 0))
assert (game.validate_move((lv.FIRE,lv.FIRE), 0))
assert not (game.validate_move((lv.FIRE,lv.WATER), 0))

print("----------------------------------")
# Validate valid move generator
game.reset_game()
for i in range(game.num_elements):
  game.players[0]["discard"][i] += np.random.randint(2)
  game.players[1]["discard"][i] += np.random.randint(2)
  game.players[0]["field"][i] += np.random.randint(2)
  game.players[1]["field"][i] += np.random.randint(2)
print(game.players)
p1_moves = game.valid_moves(0)
p2_moves = game.valid_moves(1)
print(p1_moves)
print(p2_moves)

for i in range(len(p1_moves)):
  assert game.validate_move(p1_moves[i], 0)

for i in range(len(p2_moves)):
  assert game.validate_move(p2_moves[i], 1)

# -------------------------------------------------------
# Play moves
# -------------------------------------------------------

print("----------------------------------")

print("before playing valid grass")
print(game.players)
print(game.gameover)
game.play_card((lv.GRASS,lv.FIRE))
print("after playing valid grass")
print(game.players)
print(game.gameover)

print("----------------------------------")

game.reset_game()
game.players[0]["hand"][lv.GRASS-1] += 1
print("before play invalid grass")
print(game.players)
print(game.gameover)
game.play_card((lv.GRASS,lv.GRASS))
print("after play invalid grass")
print(game.players)
print(game.gameover)

print("----------------------------------")

game.reset_game()
game.players[0]["hand"][lv.YELLOW-1] += 1
print("before play valid yellow")
print(game.players)
print(game.gameover)
game.play_card((lv.YELLOW,lv.GRASS))
print("after play valid yellow")
print(game.players)
print(game.gameover)

print("----------------------------------")

game.reset_game()
game.players[0]["hand"][lv.FIRE-1] += 1
game.players[1]["field"][lv.FIRE-1] += 1
print("before play valid fire")
print(game.players)
print(game.gameover)
game.play_card((lv.FIRE,lv.FIRE))
print("after play valid fire")
print(game.players)
print(game.gameover)

print("----------------------------------")

game.reset_game()
game.players[0]["hand"][lv.FIRE-1] += 1
print("before play invalid fire")
print(game.players)
print(game.gameover)
game.play_card((lv.FIRE,lv.GRASS))
print("after play invalid fire")
print(game.players)
print(game.gameover)

print("----------------------------------")

# dark when the opponent has 1 or more cards in their hand
game.reset_game()
game.players[0]["hand"][lv.DARK-1] += 1
print("before play valid dark")
print(game.players)
print(game.gameover)
game.play_card((lv.DARK,lv.GRASS))
print("after play valid dark")
print(game.players)
print(game.gameover)

print("----------------------------------")

# dark when the opponent has no cards in their hand
game.reset_game()
game.players[0]["hand"][lv.DARK-1] += 1
game.players[1]["hand"].fill(0)
print("before play valid dark")
print(game.players)
print(game.gameover)
game.play_card((lv.DARK,lv.GRASS))
print("after play valid dark")
print(game.players)
print(game.gameover)

print("----------------------------------")

# Do nothing for now
game.reset_game()
game.players[0]["hand"][lv.WATER-1] += 1
print("before play valid water")
print(game.players)
print(game.gameover)
game.play_card((lv.WATER,lv.GRASS))
print("after play valid water")
print(game.players)
print(game.gameover)

print("----------------------------------")

game.reset_game()
for j in range(lv.PLAYER_COUNT):
  for i in range(lv.NUM_ELEMENTS):
    game.players[j]["field"][i] = 5
    assert game.win() == j + 1
    game._reset_states(j)
    # print(game.players)

  for i in range(lv.NUM_ELEMENTS):
    game.players[j]["field"][i] = 1
  assert game.win() == j + 1
  game._reset_states(j)

