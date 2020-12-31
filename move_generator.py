import math
import time
import logging
from evaluate import evaluate, evaluate_move_value

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
        logging.debug(f"{func.__name__} took {toc - tic:0.4f} seconds to execute")
        return result
    helper.__name__= func.__name__

    return helper

def sort_moves_by_value(board, moves):
    return sorted(moves, key=lambda move: evaluate_move_value(board, move), reverse=True)

def prioritize_legal_moves(board):
    legal_moves = board.legal_moves

    grouped_moves = groupby(legal_moves, compose_move_type(board))
    sorted_nonquiet_moves = sort_moves_by_value(board, grouped_moves['nonquiet'])
    sorted_quiet_moves = sort_moves_by_value(board, grouped_moves['quiet'])

    # nonquiet moves should be searched first, since they are most likely to increase value
    return sorted_nonquiet_moves + sorted_quiet_moves

# should checks be handled differently than captures? the bot is pretty bad at checkmating
# how to handle en passant?
def get_moves_to_dequiet(board):
    moves_to_dequiet = list(filter(lambda move: board.is_capture(move) or board.gives_check(move), board.legal_moves))

    return sort_moves_by_value(board, moves_to_dequiet)

# https://www.chessprogramming.org/Quiescence_Search
# implement capture ordering... https://chess.stackexchange.com/questions/27257/chess-engine-quiescence-search-increases-required-time-by-a-factor-of-20
# only quiesce on the square where the previous move was made?
@call_counter
def quiesce(board, depth, alpha, beta, maximizing_player):
    if board.is_variant_win() and maximizing_player:
        # black wins (white made prior move)
        return -math.inf
    elif board.is_variant_loss() and maximizing_player:
        # white wins (black made prior move)
        return math.inf
    elif board.is_variant_win() and not maximizing_player:
        # white wins (black made prior move)
        return math.inf
    elif board.is_variant_loss() and not maximizing_player:
        # black wins (white made prior move)
        return -math.inf
    elif board.is_variant_draw():
        return 0

    if depth == 0:
        return evaluate(board)

    moves_to_dequiet = get_moves_to_dequiet(board)

    if not moves_to_dequiet:
        return evaluate(board)

    if maximizing_player:
        for move in moves_to_dequiet:
            board.push(move)
            move_eval = quiesce(board, depth - 1, alpha, beta, not maximizing_player)
            alpha = max(alpha, move_eval)
            board.pop()
            if beta <= alpha:
                break
        return alpha
    else:
        for move in moves_to_dequiet:
            board.push(move)
            move_eval = quiesce(board, depth - 1, alpha, beta, not maximizing_player)
            beta = min(beta, move_eval)
            board.pop()
            if beta <= alpha:
                break
        return beta

# Minimax algorithm w/ alpha beta pruning: https://www.youtube.com/watch?v=l-hh51ncgDI
# what happens if maximizing player is black? account for this in the evaluate function
@call_counter
def minimax(board, depth, alpha, beta, maximizing_player):
    if board.is_variant_win() and maximizing_player:
        # black wins (white made prior move)
        return -math.inf
    elif board.is_variant_loss() and maximizing_player:
        # white wins (black made prior move)
        return math.inf
    elif board.is_variant_win() and not maximizing_player:
        # white wins (black made prior move)
        return math.inf
    elif board.is_variant_loss() and not maximizing_player:
        # black wins (white made prior move)
        return -math.inf
    elif board.is_variant_draw():
        return 0

    if board.is_game_over():
        # does the king get removed from the board in checkmate?
        return evaluate(board)

    if depth == 0:
        # the hand-off seems incorrect...
        return quiesce(board, 3, alpha, beta, maximizing_player)

    prioritized_moves = prioritize_legal_moves(board)

    if maximizing_player:
        for move in prioritized_moves:
            board.push(move)
            move_eval = minimax(board, depth - 1, alpha, beta, not maximizing_player)
            alpha = max(alpha, move_eval)
            board.pop()
            if beta <= alpha:
                break
        return alpha
    else:
        for move in prioritized_moves:
            board.push(move)
            move_eval = minimax(board, depth - 1, alpha, beta, not maximizing_player)
            beta = min(beta, move_eval)
            board.pop()
            if beta <= alpha:
                break
        return beta

# input list to split, function to group by
def groupby(list, fn):
    grouped_list = {
        'nonquiet': [],
        'quiet': []
    }

    for i in list:
        key = fn(i)
        grouped_list[key].append(i)

    return grouped_list

def evaluate_move(board, move, depth, maximizing_player):
    board.push(move)
    move_value = minimax(board, depth - 1, -math.inf, math.inf, not maximizing_player)
    board.pop()
    return move_value

def compose_move_type(board):
    def determine_move_type(move):
        if board.is_capture(move) or board.gives_check(move):
            return 'nonquiet'
        else:
            return 'quiet'

    return determine_move_type

def next_move(board, depth):
    color = board.turn
    best_move_value = -math.inf if color else math.inf
    best_move = None

    prioritized_moves = prioritize_legal_moves(board)

    tic = time.perf_counter()

    for move in prioritized_moves:
        move_value = evaluate_move(board, move, depth, color)
        logging.info(f"move={move}; move_value={move_value}")

        if color and move_value > best_move_value:
            best_move_value = move_value
            best_move = move
        elif not color and move_value < best_move_value:
            best_move_value = move_value
            best_move = move

    toc = time.perf_counter()
    logging.info(f"Searched {minimax.calls} minimax moves and {quiesce.calls} quiesce moves, and found best move value: {best_move_value} in {toc - tic:0.4f} seconds")

    return best_move

