import sys
import chess
import argparse
import time
from move_generator import next_move
from evaluate import evaluate

# UCI gist: https://gist.github.com/aliostad/f4470274f39d29b788c1b09519e67372
def talk():
    '''
    The main input/output loop.
    This implements a slice of the UCI protocol.
    '''
    board = chess.Board()
    depth = get_depth()
    # model = read_model()

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
        move = next_move(board, depth)
        print(f"bestmove {move}")
        return

    if msg == 'test':
        move = next_move(chess.Board('rnbqkb1r/pp2pppp/3p1n2/8/3NP3/2N5/PPP2PPP/R1BQKB1R b KQkq - 1 1'), depth)
        print(f"{move}")
        return

    if msg == 'self':
        board = chess.Board('rnbqkb1r/pp2pppp/3p1n2/8/3NP3/2N5/PPP2PPP/R1BQKB1R b KQkq - 1 1')
        while not board.is_game_over():
            move = next_move(board, depth)
            board.push(move)
            print(board)
            print(f"{move}")
            print('-----------------')
            time.sleep(5)
        return

    if msg == 'eval':
        board = chess.Board('r1bqkbnr/ppp1ppp1/2np4/7p/3PPB2/P1N2N1P/1PP2PP1/R2QKB1R w KQkq - 0 1')
        print(evaluate(board))
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
