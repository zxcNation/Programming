import unittest
from src.lab2.vigenre import encrypt_vigenere

class VigenreTestCase(unittest.TestCase):
    def test_OnlyUpperCase(self):
        self.assertEqual(encrypt_vigenere("ATTACKATDAWN", "LEMON"), "LXFOPVEFRNHR")

    def test_OnlyLowerCase(self):
        self.assertEqual(encrypt_vigenere("python", "ab"), "pztioo")

    def test_DifferentCases(self):
        self.assertEqual(encrypt_vigenere("PYTHON", "ab"), "PZTIOO")

