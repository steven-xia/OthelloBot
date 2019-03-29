import multiprocessing

import numpy


def to_data_conversion(s):
    if s == "X":
        return 1, 0
    elif s == "O":
        return 0, 1
    else:
        return 0, 0


def preprocess_board(text_representation):
    board = text_representation[:-1]
    turn = text_representation[-1]

    return_board = []
    for character in board:
        return_board.append(to_data_conversion(character))

    return_board = numpy.array(numpy.array(return_board))
    return_board = numpy.resize(return_board, (8, 8, 2))

    turn = numpy.array(to_data_conversion(turn))

    return return_board, turn


def preprocess_game(inputs):
    board, evaluation = inputs

    return preprocess_board(board), float(evaluation)


def preprocess(loaded_dictionary):
    p = multiprocessing.Pool(multiprocessing.cpu_count())
    output = p.map(preprocess_game, loaded_dictionary.items())

    return output


if __name__ == "__main__":
    import datafile_manager

    d = datafile_manager.load_data("training_data.txt")
    t = preprocess(d)
    print(t[0])
