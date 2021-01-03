import sys
sys.path.insert(0, 'src')
import unittest
import chess
from move_generator import next_move

class NextMove(unittest.TestCase):

    # Example taken from Dad's first time beating the bot: https://lichess.org/YUam7SaocBld
    def test_detect_oppononent_checkmate(self):
        board = chess.Board('1r3rk1/p1p3pp/3bp3/1p1P1q2/P3pP2/2B1P2P/1P4Q1/4K1NR b K - 0 1')
        move = next_move(board, 3)
        self.assertEqual(str(move), 'g7g6')

if __name__ == '__main__':
    unittest.main()
