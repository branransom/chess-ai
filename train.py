import chess
import chess.pgn
import numpy as np
import tensorflow as tf
import os
import time
from sklearn.model_selection import train_test_split
from serialize import serialize

def read_model():
    model = tf.keras.models.load_model('model')
    model.summary()
    return model

def read_game(file):
    print(f'Reading games from {file}...')
    pgn = open(file)

    X = []
    y = []
    games_read = 0

    result_states = { '1/2-1/2': 0, '0-1': -1, '1-0': 1 }

    try:
        while True:
            game = chess.pgn.read_game(pgn)

            if game is None:
                break;

            result = game.headers["Result"]
            if result not in result_states:
                continue;

            result = result_states[result]

            board = game.board()
            for move in game.mainline_moves():
                board.push(move)
                serialized_board = serialize(board)
                X.append(serialized_board)
                y.append(result)

            games_read += 1
            print(f'games read: {games_read}')
    except:
        print('Encountered exception... continuing')

    X = np.array(X).astype(np.float32)
    y = np.array(y).astype(np.float32)

    return X, y


def read_games():
    X = np.empty([1, 7, 8, 8])
    y = np.empty([1, 7, 8, 8])

    directory = 'data'
    for filename in os.listdir(directory):
        if filename.endswith(".pgn"):
            tic = time.perf_counter()
            X_pgn, y_pgn = read_game(os.path.join(directory, filename))
            X = np.concatenate(( X, X_pgn ), axis=0) if X is not None else X_pgn
            y = np.concatenate(( y, y_pgn ), axis=0) if y is not None else y_pgn
            toc = time.perf_counter()
            print(f"Read game {toc - tic:0.4f} seconds")
        else:
            continue

    return X, y

def train():
    X, y = read_games()
    X = np.moveaxis(X, 1, -1) # workaround for error, where tensorflow is expecting channels column last

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

    cnn = tf.keras.models.Sequential()

    # Convolution
    print('Convolution')
    cnn.add(tf.keras.layers.Conv2D(filters=32, kernel_size=3, activation='relu'))

    # Pooling
    print('Pooling')
    cnn.add(tf.keras.layers.MaxPool2D(pool_size=2, strides=2, padding='same'))

    # Second convolution layer
    print('Second convolution layer')
    cnn.add(tf.keras.layers.Conv2D(filters=32, kernel_size=3, activation='relu'))
    cnn.add(tf.keras.layers.MaxPool2D(pool_size=2, strides=2))

    # Flattening
    print('Flattening')
    cnn.add(tf.keras.layers.Flatten())

    # Full connection
    print('Full connection')
    cnn.add(tf.keras.layers.Dense(units=128, activation='relu'))

    # Output layer
    print('Output layer')
    cnn.add(tf.keras.layers.Dense(units=1, activation='sigmoid'))

    # Compiling the CNN
    print('Compiling')
    cnn.compile(optimizer = 'adam', loss = 'binary_crossentropy', metrics = ['accuracy'])

    # Training
    print('Training')
    cnn.fit(x=X_train, y=y_train, validation_split=0.2, epochs = 35)

    cnn.save('model')
    print("Saved model to disk")

    # example_board = X_test
    # result = y_test

    # prediction = cnn.predict(example_board)

    # print(prediction)
    # print(result)

