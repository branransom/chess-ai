import sys
sys.path.insert(0, 'src')
import unittest
import chess
from board_wrapper import Board

class BoardTest(unittest.TestCase):

    def test_board_value(self):
        board = Board('5k2/8/4p3/4Np2/3P4/7r/P3p3/6K1 b - - 0 1')
        self.assertEqual(board.value(), -290)

class WhitePawnTest(unittest.TestCase):
    def test_row_2(self):
        board = Board('8/8/8/8/8/8/PPPPPPPP/8 w - - 0 1')
        self.assertEqual(board.value(), 810)

    def test_row_3(self):
        board = Board('8/8/8/8/8/PPPPPPPP/8/8 w - - 0 1')
        self.assertEqual(board.value(), 780)

    def test_row_4(self):
        board = Board('8/8/8/8/PPPPPPPP/8/8/8 w - - 0 1')
        self.assertEqual(board.value(), 840)

    def test_row_5(self):
        board = Board('8/8/8/PPPPPPPP/8/8/8/8 w - - 0 1')
        self.assertEqual(board.value(), 890)

    def test_row_6(self):
        board = Board('8/8/PPPPPPPP/8/8/8/8/8 w - - 0 1')
        self.assertEqual(board.value(), 940)

    def test_row_7(self):
        board = Board('8/PPPPPPPP/8/8/8/8/8/8 w - - 0 1')
        self.assertEqual(board.value(), 1200)

class BlackPawnTest(unittest.TestCase):
    def test_row_7(self):
        board = Board('8/pppppppp/8/8/8/8/8/8 w - - 0 1')
        self.assertEqual(board.value(), -810)

    def test_row_6(self):
        board = Board('8/8/pppppppp/8/8/8/8/8 w - - 0 1')
        self.assertEqual(board.value(), -780)

    def test_row_5(self):
        board = Board('8/8/8/pppppppp/8/8/8/8 w - - 0 1')
        self.assertEqual(board.value(), -840)

    def test_row_4(self):
        board = Board('8/8/8/8/pppppppp/8/8/8 w - - 0 1')
        self.assertEqual(board.value(), -890)

    def test_row_3(self):
        board = Board('8/8/8/8/8/pppppppp/8/8 w - - 0 1')
        self.assertEqual(board.value(), -940)

    def test_row_2(self):
        board = Board('8/8/8/8/8/8/pppppppp/8 w - - 0 1')
        self.assertEqual(board.value(), -1200)

class WhiteQueenTest(unittest.TestCase):
    def test_a1(self):
        board = Board('8/8/8/8/8/8/8/Q7 w - - 0 1')
        self.assertEqual(board.value(), 880)

    def test_b3(self):
        board = Board('8/8/8/8/8/1Q6/8/8 w - - 0 1')
        self.assertEqual(board.value(), 905)

    def test_g4(self):
        board = Board('8/8/8/8/7Q/8/8/8 w - - 0 1')
        self.assertEqual(board.value(), 895)

class BlackQueenTest(unittest.TestCase):
    def test_a8(self):
        board = Board('q7/8/8/8/8/8/8/8 w - - 0 1')
        self.assertEqual(board.value(), -880)

    def test_g6(self):
        board = Board('8/8/6q1/8/8/8/8/8 w - - 0 1')
        self.assertEqual(board.value(), -905)

    def test_a5(self):
        board = Board('8/8/8/q7/8/8/8/8 w - - 0 1')
        self.assertEqual(board.value(), -895)

if __name__ == '__main__':
    unittest.main()
