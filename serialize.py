import chess
import numpy as np
import math

color_map = {
    chess.WHITE: 1,
    chess.BLACK: -1
}

piece_map = {
    chess.PAWN: 0,
    chess.KNIGHT: 1,
    chess.BISHOP: 2,
    chess.ROOK: 3,
    chess.QUEEN: 4,
    chess.KING: 5
}

def initialize():
    # 8 x 8 x 7 dimensional array
    # pawns
    # knights
    # bishops
    # rooks
    # queens
    # kings
    # whose turn is it next?
    return np.zeros((7, 64), dtype=np.int8)

def serialize(board):
    state = initialize()

    for square in chess.SQUARES:
        color = board.color_at(square)

        if color is None:
            continue

        piece = board.piece_at(square).piece_type
        state[piece_map[piece], square] = 1 * color_map[color]

    state[6] = board.turn * 1

    return state.reshape(7, 8, 8)
