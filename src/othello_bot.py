import time

import evaluator
import engine
import board


try:
    # from matplotlib import pyplot as pylab

    GRAPH = False
except ImportError:
    GRAPH = False

SELF_PLAY = False

current_limit = 64

DIFFICULTY = int(input("Enter difficulty (1 - 10): ")) ** 2 / 10
print(f"Time per move set at {round(DIFFICULTY, 2)} seconds.")
# DIFFICULTY = 2

b = board.Board()
bot = engine.Engine(b, evaluator.evaluate)

turn = 0
evaluations = []
while not b.is_game_over():
    print(b)
    print("Legal moves:", tuple(map(lambda bb: engine.BITBOARD_TO_COORD[bb], b.legal_moves())))
    print("Game over:", b.is_game_over())
    print("Score:", b.score())

    if turn % 2 == 1:
        depth = 1
        t = 0
        start_time = time.time()

        pv, value = bot.best_move(depth)
        move = pv[0]
        pv = " ".join(tuple(map(lambda m: engine.BITBOARD_TO_COORD[m], pv)))

        while t < DIFFICULTY and len(b.legal_moves()) > 1 and depth <= 2 * b.empty_spaces():
            pv, value = bot.best_move(depth)

            move = pv[0]
            pv = " ".join(tuple(map(lambda m: engine.BITBOARD_TO_COORD[m], pv)))

            print(f"info depth {depth} " +
                  f"time {int(1000 * (time.time() - start_time))} " +
                  f"nodes {bot.searched_nodes} " +
                  f"nps {int(bot.searched_nodes / (max(0.1, t)))} score {value} " +
                  f"pv {pv}")

            depth += 1
            t = time.time() - start_time

        print(f"bestmove {engine.BITBOARD_TO_COORD[move]}")
        print("Evaluation:", value)

        if GRAPH:
            value = max(-640, min(640, value))
            evaluations.append(value)
            current_limit = max(abs(value), current_limit)
            pylab.plot(evaluations, color="blue", marker="o")
            x_minimum, x_maximum, y_minimum, y_maximum = pylab.axis()
            pylab.axis((0, max(10, len(evaluations)), 1.1 * -current_limit, 1.1 * current_limit))
            pylab.plot([0] * (max(10, len(evaluations)) + 1), color="black", linestyle="dashed", linewidth=0.5)
            pylab.pause(0.01)

    else:
        try:

            if SELF_PLAY:
                import random
                move = random.choice(b.legal_moves())
            else:
                move = engine.COORD_TO_BITBOARD[input(">>> ").strip().upper()]
        except KeyError:
            move = ""

        while move not in b.legal_moves():
            try:
                move = engine.COORD_TO_BITBOARD[input(">>> ").strip().upper()]
            except KeyError:
                move = ""
    b.move(move)

    evaluator.get_frontier_score(b.bitboard_black, b.bitboard_white)

    turn += 1

print()
print(b)
print("Legal moves:", b.legal_moves())
print("Game over:", b.is_game_over())
print("Score:", b.score())

if GRAPH:
    pylab.show()
