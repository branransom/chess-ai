import chess
import numpy as np
from evaluate import piece_values, get_position_value, color_multiplier

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

class Board(chess.Board):
    # is there a faster way to check this?
    # once the board becomes "endgame", we shouldn't need to check it again (unless moves were popped off)
    # could short-circuit as soon as we know it's not endgame (2 queens seen, etc)
    def is_endgame(self):
        piece_count = {
            chess.WHITE: initialize_piece_count(),
            chess.BLACK: initialize_piece_count()
        }

        for square in chess.SQUARES:
            piece = self.piece_at(square)

            if not piece:
                continue

            color = piece.color
            piece_type = piece.piece_type

            piece_count[color][piece_type] += 1

        return no_queen_or_at_most_one_minor_piece(piece_count, chess.WHITE) and no_queen_or_at_most_one_minor_piece(piece_count, chess.BLACK)

    def value(self):
        board_value = 0
        is_endgame = self.is_endgame()

        for square in chess.SQUARES:
            piece = self.piece_at(square)

            if not piece:
                continue

            color = piece.color
            piece_type = piece.piece_type

            value = piece_values[piece_type] + get_position_value(piece_type, color, square, is_endgame)

            board_value += value * color_multiplier[color]

        return board_value
