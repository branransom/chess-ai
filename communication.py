import sys
import chess
import argparse
from move_generator import next_move
from train import read_model


def talk():
    '''
    The main input/output loop.
    This implements a slice of the UCI protocol.
    '''
    board = chess.Board()
    depth = get_depth()
    model = read_model()

    while True:
        msg = input()
        print(f'>>> {msg}', file=sys.stderr)
        
        if (msg == 'quit'):
            break

        command(depth, board, msg, model)


def command(depth, board, msg, model):
    '''
    Accept UCI commands and respond.
    The board state is also updated.
    '''
    if msg == 'uci':
        print("id name brandobot")
        print("id author Brandon Ransom")
        print("uciok")
        return

    if msg == 'isready':
        print('readyok')
        return

    if msg == 'ucinewgame':
        return

    if 'position startpos moves' in msg:
        moves = msg.split(' ')[3:]
        board.clear()
        board.set_fen(chess.STARTING_FEN)
        for move in moves:
            board.push(chess.Move.from_uci(move))
        return

    if 'position fen' in msg:
        fen = ' '.join(msg.split(' ')[2:])
        board.set_fen(fen)
        return

    if msg[0:2] == 'go':
        move = next_move(depth, board, model)
        print(f"bestmove {move}")
        return


def get_depth():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--depth',
        default=3,
        help='provide an integer (default: 3)'
    )
    args = parser.parse_args()
    return int(args.depth)
