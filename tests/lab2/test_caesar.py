import unittest
from src.lab2.caesar import encrypt_caesar
class CaesarTestCase(unittest.TestCase):
    def OnlyUpperCase(self):
        self.assertEquals(encrypt_caesar("PYTHON"), "SBWKRQ")

    def OnlyLowerCase(self):
        self.assertEquals(encrypt_caesar("python"), "sbwkrq")

    def PlaintextWithAnotherSymbols(self):
        self.assertEquals(encrypt_caesar("Python3.6"),"'Sbwkrq3.6'")
