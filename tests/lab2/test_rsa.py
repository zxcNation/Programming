import unittest
from src.lab2.rsa import is_prime

class RsaTestCase(unittest.TestCase):
    def test_Prime(self):
        self.assertEqual(is_prime(19), True)

    def test_NotPrime(self):
        self.assertEqual(is_prime(111), False)

    def test_TrivialOne(self):
        self.assertEqual(is_prime(1), True)

    def test_TrivialTwo(self):
        self.assertEqual(is_prime(2), True)


if __name__ == '__main__':
    unittest.main()
