import math
import time
import chess
import chess.polyglot
from evaluate import evaluate, color_multiplier
from transposition_table import TranspositionTable, HashEntry, Flag
from decorators import call_counter
from move_sorter import get_moves_to_dequiet, prioritize_legal_moves

class Searcher():
    def __init__(self, board, depth):
        self.board = board
        self.depth = depth
        self.transposition_table = TranspositionTable()

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

    # https://en.wikipedia.org/wiki/Negamax#Negamax_with_alpha_beta_pruning_and_transposition_tables
    # only need to return best move at the top of the tree
    @call_counter
    def negamax(self, board, depth, alpha, beta, **kwargs):
        alpha_orig = alpha

        if board.is_checkmate():
            return -math.inf

        best_move = None

        zobrist = chess.polyglot.zobrist_hash(board)
        stored_entry = self.transposition_table.get(zobrist)

        if stored_entry is not None and stored_entry.depth >= depth:
            if stored_entry.flag == Flag.EXACT:
                return stored_entry.value
            elif stored_entry.flag == Flag.LOWER_BOUND:
                alpha = max(alpha, stored_entry.value)
            elif stored_entry.flag == Flag.UPPER_BOUND:
                beta = min(beta, stored_entry.value)

            if alpha >= beta:
                return stored_entry.value

        if depth == 0:
            return self.quiescence(board, depth, alpha, beta, **kwargs)

        prioritized_moves = prioritize_legal_moves(board)

        max_val = -math.inf
        for move in prioritized_moves:
            board.push(move)
            move_eval = -self.negamax(board, depth - 1, -beta, -alpha, **kwargs)
            board.pop()
            alpha = max(alpha, move_eval)
            if move_eval > max_val:
                best_move = move

            max_val = max(max_val, move_eval)

            if alpha >= beta:
                break

        flag_to_store = None
        if max_val <= alpha_orig:
            flag_to_store = Flag.UPPER_BOUND
        elif max_val >= beta:
            flag_to_store = Flag.LOWER_BOUND
        else:
            flag_to_store = Flag.EXACT
        
        new_entry = HashEntry(zobrist, best_move, depth, max_val, flag_to_store, board.fullmove_number)
        self.transposition_table.replace(new_entry)

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

