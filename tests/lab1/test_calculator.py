import unittest



from src.lab1.calculator import calculate

class TestCalculator(unittest.TestCase):

    def test_addition(self):
        self.assertEqual(calculate("2 + 3"), 5.0)

    def test_subtraction(self):
        self.assertEqual(calculate("5 - 2"), 3.0)

    def test_multiplication(self):
        self.assertEqual(calculate("4 * 3"), 12.0)

    def test_division(self):
        self.assertEqual(calculate("10 / 2"), 5.0)

    def test_precedence(self):
        self.assertEqual(calculate("1 + 2 * 3"), 7.0)

    def test_parentheses(self):
        self.assertEqual(calculate("(1 + 2) * 3"), 9.0)

    def test_float_numbers(self):
        self.assertEqual(calculate("2.5 + 3.5"), 6.0)

    def test_division_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            calculate("10 / 0")

    def test_invalid_expression(self):
        with self.assertRaises(ValueError):
            calculate("invalid expression")

    def test_number_starting_with_dot(self):
        self.assertEqual(calculate(".5 + 1"), 1.5)

    def test_multiple_operations_with_parentheses(self):
        self.assertEqual(calculate("(1 + 2) * (3 - 1) / 4"), 1.5)

    def test_operators_and_parentheses(self):
        self.assertEqual(calculate("(1+2)*3"), 9.0)

if __name__ == '__main__':
    unittest.main()
