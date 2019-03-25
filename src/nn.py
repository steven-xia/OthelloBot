import math

import numpy
import tensorflow

import board
import engine


def shifted_leaky_relu(x):
    x = tensorflow.keras.backend.maximum(0.5 * x, x)
    x = tensorflow.keras.backend.maximum(-tensorflow.keras.backend.ones_like(x), x)
    return x


network = tensorflow.keras.models.load_model("network.h5", custom_objects={"shifted_leaky_relu": shifted_leaky_relu})


def preprocess_board_object(board_object):
    black_board = board.board_array(board_object.bitboard_black)
    white_board = board.board_array(board_object.bitboard_white)

    board_input = [[] for _ in range(board.BOARD_SIZE)]
    for index, black in enumerate(black_board):
        board_input[index // 8].append((black, white_board[index]))

    if board_object.side == board.BLACK:
        extra_input = (1, 0)
    else:
        extra_input = (0, 1)

    return numpy.array([board_input]), numpy.array([extra_input])


def inverse_tanh(x):
    return (1 / 2) * math.log((x + 1) / (1 - x))


def evaluate(board_object):
    black_score, white_score = board_object.score()

    # if the game is over
    if board_object.is_game_over():
        if black_score > white_score:
            return engine.INFINITY - (board.BOARD_ARRAY_SIZE - white_score)
        elif black_score < white_score:
            return -engine.INFINITY + (board.BOARD_ARRAY_SIZE - black_score)
        else:
            return 0

    inputs = preprocess_board_object(board_object)
    output = network.predict(inputs)[0][0]

    return int(100 * inverse_tanh(output))
