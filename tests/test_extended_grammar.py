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

    def test_length(self):
        self.assertEqual(self.jexl.evaluate("'test123'|length"), 7)
        self.assertEqual(self.jexl.evaluate('["a",1,"b"]|length'), 3)
        self.assertEqual(self.jexl.evaluate('$length(["a",1,"b"])'), 3)
        self.assertEqual(self.jexl.evaluate("""{a:1,b:2,c:3}|length"""), 3)

    def test_substring(self):
        self.assertEqual(self.jexl.evaluate("substring(123456,2,2)"), "34")
        self.assertEqual(self.jexl.evaluate("$substring('test',(-2))"), "st")
        self.assertEqual(
            self.jexl.evaluate("$substring($string({a:123456}, true),0,1)"), "{"
        )

    def test_substring_before(self):
        self.assertEqual(
            self.jexl.evaluate('"hello world"|substringBefore(" ")'), "hello"
        )
        self.assertEqual(
            self.jexl.evaluate('substringBefore("hello world", "o")'), "hell"
        )
        self.assertEqual(
            self.jexl.evaluate('substringBefore("hello world", "x")'), "hello world"
        )
        self.assertEqual(self.jexl.evaluate("substringBefore(123456,2)"), "1")

    def test_substring_after(self):
        self.assertEqual(
            self.jexl.evaluate('"hello world"|substringAfter(" ")'), "world"
        )
        self.assertEqual(
            self.jexl.evaluate('substringAfter("hello world", "o")'), " world"
        )
        self.assertEqual(self.jexl.evaluate('substringAfter("hello world", "x")'), "")
        self.assertEqual(self.jexl.evaluate("substringAfter(123456,2)"), "3456")

    def test_uppercase(self):
        self.assertEqual(self.jexl.evaluate('uppercase("hello world")'), "HELLO WORLD")
        self.assertEqual(self.jexl.evaluate("uppercase(123456)"), "123456")
        self.assertEqual(self.jexl.evaluate("'baz'|uppercase"), "BAZ")

    def test_lowercase(self):
        self.assertEqual(self.jexl.evaluate('lowercase("HELLO WORLD")'), "hello world")
        self.assertEqual(self.jexl.evaluate("lowercase(123456)"), "123456")
        self.assertEqual(self.jexl.evaluate('$lowercase("FOObar")'), "foobar")
        self.assertEqual(self.jexl.evaluate('"FOObar"|lower'), "foobar")

    def test_camel_pascal_case(self):
        self.assertEqual(self.jexl.evaluate("'foo bar '|camelCase"), "fooBar")
        self.assertEqual(self.jexl.evaluate('$camelCase("Foo_bar")'), "fooBar")
        self.assertEqual(self.jexl.evaluate("'FooBar'|toCamelCase"), "fooBar")
        self.assertEqual(self.jexl.evaluate("'Foo-bar'|toCamelCase"), "fooBar")
        self.assertEqual(self.jexl.evaluate("'foo bar'|toPascalCase"), "FooBar")
        self.assertEqual(self.jexl.evaluate("'fooBar'|toPascalCase"), "FooBar")
        self.assertEqual(self.jexl.evaluate("'Foo_bar'|toPascalCase"), "FooBar")

    def test_trim_pad(self):
        self.assertEqual(self.jexl.evaluate('trim(" baz  ")'), "baz")
        self.assertEqual(self.jexl.evaluate('trim("  baz  ")'), "baz")
        self.assertEqual(self.jexl.evaluate('pad("foo",5)'), "foo  ")
        self.assertEqual(self.jexl.evaluate('pad("foo",-5,0)'), "00foo")

    def test_contains(self):
        self.assertTrue(self.jexl.evaluate("'foo-bar'|contains('bar')"))
        self.assertFalse(self.jexl.evaluate("'foo-bar'|contains('baz')"))
        self.assertFalse(self.jexl.evaluate('["foo-bar"]|contains("bar")'))
        self.assertTrue(self.jexl.evaluate('["foo-bar"]|contains("foo-bar")'))
        self.assertTrue(self.jexl.evaluate('["baz", "foo", "bar"]|contains("bar")'))
