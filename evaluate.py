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

@functools.lru_cache(maxsize=1000)
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
        inc_value = (get_piece_value(piece) + get_position_value(piece, color, square)) * color_multiplier[color]
        value += inc_value

    return value

def lost_value(board, move):
    try:
        from_piece = board.piece_at(move.from_square).piece_type
        to_piece = board.piece_at(move.to_square).piece_type

        return piece_values[to_piece] - piece_values[from_piece]
    except:
        # en passants and checks will throw an exception, since they do not have a capturing move
        return 0
