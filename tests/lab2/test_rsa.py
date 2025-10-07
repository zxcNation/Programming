import unittest
from src.lab2.rsa import is_prime
from src.lab2.rsa import gcd
from src.lab2.rsa import multiplicative_inverse
class RsaTestCase(unittest.TestCase):
    def test_Prime(self):
        self.assertEqual(is_prime(19), True)

    def test_NotPrime(self):
        self.assertEqual(is_prime(111), False)

    def test_TrivialOne(self):
        self.assertEqual(is_prime(1), True)

    def test_TrivialTwo(self):
        self.assertEqual(is_prime(2), True)

    def test_CoprimeNumbers(self):
        self.assertEqual(gcd(7,5), 1)

    def test_NotCoprimeNumbers(self):
        self.assertEqual(gcd(5, 25), 5)

    def test_MultiplicativeInverse(self):
        self.assertEqual(multiplicative_inverse(7, 40), 23)

if __name__ == '__main__':
    unittest.main()
