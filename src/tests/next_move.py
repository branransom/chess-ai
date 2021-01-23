import sys
sys.path.insert(0, 'src')
import unittest
from board import Board
from searcher import Searcher
from transposition_table import TranspositionTable

class NextMoveTest(unittest.TestCase):

    # Example taken from Dad's first time beating the bot: https://lichess.org/YUam7SaocBld
    def test_detect_oppononent_checkmate(self):
        transposition_table = TranspositionTable()
        board = Board('1r3rk1/p1p3pp/3bp3/1p1P1q2/P3pP2/2B1P2P/1P4Q1/4K1NR b K - 0 1')
        move = Searcher(board, 3, transposition_table).next_move()
        self.assertEqual(str(move), 'f8f7')

    # Need to make a move even if there is an impending checkmate
    def test_move_out_of_checkmate(self):
        transposition_table = TranspositionTable()
        board = Board('1r1qr3/pppbbQ1k/2n1p1p1/2PpP3/3P4/2P2N2/P1B2PP1/1RB1K3 b - - 0 1')
        move = Searcher(board, 3, transposition_table).next_move()
        self.assertEqual(str(move), 'h7h8')

    def test_mate_in_three(self):
        transposition_table = TranspositionTable()
        board = Board('r5rk/5p1p/5R2/4B3/8/8/7P/7K w')
        move = Searcher(board, 3, transposition_table).next_move()
        self.assertEqual(str(move), 'f6a6')

    def test_dont_sacrifice_rook(self):
        transposition_table = TranspositionTable()
        board = Board('2r3k1/6p1/5p1p/p2r4/3p4/6B1/PPP2PPP/R3R1K1 w - - 0 1')
        move = Searcher(board, 3, transposition_table).next_move()
        self.assertNotEqual(str(move), 'e1e8')

    # Review the end of this game: https://lichess.org/Bk7qEJiX#94
    # Figure out how to prevent the passed pawn from reaching promotion
    # def test_prevent_opponent_pawn_promotion(self):
    #     board = Board('4k3/3R4/4p3/4Np2/3P4/4p2r/P7/6K1 w - - 0 1')
    #     move = Searcher(board, 3).next_move()
    #     self.assertEqual(str(move), 'd7g7')

    # def test_dont_sacrifice_rook(self):
    #     board = Board('6k1/5R2/4p3/4Np2/3P4/7r/P3p1K1/8 w - - 0 1')
    #     move = Searcher(board, 3).next_move()
    #     self.assertNotEqual(str(move), 'f7f8')


if __name__ == '__main__':
    unittest.main()
