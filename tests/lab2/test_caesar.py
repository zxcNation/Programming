import unittest
from src.lab2.caesar import encrypt_caesar
from src.lab2.caesar import decrypt_caesar
class CaesarTestCase(unittest.TestCase):
    def test_OnlyUpperCaseEncrypt(self):
        self.assertEqual(encrypt_caesar("PYTHON"), "SBWKRQ")

    def test_OnlyLowerCaseEncrypt(self):
        self.assertEqual(encrypt_caesar("python"), "sbwkrq")

    def test_PlaintextWithAnotherSymbols(self):
        self.assertEqual(encrypt_caesar("Python3.6"), "Sbwkrq3.6")

    def test_OnlyUpperCaseDecrypt(self):
        self.assertEqual(decrypt_caesar("SBWKRQ"), "PYTHON")

    def test_OnlyLowerCaseDecrypt(self):
        self.assertEqual(decrypt_caesar("sbwkrq"), "python")

    def test_CiphertextWithAnotherSymbols(self):
        self.assertEqual(decrypt_caesar("Sbwkrq3.6"), "Python3.6")


if __name__ == '__main__':
    unittest.main()
