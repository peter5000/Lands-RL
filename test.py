import lands_vars as lv
import lands_game as lg
import random

game = lg.LandsGame()

print(game)

print(game.possible_actions)

possible_moves = game.possible_actions
# choose random possible move
random_move = random.choice(possible_moves)

while True:
    possible_moves, turn, sub_turn = game.play_move(lg.parse_action_data(random_move))
    if not possible_moves or game.gameover:
        print(game)
        break
    print(f"Random Move: {random_move}")
    print(f"Turn: {turn}, Sub-turn: {sub_turn}")
    print("Possible Moves:")
    for move in possible_moves:
        print(move)
    print("Current Game State:")
    print(game)
    

    print("--------------------")
    random_move = random.choice(possible_moves)
    input("Press Enter to continue...")
    print("--------------------")
    