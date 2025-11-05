
import unittest

from src.lab3.sudoku import get_row
from src.lab3.sudoku import get_col
from src.lab3.sudoku import get_block

class TestSudokuHelpers(unittest.TestCase):
    def setUp(self):
        self.sample_grid = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9'],
            ['4', '5', '6', '7', '8', '9', '1', '2', '3'],
            ['7', '8', '9', '1', '2', '3', '4', '5', '6'],
            ['2', '3', '4', '5', '6', '7', '8', '9', '1'],
            ['5', '6', '7', '8', '9', '1', '2', '3', '4'],
            ['8', '9', '1', '2', '3', '4', '5', '6', '7'],
            ['3', '4', '5', '6', '7', '8', '9', '1', '2'],
            ['6', '7', '8', '9', '1', '2', '3', '4', '5'],
            ['9', '1', '2', '3', '4', '5', '6', '7', '8']
        ]

        self.grid_with_dots = [
            ['1', '2', '.', '4', '.', '6'],
            ['4', '.', '6', '7', '8', '9'],
            ['.', '8', '9', '.', '2', '3'],
            ['2', '3', '4', '5', '6', '.'],
            ['5', '6', '.', '8', '9', '1'],
            ['8', '.', '1', '2', '3', '4']
        ]

    def test_get_row(self):
        result = get_row(self.sample_grid, (0, 0))
        expected = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        self.assertEqual(result, expected)

        result = get_row(self.sample_grid, (4, 0))
        expected = ['5', '6', '7', '8', '9', '1', '2', '3', '4']
        self.assertEqual(result, expected)

    def test_get_row_with_dots(self):
        result = get_row(self.grid_with_dots, (0, 0))
        expected = ['1', '2', '.', '4', '.', '6']
        self.assertEqual(result, expected)

        result = get_row(self.grid_with_dots, (2, 0))
        expected = ['.', '8', '9', '.', '2', '3']
        self.assertEqual(result, expected)

    def test_get_col(self):
        result = get_col(self.sample_grid, (0, 0))
        expected = ['1', '4', '7', '2', '5', '8', '3', '6', '9']
        self.assertEqual(result, expected)

        result = get_col(self.sample_grid, (0, 4))
        expected = ['5', '8', '2', '6', '9', '3', '7', '1', '4']
        self.assertEqual(result, expected)

    def test_get_col_with_dots(self):
        result = get_col(self.grid_with_dots, (0, 1))
        expected = ['2', '.', '8', '3', '6', '.']
        self.assertEqual(result, expected)

        result = get_col(self.grid_with_dots, (0, 2))
        expected = ['.', '6', '9', '4', '.', '1']
        self.assertEqual(result, expected)


    def test_get_block(self):
        result = get_block(self.sample_grid, (0, 0))
        expected = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        self.assertEqual(result, expected)

        result = get_block(self.sample_grid, (1, 1))
        expected = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        self.assertEqual(result, expected)

    def test_get_block_with_dots(self):
        test_grid = [
            ['1', '2', '.', '4', '5', '6'],
            ['4', '.', '6', '7', '8', '9'],
            ['.', '8', '9', '1', '2', '3'],
            ['2', '3', '4', '5', '6', '7'],
            ['5', '6', '7', '8', '9', '1'],
            ['8', '9', '1', '2', '3', '4']
        ]

        result = get_block(test_grid, (0, 1))
        expected = ['1', '2', '.', '4', '.', '6', '.', '8', '9']
        self.assertEqual(result, expected)


if __name__ == '__main__':

    unittest.main()