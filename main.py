import chess
import chess.pgn
from evaluate import get_position_value, get_piece_value

def read_game():
    pgn = open("data/Fischer.pgn")

    first_game = chess.pgn.read_game(pgn)
    print(first_game.headers["Event"])

    board = first_game.board()
    for move in first_game.mainline_moves():
        board.push(move)
        print(board)

def play_game():
    board = chess.Board()

    for i in range(50):
        # if (board.turn == chess.WHITE):
            # input_value = input("Press enter to continue, s to stop... ")
            # if input_value == "s":
            #     break;

        turn = board.turn
        legal_moves = list(board.legal_moves)

        positions = {}

        for move in legal_moves:
            value = 0

            board.push(move)

            for square in chess.SQUARES:
                color = board.color_at(square)
                if color is None:
                    continue

                piece = board.piece_at(square).piece_type
                if color != turn:
                    value += get_piece_value(piece)
                else:
                    value += get_position_value(piece, color, square)

            positions[move] = value
            board.pop()

        best_move = min(positions, key=positions.get)
        board.push(best_move)
        print(board)
        print('----------------')

read_game()
