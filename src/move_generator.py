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

def sort_moves_by_value(board, moves):
    return sorted(moves, key=lambda move: evaluate_move_value(board, move), reverse=True)

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

def prioritize_legal_moves(board):
    legal_moves = board.legal_moves

    grouped_moves = groupby(legal_moves, compose_move_type(board))
    sorted_check_moves = sort_moves_by_value(board, grouped_moves['check'])
    sorted_capture_moves = sort_mvv_lva(board, grouped_moves['capture'])
    sorted_quiet_moves = sort_moves_by_value(board, grouped_moves['quiet'])

    # nonquiet moves should be searched first, since they are most likely to increase value
    return sorted_check_moves + sorted_capture_moves + sorted_quiet_moves

def get_moves_to_dequiet(board):
    legal_moves = board.legal_moves
    grouped_moves = groupby(legal_moves, compose_move_type(board))

    sorted_check_moves = sort_moves_by_value(board, grouped_moves['check'])
    sorted_capture_moves = sort_mvv_lva(board, grouped_moves['capture'])

    return sorted_check_moves + sorted_capture_moves


@call_counter
# https://www.chessprogramming.org/Quiescence_Search
# each side should have the option of making no move at all
# consider fivefold repetition, etc... these searches can add time, so leaving them out for now
def quiescence(board, depth, alpha, beta, maximizing_player):
    if maximizing_player and board.is_checkmate():
        # black wins (white made prior move)
        return -math.inf
    elif not maximizing_player and board.is_checkmate():
        # white wins (black made prior move)
        return math.inf
    elif board.is_stalemate():
        return 0

    stand_pat = evaluate(board)

    if depth == 0:
        return stand_pat

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

    moves = get_moves_to_dequiet(board)

    if not moves:
        return evaluate(board)
    
    if maximizing_player:
        for move in moves:
            board.push(move)
            score = quiescence(board, depth - 1, alpha, beta, not maximizing_player)
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
            score = quiescence(board, depth - 1, alpha, beta, not maximizing_player)
            board.pop()

            # if score >= beta:
            #     return beta
            if score <= alpha:
                return alpha
            if beta <= alpha:
                break
            beta = min(beta, score)
        return beta

# Minimax algorithm w/ alpha beta pruning: https://www.youtube.com/watch?v=l-hh51ncgDI
@call_counter
def minimax(board, depth, alpha, beta, maximizing_player):
    if maximizing_player and board.is_checkmate():
        # black wins (white made prior move)
        return -math.inf
    elif not maximizing_player and board.is_checkmate():
        # white wins (black made prior move)
        return math.inf
    elif board.is_stalemate():
        return 0

    if depth == 0:
        return quiescence(board, 5, -math.inf, math.inf, maximizing_player)

    prioritized_moves = prioritize_legal_moves(board)

    if maximizing_player:
        max_eval = -math.inf
        for move in prioritized_moves:
            board.push(move)
            move_eval = minimax(board, depth - 1, alpha, beta, not maximizing_player)
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
            move_eval = minimax(board, depth - 1, alpha, beta, not maximizing_player)
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

def evaluate_move(board, move, depth, alpha, beta, maximizing_player):
    board.push(move)
    move_value = minimax(board, depth - 1, alpha, beta, not maximizing_player)
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

def next_move(board, depth):
    color = board.turn
    best_move = None
    minimax.calls = 0
    quiescence.calls = 0
    alpha = -math.inf
    beta = math.inf

    prioritized_moves = prioritize_legal_moves(board)

    tic = time.perf_counter()

    for move in prioritized_moves:
        move_value = evaluate_move(board, move, depth, alpha, beta, color)
        print(f"move={move}; move_value={move_value}")

        if color and move_value >= alpha:
            alpha = move_value
            best_move = move
        elif not color and move_value <= beta:
            beta = move_value
            best_move = move

    best_move_value = alpha if color else beta

    toc = time.perf_counter()
    print(f"Searched {minimax.calls} minimax moves and {quiescence.calls} quiesce moves, and found best move value: {best_move_value} in {toc - tic:0.4f} seconds")

    return best_move
