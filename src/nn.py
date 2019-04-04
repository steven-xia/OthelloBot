import os
import math

import numpy
import tensorflow

import board
import engine


def compile_model_for_tpu(model):
    import pprint

    if 'COLAB_TPU_ADDR' not in os.environ:
        print('ERROR: Not connected to a TPU runtime!')
        return False
    else:
        tpu_address = 'grpc://' + os.environ['COLAB_TPU_ADDR']
        print('TPU address is', tpu_address)

        with tensorflow.Session(tpu_address) as session:
            devices = session.list_devices()

        print('TPU devices:')
        pprint.pprint(devices)

        tpu_address = 'grpc://' + os.environ['COLAB_TPU_ADDR']
        tensorflow.logging.set_verbosity(tensorflow.logging.INFO)

        model = tensorflow.contrib.tpu.keras_to_tpu_model(
            model,
            strategy=tensorflow.contrib.tpu.TPUDistributionStrategy(
                tensorflow.contrib.cluster_resolver.TPUClusterResolver(tpu_address)))

    return model


NETWORK_LOCATION = os.path.join(os.path.dirname(__file__), "network.h5")
network = tensorflow.keras.models.load_model(NETWORK_LOCATION)
network = compile_model_for_tpu(network)


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


TANH_LIMIT = 1 - 10 ** (-16)


def inverse_tanh(x):
    x = max(-TANH_LIMIT, min(TANH_LIMIT, x))
    return (1 / 2) * math.log((x + 1) / (1 - x))


SQUARED_FACTOR = math.log(64) / math.log(inverse_tanh(TANH_LIMIT)) + 10 ** (-12)


def inverse_tanh_squared(x):
    x = max(-TANH_LIMIT, min(TANH_LIMIT, x))
    return (x / abs(x)) * inverse_tanh(abs(x)) ** SQUARED_FACTOR


def evaluate(board_object):
    black_score, white_score = board_object.score()

    # if the game is over
    if board_object.is_game_over():
        if black_score > white_score:
            return engine.INFINITY - white_score - 1
        elif black_score < white_score:
            return -engine.INFINITY + black_score + 1
        else:
            return 0

    inputs = preprocess_board_object(board_object)
    output = network.predict(inputs)[0][0]

    # return int(100 * inverse_tanh(output))
    return int(100 * inverse_tanh_squared(output))
