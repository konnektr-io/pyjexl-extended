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

    def test_split(self):
        self.assertEqual(self.jexl.evaluate('split("foo-bar", "-")'), ["foo", "bar"])
        self.assertEqual(self.jexl.evaluate('split("foo-bar", "-")[1]'), "bar")
        self.assertEqual(self.jexl.evaluate('split("foo-bar", "-")[0]'), "foo")
        self.assertEqual(
            self.jexl.evaluate('split("foo-bar", "-")[0]|uppercase'), "FOO"
        )
        self.assertEqual(
            self.jexl.evaluate('split("foo-bar", "-")[1]|lowercase'), "bar"
        )
        self.assertEqual(
            self.jexl.evaluate('split("foo-bar", "-")[1]|substring(0,1)'), "b"
        )

    def test_join(self):
        self.assertEqual(self.jexl.evaluate('join(["foo", "bar"], "-")'), "foo-bar")
        self.assertEqual(self.jexl.evaluate('join(["foo", "bar"], "")'), "foobar")
        self.assertEqual(self.jexl.evaluate('["foo", "bar"]|join'), "foo,bar")
        # self.assertEqual(
        #     self.jexl.evaluate('"f,b,a,d,e,c"|split(",")|sort|join'), "a,b,c,d,e,f"
        # )
        # self.assertEqual(
        #     self.jexl.evaluate('"f,b,a,d,e,c"|split(",")|sort|join("")'), "abcdef"
        # )

    def test_replace(self):
        self.assertEqual(self.jexl.evaluate('replace("foo-bar", "-", "_")'), "foo_bar")
        self.assertEqual(self.jexl.evaluate('replace("foo-bar---", "-", "")'), "foobar")
        self.assertEqual(
            self.jexl.evaluate('"123ab123ab123ab"|replace("123")'), "ababab"
        )

    def test_base64(self):
        self.assertEqual(self.jexl.evaluate('base64Encode("foobar")'), "Zm9vYmFy")
        self.assertEqual(self.jexl.evaluate('base64Decode("Zm9vYmFy")'), "foobar")

    def test_number(self):
        self.assertEqual(self.jexl.evaluate('$number("1")'), 1)
        self.assertEqual(self.jexl.evaluate('$number("1.1")'), 1.1)
        self.assertEqual(self.jexl.evaluate('$number("-1.1")'), -1.1)
        self.assertEqual(self.jexl.evaluate("$number(-1.1)"), -1.1)
        self.assertEqual(self.jexl.evaluate("$number(-1.1)|floor"), -2)
        self.assertEqual(self.jexl.evaluate('$number("10.6")|ceil'), 11)
        self.assertEqual(self.jexl.evaluate("10.123456|round(2)"), 10.12)
        self.assertEqual(self.jexl.evaluate("10.123456|toInt"), 10)
        self.assertEqual(self.jexl.evaluate('"10.123456"|toInt'), 10)
        self.assertEqual(self.jexl.evaluate("'16325'|toInt"), 16325)
        self.assertEqual(self.jexl.evaluate("(9/2)|toInt"), 4)
        self.assertEqual(self.jexl.evaluate("3|power(2)"), 9)
        self.assertEqual(self.jexl.evaluate("3|power"), 9)
        self.assertEqual(self.jexl.evaluate("9|sqrt"), 3)
        self.assertEqual(self.jexl.evaluate("random() < 1"), True)

    def test_formatting(self):
        self.assertEqual(
            self.jexl.evaluate('16325.62|formatNumber("0,0.000")'), "16,325.620"
        )
        self.assertEqual(
            self.jexl.evaluate('16325.62|formatNumber("0.000")'), "16325.620"
        )
        self.assertEqual(self.jexl.evaluate("12|formatBase(16)"), "c")
        self.assertEqual(
            self.jexl.evaluate('16325.62|formatInteger("0000000")'), "0016325"
        )

    def test_numeric_aggregations(self):
        self.assertEqual(self.jexl.evaluate("[1,2,3]|sum"), 6)
        self.assertEqual(self.jexl.evaluate("sum(1,2,3,4,5)"), 15)
        self.assertEqual(self.jexl.evaluate("[1,3]|sum(1,2,3,4,5)"), 19)
        self.assertEqual(self.jexl.evaluate("[1,3]|sum([1,2,3,4,5])"), 19)
        self.assertEqual(self.jexl.evaluate("[1,3]|max([1,2,3,4,5])"), 5)
        self.assertEqual(self.jexl.evaluate("[2,3]|min([1,2,3,4,5])"), 1)
        self.assertEqual(self.jexl.evaluate("[2,3]|min(1,2,3,4,5)"), 1)
        # self.assertEqual(self.jexl.evaluate('[4,5,6]|avg'), 5)
