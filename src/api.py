import json
import chess
from searcher import Searcher
from board_wrapper import Board
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

@app.route('/next_move', methods=['POST'])
def next_move():
    data = request.json
    fen = data.get('fen')

    print(fen)

    if fen is not None:
        board = Board(fen)
    else:
        board = Board()

    if board.is_game_over():
        return jsonify({ "fen": board.fen(), "is_game_over": True })
    
    move = Searcher(board, depth, transposition_table).next_move()

    board.push(move)

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

@app.route('/principal_variation', methods=['GET'])
def get_principal_variation():
    with open('principal_variation.json') as f:
        data = json.load(f)

    return jsonify(data)

if __name__ == "__main__":
    app.run()
