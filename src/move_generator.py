import math
import time
import chess
from collections import defaultdict
from evaluate import evaluate, evaluate_move_value, piece_values

def call_counter(func):
    def helper(*args, **kwargs):
        helper.calls += 1
        return func(*args, **kwargs)
    helper.calls = 0
    helper.__name__= func.__name__

    return helper

def timer(func):
    def helper(*args, **kwargs):
        tic = time.perf_counter()
        result = func(*args, **kwargs)
        toc = time.perf_counter()
        print(f"{func.__name__} took {toc - tic:0.4f} seconds to execute")
        return result
    helper.__name__= func.__name__

    return helper

def sort_moves_by_value(board, moves, is_endgame):
    return sorted(moves, key=lambda move: evaluate_move_value(board, move, is_endgame), reverse=True)

def determine_victim_and_aggressor_types(board, move):
    if board.is_en_passant(move):
        return [move, piece_values[chess.PAWN], piece_values[chess.PAWN]]

    aggressor = board.piece_at(move.from_square).piece_type
    victim = board.piece_at(move.to_square).piece_type

    return [move, piece_values[victim], piece_values[aggressor]]

# Most valuable victim, lease valuable aggressor: https://www.chessprogramming.org/MVV-LVA
def sort_mvv_lva(board, moves):
    victims_and_aggressors = [determine_victim_and_aggressor_types(board, move) for move in moves]
    # move is index 0, victim values are index 1, aggressor values are index 2
    return list(map(lambda x: x[0], sorted(victims_and_aggressors, key=lambda x: (-x[1], x[2]))))

def prioritize_legal_moves(board, is_endgame):
    legal_moves = board.legal_moves

    grouped_moves = groupby(legal_moves, compose_move_type(board))
    sorted_check_moves = sort_moves_by_value(board, grouped_moves['check'], is_endgame)
    sorted_capture_moves = sort_mvv_lva(board, grouped_moves['capture'])
    sorted_quiet_moves = sort_moves_by_value(board, grouped_moves['quiet'], is_endgame)

    # nonquiet moves should be searched first, since they are most likely to increase value
    return sorted_check_moves + sorted_capture_moves + sorted_quiet_moves

def get_moves_to_dequiet(board, is_endgame):
    if board.is_check():
        return prioritize_legal_moves(board, is_endgame)

    legal_moves = board.legal_moves
    
    grouped_moves = groupby(legal_moves, compose_move_type(board))

    sorted_check_moves = sort_moves_by_value(board, grouped_moves['check'], is_endgame)
    sorted_capture_moves = sort_mvv_lva(board, grouped_moves['capture'])

    return sorted_check_moves + sorted_capture_moves


@call_counter
# https://www.chessprogramming.org/Quiescence_Search
# each side should have the option of making no move at all
# consider fivefold repetition, etc... these searches can add time, so leaving them out for now
def quiescence(board, depth, alpha, beta, maximizing_player, is_endgame):
    if maximizing_player and board.is_checkmate():
        # black wins (white made prior move)
        return -math.inf
    elif not maximizing_player and board.is_checkmate():
        # white wins (black made prior move)
        return math.inf
    elif board.is_stalemate() or board.can_claim_draw() or board.is_fivefold_repetition():
        return 0

    stand_pat = evaluate(board, is_endgame)

    if depth == 0:
        return stand_pat

    # stand pat is not valid when in check
    if not board.is_check():
        if maximizing_player:
            if stand_pat >= beta:
                return beta
            if alpha < stand_pat:
                alpha = stand_pat
        else:
            if stand_pat <= alpha:
                return alpha
            if beta > stand_pat:
                beta = stand_pat

    moves = get_moves_to_dequiet(board, is_endgame)

    # if last move resulted in check, then it will stop... add in evasion
    if not moves:
        return stand_pat
    
    if maximizing_player:
        for move in moves:
            board.push(move)
            score = quiescence(board, depth - 1, alpha, beta, not maximizing_player, is_endgame)
            board.pop()

            if score >= beta:
                return beta
            if beta <= alpha:
                break

            alpha = max(alpha, score)
        return alpha
    else:
        for move in moves:
            board.push(move)
            score = quiescence(board, depth - 1, alpha, beta, not maximizing_player, is_endgame)
            board.pop()

            if score <= alpha:
                return alpha
            if beta <= alpha:
                break
            beta = min(beta, score)
        return beta

# Minimax algorithm w/ alpha beta pruning: https://www.youtube.com/watch?v=l-hh51ncgDI
@call_counter
def minimax(board, depth, alpha, beta, maximizing_player, is_endgame):
    if maximizing_player and board.is_checkmate():
        # black wins (white made prior move)
        return -math.inf
    elif not maximizing_player and board.is_checkmate():
        # white wins (black made prior move)
        return math.inf
    elif board.is_stalemate() or board.can_claim_draw() or board.is_fivefold_repetition():
        return 0

    if depth == 0:
        return quiescence(board, 5, alpha, beta, maximizing_player, is_endgame)

    prioritized_moves = prioritize_legal_moves(board, is_endgame)

    if maximizing_player:
        max_eval = -math.inf
        for move in prioritized_moves:
            board.push(move)
            move_eval = minimax(board, depth - 1, alpha, beta, not maximizing_player, is_endgame)
            alpha = max(alpha, move_eval)
            max_eval = max(max_eval, move_eval)
            board.pop()
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for move in prioritized_moves:
            board.push(move)
            move_eval = minimax(board, depth - 1, alpha, beta, not maximizing_player, is_endgame)
            beta = min(beta, move_eval)
            min_eval = min(min_eval, move_eval)
            board.pop()
            if beta <= alpha:
                break
        return min_eval

# input list to split, function to group by
def groupby(list_to_group, fn):
    grouped_list = defaultdict(list)

    for i in list_to_group:
        key = fn(i)
        grouped_list[key].append(i)

    return grouped_list

def evaluate_move(board, move, depth, alpha, beta, maximizing_player, is_endgame):
    board.push(move)
    move_value = minimax(board, depth - 1, alpha, beta, not maximizing_player, is_endgame)
    board.pop()
    return move_value

def compose_move_type(board):
    def determine_move_type(move):
        if board.gives_check(move):
            return 'check'
        elif board.is_capture(move):
            return 'capture'
        else:
            return 'quiet'

    return determine_move_type

def initialize_piece_count():
    return {
        chess.PAWN: 0,
        chess.ROOK: 0,
        chess.KNIGHT: 0,
        chess.BISHOP: 0,
        chess.QUEEN: 0,
        chess.KING: 0
    }

def no_queen_or_at_most_one_minor_piece(piece_count, color):
    counts = piece_count[color]

    return counts[chess.QUEEN] == 0 or (counts[chess.ROOK] == 0 and counts[chess.BISHOP] + counts[chess.KNIGHT] <= 1)

def check_endgame(board):
    piece_count = {
        chess.WHITE: initialize_piece_count(),
        chess.BLACK: initialize_piece_count()
    }

    for square in chess.SQUARES:
        piece = board.piece_at(square)

        if not piece:
            continue

        color = piece.color
        piece_type = piece.piece_type

        piece_count[color][piece_type] += 1

    return no_queen_or_at_most_one_minor_piece(piece_count, chess.WHITE) and no_queen_or_at_most_one_minor_piece(piece_count, chess.BLACK)


def next_move(board, depth):
    color = board.turn
    best_move = None
    is_endgame = check_endgame(board)
    alpha = -math.inf
    beta = math.inf
    minimax.calls = 0
    quiescence.calls = 0

    prioritized_moves = prioritize_legal_moves(board, is_endgame)

    tic = time.perf_counter()

    for move in prioritized_moves:
        move_value = evaluate_move(board, move, depth, alpha, beta, color, is_endgame)
        print(f"move={move}; move_value={move_value}")

        if color and move_value > alpha:
            alpha = move_value
            best_move = move
        elif not color and move_value < beta:
            beta = move_value
            best_move = move

    # handle case where checkmate is impending... we still need to move
    if best_move is None:
        best_move = prioritized_moves[0]

    best_move_value = alpha if color else beta

    toc = time.perf_counter()
    print(f"Searched {minimax.calls} minimax moves and {quiescence.calls} quiesce moves, and found best move {str(best_move)} with value: {best_move_value} in {toc - tic:0.4f} seconds")

    return best_move
