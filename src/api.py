import json
import chess
from searcher import Searcher
from board import Board
from transposition_table import TranspositionTable
from flask import Flask, request, jsonify
from flask_cors import CORS
from json_encoder import JSONEncoder

app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = True
app.json_encoder = JSONEncoder
depth = 3
transposition_table = TranspositionTable()

@app.route('/reset', methods=['POST'])
def reset():
    global transposition_table
    transposition_table = TranspositionTable()

    return jsonify({ "success": True })

@app.route('/move', methods=['POST'])
def move():
    data = request.json
    starting_fen = data.get('fen')
    source_square = data.get('sourceSquare')
    target_square = data.get('targetSquare')

    if source_square is None:
        return 'Must pass sourceSquare', 400

    if target_square is None:
        return 'Must pass targetSquare', 400

    if starting_fen is not None:
        board = Board(starting_fen)
    else:
        board = Board()

    move = chess.Move(chess.parse_square(source_square), chess.parse_square(target_square))
    board.push(move)

    return jsonify({ "fen": board.fen(), "last_move": str(move) })

@app.route('/next_move', methods=['POST'])
def next_move():
    data = request.json
    fen = data.get('fen')

    if fen is not None:
        board = Board(fen)
    else:
        board = Board()

    if board.is_game_over():
        return jsonify({ "fen": board.fen(), "is_game_over": True })
    
    move = Searcher(board, depth, transposition_table).next_move()

    return jsonify({ "fen": board.fen(), "last_move": str(move), "is_game_over": False })

@app.route('/transposition_table', methods=['GET'])
def get_transposition_table():
    table = getattr(transposition_table, 'table')
    json_table = list(map(lambda x: x.json(), filter(lambda entry: entry is not None, table)))

    return jsonify(json_table)

@app.route('/decision_tree', methods=['GET'])
def get_decision_tree():
    with open('tree.json') as f:
        data = json.load(f)

    return jsonify(data)


app.run()
