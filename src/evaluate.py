import chess
import functools
import numpy as np
import chess.polyglot

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

king_middlegame_position_values = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20
]

king_endgame_position_values = [
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50
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
middlegame_position_values = {
    chess.PAWN: np.flip(np.array(pawn_position_values).reshape(8, 8), 0).reshape(64),
    chess.ROOK: np.flip(np.array(rook_position_values).reshape(8, 8), 0).reshape(64),
    chess.KNIGHT: np.flip(np.array(knight_position_values).reshape(8, 8), 0).reshape(64),
    chess.BISHOP: np.flip(np.array(bishop_position_values).reshape(8, 8), 0).reshape(64),
    chess.QUEEN: np.flip(np.array(queen_position_values).reshape(8, 8), 0).reshape(64),
    chess.KING: np.flip(np.array(king_middlegame_position_values).reshape(8, 8), 0).reshape(64)
}

color_multiplier = {
    chess.WHITE: 1,
    chess.BLACK: -1
}

# 6 pieces per color, plus 1 per color for king endgame
@functools.lru_cache(maxsize=14)
def get_position_values_for_color(piece, color, is_endgame):
    values = []
    if is_endgame and piece == chess.KING:
        values = king_endgame_position_values
    else:
        values = middlegame_position_values[piece]

    # reverse the board if black's turn
    return values if color == chess.WHITE else values[::-1]

@functools.lru_cache(maxsize=1000)
def get_position_value(piece, color, square, is_endgame):
    return get_position_values_for_color(piece, color, is_endgame)[square]

# Assume the move is being evaluated before it's made
# How should checks be valued?
def evaluate_move_value(board, move):
    if move.promotion is not None:
        return piece_values[move.promotion]

    value = 0

    if board.is_capture(move):
        value += capture_value(board, move)

    from_square = move.from_square
    to_square = move.to_square
    piece_type = board.piece_at(from_square).piece_type
    color = board.turn

    value += position_value_change(piece_type, color, from_square, to_square, board.is_endgame)

    return value

def position_value_change(piece, color, from_square, to_square, is_endgame):
    from_value = get_position_value(piece, color, from_square, is_endgame)
    to_value = get_position_value(piece, color, to_square, is_endgame)

    return to_value - from_value

# Lesser valued pieces taking higher valued pieces are the best
def capture_value(board, move):
    if board.is_en_passant(move):
        return piece_values[chess.PAWN]

    from_piece = board.piece_at(move.from_square).piece_type
    to_piece = board.piece_at(move.to_square).piece_type

    return piece_values[to_piece] - piece_values[from_piece]
