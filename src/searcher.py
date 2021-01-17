import math
import time
from evaluate import evaluate, color_multiplier
from decorators import call_counter
from move_sorter import get_moves_to_dequiet, prioritize_legal_moves

class Searcher():
    def __init__(self, board, depth):
        self.board = board
        self.depth = depth

    @call_counter
    def quiescence(self, board, depth, alpha, beta, **kwargs):
        color = board.turn

        if board.is_checkmate():
            return -math.inf

        stand_pat = evaluate(board) * color_multiplier[color]

        if depth < -10:
            return stand_pat

        if not board.is_check():
            if stand_pat >= beta:
                return beta
            alpha = max(alpha, stand_pat)

        moves = get_moves_to_dequiet(board)

        if not moves:
            return stand_pat

        for move in moves:
            board.push(move)
            move_eval = -self.quiescence(board, depth - 1, -beta, -alpha)
            board.pop()

            if move_eval >= beta:
                return beta
            alpha = max(alpha, move_eval)

        return alpha

    @call_counter
    def negamax(self, board, depth, alpha, beta, **kwargs):
        best_move = None

        if board.is_checkmate():
            return -math.inf

        if depth == 0:
            return self.quiescence(board, depth, alpha, beta, **kwargs)

        prioritized_moves = prioritize_legal_moves(board)

        max_val = -math.inf
        for move in prioritized_moves:
            board.push(move)
            move_eval = -self.negamax(board, depth - 1, -beta, -alpha, **kwargs)
            board.pop()
            alpha = max(alpha, move_eval)
            if depth == self.depth and move_eval > max_val:
                best_move = move

            max_val = max(max_val, move_eval)

            if alpha >= beta:
                break

        if depth == self.depth:
            return ( best_move, max_val )
        return max_val

    def next_move(self):
        best_move = None
        alpha = -math.inf
        beta = math.inf

        prioritized_moves = prioritize_legal_moves(self.board)

        tic = time.perf_counter()

        best_move, best_move_value = self.negamax(self.board, self.depth, alpha, beta)

        # handle case where checkmate is impending... we still need to move
        if best_move is None:
            best_move = prioritized_moves[0]

        toc = time.perf_counter()
        print(f"Searched {self.negamax.calls} minimax moves and {self.quiescence.calls} quiesce moves, and found best move {best_move} with value: {best_move_value} in {toc - tic:0.4f} seconds")

        return best_move

