import lands_vars as lv
import lands_game_copy as lg
import random


game = lg.LandsGame()

print(game)

print(game.possible_actions)

possible_moves = game.possible_actions

# choose random possible move
random_move = random.choice(possible_moves)
def legal_moves(possible_actions):
    action_mask = [[0]*4, [0]*5, [0]*2, [0]*55, [0]*5]
    for action in possible_actions:
        action_choice = action[0]
        action_data = action[action_choice]

        action_mask[0][action_choice] = 1
        action_mask[action_choice][action_data] = 1

    return action_mask
while True:
    # print(legal_moves(possible_moves))
    possible_moves, turn, sub_turn = game.play_move(random_move)
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

