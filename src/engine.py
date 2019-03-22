import board

INFINITY = 2147483647

A = ord("A")
COORD_TO_BITBOARD = {chr(A + l) + str(n + 1): 1 << (board.BOARD_SIZE * n + l)
                     for l in range(board.BOARD_SIZE) for n in range(board.BOARD_SIZE)}
COORD_TO_BITBOARD["None"] = None
COORD_TO_BITBOARD["NONE"] = None

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

        self.previous_search_position = board_object.get_board()
        self.previous_principal_variation = ()

        self.TRANSPOSITION_TABLE = {}
        self.searched_nodes = 0

    def negamax(self, board_object, depth, alpha, beta, color, pv=()):
        board_key = board_object.get_board()

        if depth == 0:
            try:
                evaluation, _ = self.TRANSPOSITION_TABLE[board_key]
            except KeyError:
                evaluation = self.evaluator(board_object)
                self.TRANSPOSITION_TABLE[board_key] = evaluation, ()
            return color * evaluation, ()

        try:
            return self.TRANSPOSITION_TABLE[board_key]
        except KeyError:
            legal_moves = sorted(board_object.legal_moves(), key=lambda m: m in CORNERS, reverse=True)

            if pv != ():
                legal_moves = sorted(legal_moves, key=lambda m: m != pv[0])
            else:
                pv = (0, )

            value = -INFINITY
            for move in legal_moves:
                self.searched_nodes += 1

                board_object.move(move)
                move_value, move_pv = self.negamax(board_object, depth - 1, -beta, -alpha, -color, pv[1:])
                board_object.pop()

                if -move_value > value:
                    value = -move_value
                    best_move = move
                    best_pv = move_pv

                    alpha = max(alpha, value)
                    if alpha >= beta:
                        break

            pv = (best_move, ) + best_pv
            self.TRANSPOSITION_TABLE[board_key] = value, pv
            return value, pv

    def best_move(self, depth):
        self.TRANSPOSITION_TABLE = {}
        self.searched_nodes = 0

        if self.board.get_board() != self.previous_search_position:
            self.previous_principal_variation = ()

        turn_factor = 1 if self.board.side == board.BLACK else -1
        evaluation, pv = self.negamax(self.board, depth, -INFINITY, INFINITY, turn_factor,
                                      self.previous_principal_variation)

        self.previous_search_position = self.board.get_board()
        self.previous_principal_variation = pv

        return pv, evaluation


if __name__ == "__main__":
    pass
