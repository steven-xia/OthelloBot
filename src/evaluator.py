import engine
import board

MOBILITY_FACTOR = 3
FRONTIER_FACTOR = 7

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

    black_interior = black_bitboard & cool_thing
    white_interior = white_bitboard & cool_thing

    black_frontier = black_interior ^ black_bitboard
    white_frontier = white_interior ^ white_bitboard

    return board.popcount(white_frontier) - board.popcount(black_frontier)


def evaluate(board_object):
    black_score, white_score = board_object.score()

    # if the game is over
    if board_object.is_game_over():
        if black_score > white_score:
            return engine.INFINITY - (board.BOARD_ARRAY_SIZE - white_score)
        elif black_score < white_score:
            return -engine.INFINITY - (board.BOARD_ARRAY_SIZE - black_score)
        else:
            return 0

    # get the piece scores
    black_board_array = board.board_array(board_object.bitboard_black)
    white_board_array = board.board_array(board_object.bitboard_white)

    piece_score = sum(x * SCORE_TABLE[i] for i, x in enumerate(black_board_array)) - \
                  sum(x * SCORE_TABLE[i] for i, x in enumerate(white_board_array))

    # get the mobility score
    mobility_score = len(board_object.legal_moves()) - len(board_object.legal_moves(opponent=True))

    # get frontier score
    frontier_score = get_frontier_score(board_object.bitboard_black, board_object.bitboard_white)

    return piece_score + MOBILITY_FACTOR * mobility_score + FRONTIER_FACTOR * frontier_score
