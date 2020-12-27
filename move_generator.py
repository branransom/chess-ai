import numpy as np
import tensorflow as tf
from serialize import serialize

# ignore depth for now
def next_move(depth, board, model):
    legal_moves = list(board.legal_moves)
    positions = {}

    print('----------')
    print(legal_moves)

    for move in legal_moves:
        board.push(move)

        serialized_board = np.array([serialize(board)]).astype(np.float32)
        serialized_board = np.moveaxis(serialized_board, 1, -1) # workaround for tf expecting channels column last

        prediction = model.predict(serialized_board)

        print(prediction)

        positions[move] = prediction

        board.pop()

    # switch to minimizing the opponent's chance of winning
    return max(positions, key=positions.get)




