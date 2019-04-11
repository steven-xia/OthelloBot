import board
import engine

cdef int MOBILITY_FACTOR = 3
cdef int FRONTIER_FACTOR = 7

SCORE_TABLE = (
    99, -8, 8, 6, 6, 8, -8, 99,
    -8, -24, -4, -3, -3, -4, -24, -8,
    8, -4, 7, 4, 4, 7, -4, 8,
    6, -3, 4, 0, 0, 4, -3, 6,
    6, -3, 4, 0, 0, 4, -3, 6,
    8, -4, 7, 4, 4, 7, -4, 8,
    -8, -24, -4, -3, -3, -4, -24, -8,
    99, -8, 8, 6, 6, 8, -8, 99,
)


SQUARE1 = (
    1, 0, 0, 0, 0, 0, 0, 1,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    1, 0, 0, 0, 0, 0, 0, 1,
)

SQUARE2 = (
    0, 1, 0, 0, 0, 0, 1, 0,
    1, 0, 0, 0, 0, 0, 0, 1,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    1, 0, 0, 0, 0, 0, 0, 1,
    0, 1, 0, 0, 0, 0, 1, 0,
)

SQUARE3 = (
    0, 0, 1, 0, 0, 1, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    1, 0, 0, 0, 0, 0, 0, 1,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    1, 0, 0, 0, 0, 0, 0, 1,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 1, 0, 0, 1, 0, 0,
)

SQUARE4 = (
    0, 0, 0, 1, 1, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    1, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 1,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 1, 1, 0, 0, 0,
)

SQUARE5 = (
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 1, 0, 0, 0, 0, 1, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 1, 0, 0, 0, 0, 1, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
)

SQUARE6 = (
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 1, 0, 0, 1, 0, 0,
    0, 1, 0, 0, 0, 0, 1, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 1, 0, 0, 0, 0, 1, 0,
    0, 0, 1, 0, 0, 1, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
)

SQUARE7 = (
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 1, 1, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 1, 0, 0, 0, 0, 1, 0,
    0, 1, 0, 0, 0, 0, 1, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 1, 1, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
)

SQUARE8 = (
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 1, 0, 0, 1, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 1, 0, 0, 1, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
)

SQUARE9 = (
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 1, 1, 0, 0, 0,
    0, 0, 1, 0, 0, 1, 0, 0,
    0, 0, 1, 0, 0, 1, 0, 0,
    0, 0, 0, 1, 1, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
)

SQUARE10 = (
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 1, 1, 0, 0, 0,
    0, 0, 0, 1, 1, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
)

SCORE_TUPLE = (
    (board.bitboard(SQUARE1),  99),
    (board.bitboard(SQUARE2),  -8),
    (board.bitboard(SQUARE3),   8),
    (board.bitboard(SQUARE4),   6),
    (board.bitboard(SQUARE5), -24),
    (board.bitboard(SQUARE6),  -4),
    (board.bitboard(SQUARE7),  -3),
    (board.bitboard(SQUARE8),   7),
    (board.bitboard(SQUARE9),   4),
    (board.bitboard(SQUARE10),  0)
)


PIECE_VALUE_DICTIONARY = {board.BOARD_ARRAY_SIZE - num_pieces:
                              max(0, -(1 / ((2 * num_pieces / board.BOARD_ARRAY_SIZE) - 2.5)) - 1)
                          for num_pieces in range(board.BOARD_ARRAY_SIZE + 1)}


def get_frontier_score(black_bitboard, white_bitboard):
    pieces = black_bitboard | white_bitboard

    cool_thing = ((pieces >> board.BOARD_SIZE) | ~board.BOTTOM_EDGE) & \
                 ((pieces << board.BOARD_SIZE) | ~board.TOP_EDGE) & \
                 ((pieces >> 1) | ~board.RIGHT_EDGE) & \
                 ((pieces << 1) | ~board.LEFT_EDGE) & \
                 ((pieces >> board.DIAGONAL_MORE) | ~board.BOTTOM_RIGHT_EDGE) & \
                 ((pieces >> board.DIAGONAL_LESS) | ~board.BOTTOM_LEFT_EDGE) & \
                 ((pieces << board.DIAGONAL_MORE) | ~board.TOP_LEFT_EDGE) & \
                 ((pieces << board.DIAGONAL_LESS) | ~board.TOP_RIGHT_EDGE)

    cdef unsigned long long black_interior = black_bitboard & cool_thing
    cdef unsigned long long white_interior = white_bitboard & cool_thing

    cdef unsigned long long black_frontier = black_interior ^ black_bitboard
    cdef unsigned long long white_frontier = white_interior ^ white_bitboard

    return board.popcount(white_frontier) - board.popcount(black_frontier)


def evaluate(board_object):
    cdef int black_score, white_score
    black_score, white_score = board_object.score()

    # if the game is over
    if board_object.is_game_over():
        if black_score > white_score:
            return engine.INFINITY - white_score - 1
        elif black_score < white_score:
            return -engine.INFINITY + black_score + 1
        else:
            return 0

    # get the piece scores
    cdef unsigned long long bitboard
    cdef int score
    cdef int piece_score = 0
    for bitboard, score in SCORE_TUPLE:
        piece_score += score * board.popcount(board_object.bitboard_black & bitboard)
        piece_score -= score * board.popcount(board_object.bitboard_white & bitboard)

    cdef int absolute_piece_factor = PIECE_VALUE_DICTIONARY[board_object.empty_spaces()]
    piece_score += absolute_piece_factor * 100 * board.popcount(board_object.bitboard_black)
    piece_score -= absolute_piece_factor * 100 * board.popcount(board_object.bitboard_white)

    # get the mobility score
    cdef int mobility_score = len(board_object.legal_moves()) - len(board_object.legal_moves(opponent=True))

    # get frontier score
    cdef int frontier_score = get_frontier_score(board_object.bitboard_black, board_object.bitboard_white)

    return int(piece_score + MOBILITY_FACTOR * mobility_score + FRONTIER_FACTOR * frontier_score)
