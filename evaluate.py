import chess
import math
import time
import numpy as np

pawn_position_values = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]

knight_position_values = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]

bishop_position_values = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
]

rook_position_values = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0
]

queen_position_values = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

king_position_values = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20
]

piece_values = {
    chess.PAWN: 100,
    chess.ROOK: 500,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# gotta be a better way to do this... the eval rows are ordered opposite the python-chess ordering of squares
position_values = {
    chess.PAWN: np.flip(np.array(pawn_position_values).reshape(8, 8), 0).reshape(64),
    chess.ROOK: np.flip(np.array(rook_position_values).reshape(8, 8), 0).reshape(64),
    chess.KNIGHT: np.flip(np.array(knight_position_values).reshape(8, 8), 0).reshape(64),
    chess.BISHOP: np.flip(np.array(bishop_position_values).reshape(8, 8), 0).reshape(64),
    chess.QUEEN: np.flip(np.array(queen_position_values).reshape(8, 8), 0).reshape(64),
    chess.KING: np.flip(np.array(king_position_values).reshape(8, 8), 0).reshape(64)
}

color_multiplier = {
    chess.WHITE: 1,
    chess.BLACK: -1
}

count = 0

def get_position_value(piece, color, square):
    if (color == chess.WHITE):
        return position_values[piece][square]
    else:
        return position_values[piece][::-1][square]

def get_piece_value(piece):
    return piece_values[piece]

def evaluate(board):
    value = 0

    for square in chess.SQUARES:
        color = board.color_at(square)

        if color is None:
            continue

        piece = board.piece_at(square).piece_type
        value += get_piece_value(piece) * color_multiplier[color]
        value += get_position_value(piece, color, square) * color_multiplier[color]
        
    return value

def call_counter(func):
    def helper(*args, **kwargs):
        helper.calls += 1
        return func(*args, **kwargs)
    helper.calls = 0
    helper.__name__= func.__name__

    return helper

# Minimax algorithm w/ alpha beta pruning: https://www.youtube.com/watch?v=l-hh51ncgDI
# what happens if maximizing player is black? account for this in the evaluate function
@call_counter
def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate(board)

    legal_moves = board.legal_moves

    if maximizing_player:
        max_eval = -math.inf
        for move in legal_moves:
            board.push(move)
            move_eval = minimax(board, depth -1, alpha, beta, not maximizing_player)
            max_eval = max(max_eval, move_eval)
            alpha = max(alpha, move_eval)
            if beta <= alpha:
                break
            board.pop()
        return max_eval
    else:
        min_eval = math.inf
        for move in legal_moves:
            board.push(move)
            move_eval = minimax(board, depth -1, alpha, beta, maximizing_player)
            min_eval = min(min_eval, move_eval)
            beta = min(beta, move_eval)
            if beta <= alpha:
                break
            board.pop()
        return min_eval

def next_move(board, depth):
    best_move_value = -math.inf
    best_move = None

    legal_moves = board.legal_moves
    tic = time.perf_counter()
    for move in legal_moves:
        board.push(move)
        move_value = minimax(board, depth - 1, -math.inf, math.inf, False)
        board.pop()
        if move_value >= best_move_value:
            best_move_value = move_value
            best_move = move

    toc = time.perf_counter()
    print(f"Searched {minimax.calls} moves, and found best move value: {best_move_value} in {toc - tic:0.4f} seconds")

    return best_move
