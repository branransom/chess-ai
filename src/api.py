import json
from searcher import Searcher
from board import Board
from transposition_table import TranspositionTable
from flask import Flask, request, jsonify
from flask_cors import CORS
from json_encoder import JSONEncoder
import os
import psycopg2


DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()
cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abc'def"))
cur.execute("SELECT * FROM test;")
cur.fetchone()
conn.commit()
cur.close()
conn.close()

app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = True
app.json_encoder = JSONEncoder
depth = 3
transposition_table = TranspositionTable()

@app.route('/next_move', methods=['POST'])
def next_move():
    data = request.json
    fen = data.get('fen')

    board = Board(fen)
    move = Searcher(board, depth, transposition_table).next_move()

    return jsonify({ "move": str(move) })

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
