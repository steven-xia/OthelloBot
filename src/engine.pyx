import board

INFINITY = 2147483647

A = ord("A")
COORD_TO_BITBOARD = {chr(A + l) + str(n + 1): 1 << (board.BOARD_SIZE * n + l)
                     for l in range(board.BOARD_SIZE) for n in range(board.BOARD_SIZE)}
COORD_TO_BITBOARD["None"] = None

BITBOARD_TO_COORD = {v: k for k, v in COORD_TO_BITBOARD.items()}

CORNERS = frozenset((
    1 << 0,
    1 << 7,
    1 << 56,
    1 << 63
))


class Engine:
    def __init__(self, board_object, evaluator):
        self.board = board_object
        self.evaluator = evaluator

        self.previous_moves = self.board.legal_moves()
        self.last_search_position = self.board.get_board()

        self.TRANSPOSITION_TABLE = {}
        self.searched_nodes = 0

    def negamax(self, board_object, depth, alpha, beta, color):
        board_key = board_object.get_board()

        if depth == 0:
            try:
                evaluation = self.TRANSPOSITION_TABLE[board_key]
            except KeyError:
                evaluation = self.evaluator(board_object)
                self.TRANSPOSITION_TABLE[board_key] = evaluation
            return color * evaluation

        try:
            return self.TRANSPOSITION_TABLE[board_key]
        except KeyError:
            legal_moves = sorted(board_object.legal_moves(), key=lambda m: m in CORNERS, reverse=True)

            value = -INFINITY
            for move in legal_moves:
                self.searched_nodes += 1

                board_object.move(move)
                value = max(value, -self.negamax(board_object, depth - 1, -beta, -alpha, -color))
                board_object.pop()

                alpha = max(alpha, value)
                if alpha >= beta:
                    break

            self.TRANSPOSITION_TABLE[board_key] = value
            return value

    def best_move(self, depth):
        self.TRANSPOSITION_TABLE = {}
        self.searched_nodes = 0

        turn_factor = -1 if self.board.side == board.BLACK else 1

        moves = {}

        if self.board.get_board() == self.last_search_position:
            legal_moves = self.previous_moves
        else:
            legal_moves = sorted(self.board.legal_moves(), key=lambda m: m in CORNERS, reverse=True)

        alpha = -INFINITY
        for move in legal_moves:
            self.board.move(move)
            moves[move] = -self.negamax(self.board, depth - 1, -INFINITY, -alpha, turn_factor)
            self.board.pop()

            alpha = max(alpha, moves[move])

        best_moves = sorted(moves, key=lambda k: moves[k], reverse=True)
        self.previous_moves = best_moves
        self.last_search_position = self.board.get_board()

        return best_moves[0], moves[best_moves[0]]


if __name__ == "__main__":
    pass
