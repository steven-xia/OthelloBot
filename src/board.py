EMPTY = 0
BLACK = 1
WHITE = 2

SIDE_REPRESENTATION = {
    EMPTY: " ",
    BLACK: "#",
    WHITE: "-"
}

BOARD_SIZE = 8
BOARD_ARRAY_SIZE = BOARD_SIZE ** 2

DIAGONAL_LESS = BOARD_SIZE - 1
DIAGONAL_MORE = BOARD_SIZE + 1

NOT_CALCULATED = 10

STARTING_POSITION_ARRAY = (
    EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
    EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
    EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
    EMPTY, EMPTY, EMPTY, WHITE, BLACK, EMPTY, EMPTY, EMPTY,
    EMPTY, EMPTY, EMPTY, BLACK, WHITE, EMPTY, EMPTY, EMPTY,
    EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
    EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
    EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
)


def bitboard(arr):
    return sum(1 << i for i, x in enumerate(arr) if x)


def board_array(bb):
    return tuple((bb >> i) & 1 for i in range(BOARD_ARRAY_SIZE))


def split_bitboard(bb):
    return tuple(1 << i for i in range(BOARD_ARRAY_SIZE) if (bb >> i) & 1)


def popcount(bb):
    count = 0
    while bb:
        count += 1
        bb &= bb - 1
    return count


def display_bitboard(bb):
    s = tuple(map(str, board_array(bb)))
    s = [" ".join(s[i: i + BOARD_SIZE]) for i in range(0, len(s), BOARD_SIZE)]
    print("\n".join(s))


TOP_EDGE_ARRAY = (
    0, 0, 0, 0, 0, 0, 0, 0,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
)

BOTTOM_EDGE_ARRAY = (
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    0, 0, 0, 0, 0, 0, 0, 0,
)

LEFT_EDGE_ARRAY = (
    0, 1, 1, 1, 1, 1, 1, 1,
    0, 1, 1, 1, 1, 1, 1, 1,
    0, 1, 1, 1, 1, 1, 1, 1,
    0, 1, 1, 1, 1, 1, 1, 1,
    0, 1, 1, 1, 1, 1, 1, 1,
    0, 1, 1, 1, 1, 1, 1, 1,
    0, 1, 1, 1, 1, 1, 1, 1,
    0, 1, 1, 1, 1, 1, 1, 1,
)

RIGHT_EDGE_ARRAY = (
    1, 1, 1, 1, 1, 1, 1, 0,
    1, 1, 1, 1, 1, 1, 1, 0,
    1, 1, 1, 1, 1, 1, 1, 0,
    1, 1, 1, 1, 1, 1, 1, 0,
    1, 1, 1, 1, 1, 1, 1, 0,
    1, 1, 1, 1, 1, 1, 1, 0,
    1, 1, 1, 1, 1, 1, 1, 0,
    1, 1, 1, 1, 1, 1, 1, 0,
)

TOP_EDGE = bitboard(TOP_EDGE_ARRAY)
BOTTOM_EDGE = bitboard(BOTTOM_EDGE_ARRAY)
LEFT_EDGE = bitboard(LEFT_EDGE_ARRAY)
RIGHT_EDGE = bitboard(RIGHT_EDGE_ARRAY)

TOP_LEFT_EDGE = TOP_EDGE & LEFT_EDGE
TOP_RIGHT_EDGE = TOP_EDGE & RIGHT_EDGE
BOTTOM_LEFT_EDGE = BOTTOM_EDGE & LEFT_EDGE
BOTTOM_RIGHT_EDGE = BOTTOM_EDGE & RIGHT_EDGE


class Board:
    def __init__(self, position=STARTING_POSITION_ARRAY, side=BLACK):
        self.bitboard_black = bitboard(tuple(x == BLACK for x in position))
        self.bitboard_white = bitboard(tuple(x == WHITE for x in position))
        self.side = side

        self._legal_moves = False
        self._opponent_legal_moves = False
        self._is_game_over = NOT_CALCULATED

        self._past_positions = []

    def legal_moves(self, opponent=False):
        if self._legal_moves and not opponent:
            return self._legal_moves
        elif opponent:
            if self._opponent_legal_moves:
                return self._opponent_legal_moves
            self.null_move()

        if self._is_game_over != NOT_CALCULATED and self._is_game_over:
            return (None,)

        if self.side == BLACK:
            to_move_board = self.bitboard_black
            opponent_board = self.bitboard_white
        else:
            to_move_board = self.bitboard_white
            opponent_board = self.bitboard_black
        empties = ~ (to_move_board | opponent_board)

        moves = 0

        # moving up ...
        temporary_bitboard = (to_move_board >> BOARD_SIZE) & opponent_board
        while temporary_bitboard:
            moves |= (temporary_bitboard >> BOARD_SIZE) & empties & BOTTOM_EDGE
            temporary_bitboard = (temporary_bitboard >> BOARD_SIZE) & opponent_board & BOTTOM_EDGE

        # moving down ...
        temporary_bitboard = (to_move_board << BOARD_SIZE) & opponent_board
        while temporary_bitboard:
            moves |= (temporary_bitboard << BOARD_SIZE) & empties & TOP_EDGE
            temporary_bitboard = (temporary_bitboard << BOARD_SIZE) & opponent_board & TOP_EDGE

        # moving left ...
        temporary_bitboard = (to_move_board >> 1) & opponent_board
        while temporary_bitboard:
            moves |= (temporary_bitboard >> 1) & empties & RIGHT_EDGE
            temporary_bitboard = (temporary_bitboard >> 1) & opponent_board & RIGHT_EDGE

        # moving right ...
        temporary_bitboard = (to_move_board << 1) & opponent_board
        while temporary_bitboard:
            moves |= (temporary_bitboard << 1) & empties & LEFT_EDGE
            temporary_bitboard = (temporary_bitboard << 1) & opponent_board & LEFT_EDGE

        # moving up left ...
        temporary_bitboard = (to_move_board >> DIAGONAL_MORE) & opponent_board
        while temporary_bitboard:
            moves |= (temporary_bitboard >> DIAGONAL_MORE) & empties & BOTTOM_RIGHT_EDGE
            temporary_bitboard = (temporary_bitboard >> DIAGONAL_MORE) & opponent_board & BOTTOM_RIGHT_EDGE

        # moving up right ...
        temporary_bitboard = (to_move_board >> DIAGONAL_LESS) & opponent_board
        while temporary_bitboard:
            moves |= (temporary_bitboard >> DIAGONAL_LESS) & empties & BOTTOM_LEFT_EDGE
            temporary_bitboard = (temporary_bitboard >> DIAGONAL_LESS) & opponent_board & BOTTOM_LEFT_EDGE

        # moving down left ...
        temporary_bitboard = (to_move_board << DIAGONAL_LESS) & opponent_board
        while temporary_bitboard:
            moves |= (temporary_bitboard << DIAGONAL_LESS) & empties & TOP_RIGHT_EDGE
            temporary_bitboard = (temporary_bitboard << DIAGONAL_LESS) & opponent_board & TOP_RIGHT_EDGE

        # moving down right ...
        temporary_bitboard = (to_move_board << DIAGONAL_MORE) & opponent_board
        while temporary_bitboard:
            moves |= (temporary_bitboard << DIAGONAL_MORE) & empties & TOP_LEFT_EDGE
            temporary_bitboard = (temporary_bitboard << DIAGONAL_MORE) & opponent_board & TOP_LEFT_EDGE

        moves_list = split_bitboard(moves)
        if moves_list == ():
            moves_list = (None,)

        if opponent:
            self._opponent_legal_moves = moves_list
            self.null_move()
        else:
            self._legal_moves = moves_list

        return moves_list

    def null_move(self):
        self.side = WHITE if self.side == BLACK else BLACK
        self._is_game_over = NOT_CALCULATED

    @staticmethod
    def _move_board(move, to_move_board, opponent_board):
        # taking up ...
        temporary_bitboard = (to_move_board >> BOARD_SIZE) & opponent_board
        while temporary_bitboard:
            if (temporary_bitboard >> BOARD_SIZE) & move & BOTTOM_EDGE:
                temp_move = move
                temp_move = (temp_move << BOARD_SIZE) & opponent_board & BOTTOM_EDGE
                while temp_move:
                    to_move_board += temp_move
                    opponent_board -= temp_move
                    temp_move = (temp_move << BOARD_SIZE) & opponent_board & BOTTOM_EDGE
                break
            temporary_bitboard = (temporary_bitboard >> BOARD_SIZE) & opponent_board & BOTTOM_EDGE

        # taking down ...
        temporary_bitboard = (to_move_board << BOARD_SIZE) & opponent_board
        while temporary_bitboard:
            if (temporary_bitboard << BOARD_SIZE) & move & TOP_EDGE:
                temp_move = move
                temp_move = (temp_move >> BOARD_SIZE) & opponent_board & TOP_EDGE
                while temp_move:
                    to_move_board += temp_move
                    opponent_board -= temp_move
                    temp_move = (temp_move >> BOARD_SIZE) & opponent_board & TOP_EDGE
                break
            temporary_bitboard = (temporary_bitboard << BOARD_SIZE) & opponent_board & TOP_EDGE

        # taking left ...
        temporary_bitboard = (to_move_board >> 1) & opponent_board
        while temporary_bitboard:
            if (temporary_bitboard >> 1) & move & RIGHT_EDGE:
                temp_move = move
                temp_move = (temp_move << 1) & opponent_board & RIGHT_EDGE
                while temp_move:
                    to_move_board += temp_move
                    opponent_board -= temp_move
                    temp_move = (temp_move << 1) & opponent_board & RIGHT_EDGE
                break
            temporary_bitboard = (temporary_bitboard >> 1) & opponent_board & RIGHT_EDGE

        # taking right ...
        temporary_bitboard = (to_move_board << 1) & opponent_board
        while temporary_bitboard:
            if (temporary_bitboard << 1) & move & LEFT_EDGE:
                temp_move = move
                temp_move = (temp_move >> 1) & opponent_board & LEFT_EDGE
                while temp_move:
                    to_move_board += temp_move
                    opponent_board -= temp_move
                    temp_move = (temp_move >> 1) & opponent_board & LEFT_EDGE
                break
            temporary_bitboard = (temporary_bitboard << 1) & opponent_board & LEFT_EDGE

        # taking up left ...
        temporary_bitboard = (to_move_board >> DIAGONAL_MORE) & opponent_board
        while temporary_bitboard:
            if (temporary_bitboard >> DIAGONAL_MORE) & move & BOTTOM_RIGHT_EDGE:
                temp_move = move
                temp_move = (temp_move << DIAGONAL_MORE) & opponent_board & BOTTOM_RIGHT_EDGE
                while temp_move:
                    to_move_board += temp_move
                    opponent_board -= temp_move
                    temp_move = (temp_move << DIAGONAL_MORE) & opponent_board & BOTTOM_RIGHT_EDGE
                break
            temporary_bitboard = (temporary_bitboard >> DIAGONAL_MORE) & opponent_board & BOTTOM_RIGHT_EDGE

        # taking up right ...
        temporary_bitboard = (to_move_board >> DIAGONAL_LESS) & opponent_board
        while temporary_bitboard:
            if (temporary_bitboard >> DIAGONAL_LESS) & move & BOTTOM_LEFT_EDGE:
                temp_move = move
                temp_move = (temp_move << DIAGONAL_LESS) & opponent_board & BOTTOM_LEFT_EDGE
                while temp_move:
                    to_move_board += temp_move
                    opponent_board -= temp_move
                    temp_move = (temp_move << DIAGONAL_LESS) & opponent_board & BOTTOM_LEFT_EDGE
                break
            temporary_bitboard = (temporary_bitboard >> DIAGONAL_LESS) & opponent_board & BOTTOM_LEFT_EDGE

        # taking down left ...
        temporary_bitboard = (to_move_board << DIAGONAL_LESS) & opponent_board
        while temporary_bitboard:
            if (temporary_bitboard << DIAGONAL_LESS) & move & TOP_RIGHT_EDGE:
                temp_move = move
                temp_move = (temp_move >> DIAGONAL_LESS) & opponent_board & TOP_RIGHT_EDGE
                while temp_move:
                    to_move_board += temp_move
                    opponent_board -= temp_move
                    temp_move = (temp_move >> DIAGONAL_LESS) & opponent_board & TOP_RIGHT_EDGE
                break
            temporary_bitboard = (temporary_bitboard << DIAGONAL_LESS) & opponent_board & TOP_RIGHT_EDGE

        # taking down right ...
        temporary_bitboard = (to_move_board << DIAGONAL_MORE) & opponent_board
        while temporary_bitboard:
            if (temporary_bitboard << DIAGONAL_MORE) & move & TOP_LEFT_EDGE:
                temp_move = move
                temp_move = (temp_move >> DIAGONAL_MORE) & opponent_board & TOP_LEFT_EDGE
                while temp_move:
                    to_move_board += temp_move
                    opponent_board -= temp_move
                    temp_move = (temp_move >> DIAGONAL_MORE) & opponent_board & TOP_LEFT_EDGE
                break
            temporary_bitboard = (temporary_bitboard << DIAGONAL_MORE) & opponent_board & TOP_LEFT_EDGE

        to_move_board += move

        return to_move_board, opponent_board

    def move(self, move=None):
        self._past_positions.append((self.bitboard_black, self.bitboard_white))

        if move is None:
            pass
        elif self.side == BLACK:
            self.bitboard_black, self.bitboard_white = self._move_board(move, self.bitboard_black, self.bitboard_white)
        else:
            self.bitboard_white, self.bitboard_black = self._move_board(move, self.bitboard_white, self.bitboard_black)

        self._legal_moves = False
        self._opponent_legal_moves = False
        self.null_move()

    def pop(self):
        self.bitboard_black, self.bitboard_white = self._past_positions.pop()

        self._legal_moves = False
        self._opponent_legal_moves = False
        self.null_move()

    def is_game_over(self):
        if self._is_game_over != NOT_CALCULATED:
            return self._is_game_over

        if self.legal_moves() == (None,) and self.legal_moves(opponent=True) == (None,):
            self._is_game_over = True
            return True
        else:
            self._is_game_over = False
            return False

    def score(self):
        return popcount(self.bitboard_black), popcount(self.bitboard_white)

    def empty_spaces(self):
        return BOARD_ARRAY_SIZE - (popcount(self.bitboard_black | self.bitboard_white))

    def get_board(self):
        return self.bitboard_black, self.bitboard_white, self.side

    def __str__(self):
        s_b = map(lambda x: EMPTY if x == 0 else BLACK, board_array(self.bitboard_black))
        s_w = tuple(map(lambda x: EMPTY if x == 0 else WHITE, board_array(self.bitboard_white)))
        s = tuple(SIDE_REPRESENTATION[x if x != 0 else s_w[i]] for i, x in enumerate(s_b))
        s = tuple(" " + " | ".join(s[i: i + BOARD_SIZE]) for i in range(0, BOARD_ARRAY_SIZE, BOARD_SIZE))
        return ("\n" + "-" * (4 * BOARD_SIZE - 1) + "\n").join(s)


if __name__ == "__main__":
    import random

    b = Board()

    while not b.is_game_over():
        print(b)
        print("Legal moves:", b.legal_moves())
        print("Game over:", b.is_game_over())
        print("Score:", b.score())

        m = b.legal_moves()
        b.move(random.choice(m))

        print()

    print(b)
    print("Legal moves:", b.legal_moves())
    print("Game over:", b.is_game_over())
    print("Score:", b.score())
