import math
import time
from evaluate import evaluate, lost_value

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

# sort these
def get_dequiet_moves(board):
    legal_moves = board.legal_moves
    dequiet_moves = list(filter(lambda move: board.is_checkmate() or board.is_capture(move) or board.gives_check(move), legal_moves))

    return sorted(dequiet_moves, key=lambda move: lost_value(board, move))

# https://www.chessprogramming.org/Quiescence_Search
# implement capture ordering... https://chess.stackexchange.com/questions/27257/chess-engine-quiescence-search-increases-required-time-by-a-factor-of-20
@call_counter
def quiesce(board, depth, alpha, beta, maximizing_player):
    if board.is_game_over() or depth == 0:
        return evaluate(board)

    dequiet_moves = get_dequiet_moves(board)

    if not dequiet_moves:
        return evaluate(board)

    if maximizing_player:
        for move in dequiet_moves:
            board.push(move)
            move_eval = quiesce(board, depth - 1, alpha, beta, not maximizing_player)
            alpha = max(alpha, move_eval)
            board.pop()
            if beta <= alpha:
                break
        return alpha
    else:
        for move in dequiet_moves:
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
        return math.inf
    elif board.is_variant_loss() and maximizing_player:
        return -math.inf
    elif board.is_variant_win() and not maximizing_player:
        return -math.inf
    elif board.is_variant_loss() and not maximizing_player:
        return math.inf

    if board.is_game_over():
        # does the king get removed from the board in checkmate?
        return evaluate(board)

    # "dequiet" the position if it's a capture/check
    # https://www.naftaliharris.com/blog/chess/
    if depth == 0:
        return quiesce(board, 3, alpha, beta, maximizing_player)

    legal_moves = board.legal_moves
    # sorted moves is slow...
    # sorted_moves = sorted(legal_moves, key=lambda move: determine_move_priority(board, move))

    if maximizing_player:
        for move in legal_moves:
            board.push(move)
            move_eval = minimax(board, depth - 1, alpha, beta, not maximizing_player)
            alpha = max(alpha, move_eval)
            board.pop()
            if beta <= alpha:
                break
        return alpha
    else:
        for move in legal_moves:
            board.push(move)
            move_eval = minimax(board, depth - 1, alpha, beta, not maximizing_player)
            beta = min(beta, move_eval)
            board.pop()
            if beta <= alpha:
                break
        return beta

@timer
def evaluate_move(board, move, depth, maximizing_player):
    board.push(move)
    move_value = minimax(board, depth - 1, -math.inf, math.inf, maximizing_player)
    board.pop()
    return move_value

def next_move(board, depth):
    color = board.turn
    best_move_value = -math.inf if color else math.inf
    best_move = None

    legal_moves = board.legal_moves
    tic = time.perf_counter()
    for move in legal_moves:
        move_value = evaluate_move(board, move, depth, not color)
        if color and move_value > best_move_value:
            best_move_value = move_value
            best_move = move
        elif not color and move_value < best_move_value:
            best_move_value = move_value
            best_move = move

    toc = time.perf_counter()
    print(f"Searched {minimax.calls} minimax moves and {quiesce.calls} quiesce moves, and found best move value: {best_move_value} in {toc - tic:0.4f} seconds")

    return best_move

