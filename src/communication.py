import sys
import chess
import argparse
from searcher import Searcher
from board import Board
from transposition_table import TranspositionTable

# UCI gist: https://gist.github.com/aliostad/f4470274f39d29b788c1b09519e67372
def talk():
    '''
    The main input/output loop.
    This implements a slice of the UCI protocol.
    '''
    board = Board()
    depth = get_depth()
    transposition_table = TranspositionTable()

    while True:
        msg = input()
        print(f'>>> {msg}', file=sys.stderr)
        
        if (msg == 'quit'):
            break

        command(board, depth, transposition_table, msg)


def command(board, depth, transposition_table, msg):
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
        if board.is_endgame:
            move = Searcher(board, depth + 4, transposition_table).next_move()
        else:
            move = Searcher(board, depth, transposition_table).next_move()
        print(f"bestmove {move}")
        return

    if msg == 'test':
        searcher = Searcher(Board('r5rk/5p1p/5R2/4B3/8/8/7P/7K w'), depth, transposition_table)
        move = searcher.next_move()
        print(f"{move}")
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
