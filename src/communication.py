import sys
import chess
import argparse
from searcher import Searcher
from board import Board

# UCI gist: https://gist.github.com/aliostad/f4470274f39d29b788c1b09519e67372
def talk():
    '''
    The main input/output loop.
    This implements a slice of the UCI protocol.
    '''
    board = Board()
    depth = get_depth()

    while True:
        msg = input()
        print(f'>>> {msg}', file=sys.stderr)
        
        if (msg == 'quit'):
            break

        command(board, depth, msg)


def command(board, depth, msg):
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
        move = Searcher(board, depth).next_move()
        print(f"bestmove {move}")
        return

    if msg == 'test':
        searcher = Searcher(Board('r5rk/5p1p/5R2/4B3/8/8/7P/7K w'), depth)
        move = searcher.next_move()
        print(f"{move}")
        return

    if msg == 'self':
        board = Board()
        while not board.is_game_over():
            move = Searcher(board, 3).next_move()
            board.push(move)
            print(board)
            print('-----------------')
        return

    if msg == 'eval':
        board = Board('5k2/8/4p3/4Np2/3P4/7r/P3p3/6K1 b - - 0 1')
        print(board.value())
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
