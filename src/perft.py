import time
from board import Board
from move_sorter import get_moves_to_dequiet, prioritize_legal_moves

def perft(depth):
    nodes = 0

    if depth == 0:
        return 1

    moves = prioritize_legal_moves(board)

    for move in moves:
        board.push(move)
        nodes += perft(depth - 1)
        board.pop()

    return nodes

if __name__ == '__main__':
    tic = time.perf_counter()
    board = Board()
    nodes = perft(3)
    toc = time.perf_counter()
    print(f"Searched {nodes} moves in {toc - tic:0.4f} seconds")
