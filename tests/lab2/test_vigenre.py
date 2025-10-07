import unittest
from src.lab2.vigenre import encrypt_vigenere
from src.lab2.vigenre import decrypt_vigenere

class VigenreTestCase(unittest.TestCase):
    def test_OnlyUpperCaseEncrypt(self):
        self.assertEqual(encrypt_vigenere("ATTACKATDAWN", "LEMON"), "LXFOPVEFRNHR")

    def test_OnlyLowerCaseEncrypt(self):
        self.assertEqual(encrypt_vigenere("python", "ab"), "pztioo")

    def test_DifferentCasesEncrypt(self):
        self.assertEqual(encrypt_vigenere("PYTHON", "ab"), "PZTIOO")

    def test_OnlyUpperCaseDecrypt(self):
        self.assertEqual(decrypt_vigenere("LXFOPVEFRNHR", "LEMON"), "ATTACKATDAWN")

    def test_OnlyLowerCaseDecrypt(self):
        self.assertEqual(decrypt_vigenere("pztioo", "ab"), "python")

    def test_DifferentCasesDecrypt(self):
        self.assertEqual(decrypt_vigenere("PZTIOO", "ab"), "PYTHON")


if __name__ == '__main__':
    unittest.main()
