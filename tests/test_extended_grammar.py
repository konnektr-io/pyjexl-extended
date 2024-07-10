import unittest
from pyjexl import JexlExtended


class TestTransformsString(unittest.TestCase):

    def setUp(self) -> None:
        self.jexl = JexlExtended()

    def test_string(self):
        self.assertEqual(self.jexl.evaluate("string(123)"), "123")
        self.assertEqual(self.jexl.evaluate("123456|string"), "123456")
        self.assertEqual(
            self.jexl.evaluate("""{a:123456}|string"""), """{"a":123456}"""
        )
