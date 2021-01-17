import sys
sys.path.insert(0, 'src')
import unittest
import chess
import chess.polyglot
from transposition_table import TranspositionTable, HashEntry

class TranspositionTableTest(unittest.TestCase):

    def setUp(self):
        self.table = TranspositionTable()

    def test_store_move_if_empty(self):
        board = chess.Board()
        zobrist = chess.polyglot.zobrist_hash(board)
        hash_entry = HashEntry(zobrist, 'e2e4', 5, 20, (-50, 50), 0)

        self.table.replace(hash_entry)

        self.assertEqual(self.table.get(zobrist, 5), hash_entry)

    def test_replace_if_age_is_greater(self):
        board = chess.Board()
        zobrist = chess.polyglot.zobrist_hash(board)
        old_hash_entry = HashEntry(zobrist, 'e2e4', 5, 20, (-50, 50), 0)
        self.table.replace(old_hash_entry)
        new_hash_entry = HashEntry(zobrist, 'e2e4', 5, 20, (-50, 50), 2)

        self.table.replace(new_hash_entry)

        self.assertEqual(self.table.get(zobrist, 5), new_hash_entry)

    def test_replace_if_depth_is_greater_and_age_equal(self):
        board = chess.Board()
        zobrist = chess.polyglot.zobrist_hash(board)
        shallow_hash_entry = HashEntry(zobrist, 'e2e4', 4, 20, (-50, 50), 0)
        self.table.replace(shallow_hash_entry)
        deep_hash_entry = HashEntry(zobrist, 'e2e4', 5, 20, (-50, 50), 0)

        self.table.replace(deep_hash_entry)

        self.assertEqual(self.table.get(zobrist, 5), deep_hash_entry)

    def test_do_not_replace_if_depth_is_lesser_and_age_equal(self):
        board = chess.Board()
        zobrist = chess.polyglot.zobrist_hash(board)
        deep_hash_entry = HashEntry(zobrist, 'e2e4', 5, 20, (-50, 50), 0)
        self.table.replace(deep_hash_entry)
        shallow_hash_entry = HashEntry(zobrist, 'e2e4', 4, 20, (-50, 50), 0)

        self.table.replace(shallow_hash_entry)

        self.assertEqual(self.table.get(zobrist, 5), deep_hash_entry)

if __name__ == '__main__':
    unittest.main()
