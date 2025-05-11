#!/usr/bin/python3

import unittest
import sudoku

class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board1s = """
..2.3.546
.945.12..
7....6...
.....76.1
465.2.3.7
..76.3...
.....2..9
.213.478.
3.8.1.4..
"""
        # First line of the board
        self.board1l0 = ['.','.','2','.','3','.','5','4','6']
        self.b = sudoku.Sudoku(self.board1s)
    
    def tearDown(self):
        pass

    def test_init(self):
        self.assertTrue(True)
        board1 = sudoku.gridStringToLines(self.board1s)
        # Check first line of conversion
        self.assertEqual(board1[0], self.board1l0)
        # Now work through the board we've created in setUp()
        self.assertFalse(self.b.is_finished())
        self.assertTrue(self.b.is_valid())

if __name__ == "__main__":
    unittest.main()
