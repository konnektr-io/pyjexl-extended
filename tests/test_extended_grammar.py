import json
import unittest
from pyjexl import JexlExtended


class JexlExtendedTests(unittest.TestCase):

    def setUp(self) -> None:
        self.jexl = JexlExtended()

    def test_string(self):
        self.assertEqual(self.jexl.evaluate("string(123)"), "123")
        self.assertEqual(self.jexl.evaluate("123456|string"), "123456")
        self.assertEqual(
            self.jexl.evaluate("""{a:123456}|string"""), """{"a":123456}"""
        )

    def test_json_parses_string(self):
        # A string that IS valid JSON still gets parsed, unchanged from before.
        self.assertEqual(self.jexl.evaluate("""'{"a": 1}'|toJson"""), {"a": 1})
        self.assertEqual(self.jexl.evaluate("""json('{"a": 1}')"""), {"a": 1})
        self.assertEqual(self.jexl.evaluate("""'[1, 2, 3]'|toJson"""), [1, 2, 3])
        self.assertEqual(self.jexl.evaluate("""'"hello"'|toJson"""), "hello")

    def test_json_passes_through_structured_values(self):
        # Already-structured values are returned unchanged; no parse attempted.
        self.assertEqual(self.jexl.evaluate("{a: 1}|toJson", {}), {"a": 1})
        self.assertEqual(self.jexl.evaluate("[1, 2, 3]|toJson", {}), [1, 2, 3])
        self.assertEqual(self.jexl.evaluate("42|toJson", {}), 42)
        self.assertEqual(self.jexl.evaluate("3.5|toJson", {}), 3.5)
        self.assertEqual(self.jexl.evaluate("true|toJson", {}), True)
        self.assertEqual(self.jexl.evaluate("false|toJson", {}), False)
        self.assertEqual(self.jexl.evaluate("null|toJson", {}), None)

    def test_json_bool_is_not_treated_as_number(self):
        # bool is a subclass of int in Python: a boolean must pass through as a
        # bool (True/False), never be coerced to 1/0 or parsed.
        self.assertIs(self.jexl.evaluate("true|toJson", {}), True)
        self.assertIs(self.jexl.evaluate("false|toJson", {}), False)
        self.assertIsInstance(self.jexl.evaluate("true|toJson", {}), bool)
        # number() returns a float in this runtime (unchanged, verified on
        # main); what matters is that toJson preserved the boolean as a bool
        # instead of parsing or coercing it to something else.
        self.assertEqual(self.jexl.evaluate("true|toJson|number", {}), 1.0)
        self.assertEqual(self.jexl.evaluate("false|toJson|number", {}), 0.0)
        self.assertEqual(
            self.jexl.evaluate("type(t|toJson)", {"t": True}), "boolean"
        )

    def test_json_passes_through_context_values(self):
        # The realistic pre-validation case: a dict/list already in the context.
        context = {"obj": {"a": 1, "nested": {"b": 2}}, "arr": [1, 2, 3]}
        self.assertEqual(self.jexl.evaluate("obj|toJson", context), {"a": 1, "nested": {"b": 2}})
        self.assertEqual(self.jexl.evaluate("arr|toJson", context), [1, 2, 3])
        # Function-call form with a context value, identical semantics.
        self.assertEqual(self.jexl.evaluate("json(obj)", context), {"a": 1, "nested": {"b": 2}})
        self.assertEqual(self.jexl.evaluate("$json(arr)", context), [1, 2, 3])

    def test_json_non_json_string_still_raises(self):
        # A malformed string must stay a visible error, not silently become a str.
        for expression in ["'hello'|toJson", "json('hello')", "'{bad json}'|parseJson"]:
            with self.assertRaises(json.JSONDecodeError):
                self.jexl.evaluate(expression)

    def test_json_numeric_string_coercion_unchanged(self):
        # Explicitly out of scope: '2026'|toJson() still yields the integer 2026.
        self.assertEqual(self.jexl.evaluate("'2026'|toJson"), 2026)
        self.assertIsInstance(self.jexl.evaluate("'2026'|toJson"), int)

    def test_json_all_aliases_share_the_behaviour(self):
        # Every registered alias, in the form it is actually registered in:
        # json/$json/$parseJson are functions, toJson/parseJson transforms, and
        # parseJson is both. All of them must be off the old path.
        context = {"obj": {"a": 1}}
        for alias in ["json", "$json", "parseJson", "$parseJson"]:
            self.assertEqual(
                self.jexl.evaluate(f"{alias}(obj)", context), {"a": 1}, msg=alias
            )
        for alias in ["toJson", "parseJson"]:
            self.assertEqual(
                self.jexl.evaluate(f"obj|{alias}", context), {"a": 1}, msg=alias
            )
        # ...and each one still parses a valid JSON string.
        for alias in ["json", "$json", "parseJson", "$parseJson"]:
            self.assertEqual(
                self.jexl.evaluate("""%s('{"a": 1}')""" % alias),
                {"a": 1},
                msg=alias,
            )
        for alias in ["toJson", "parseJson"]:
            self.assertEqual(
                self.jexl.evaluate("""'{"a": 1}'|%s""" % alias), {"a": 1}, msg=alias
            )

    def test_json_composes_with_the_grammar(self):
        # Post-pass-through chaining: indexing, length and keys all work.
        self.assertEqual(self.jexl.evaluate("{a: 1}|toJson['a']", {}), 1)
        self.assertEqual(self.jexl.evaluate("obj|toJson['a']", {"obj": {"a": 42}}), 42)
        self.assertEqual(self.jexl.evaluate("obj|parseJson['a']", {"obj": {"a": 42}}), 42)
        self.assertEqual(self.jexl.evaluate("[1, 2, 3]|toJson|length", {}), 3)
        self.assertEqual(
            self.jexl.evaluate("obj|toJson|keys", {"obj": {"a": 1, "b": 2}}),
            ["a", "b"],
        )
        self.assertEqual(
            self.jexl.evaluate("obj|toJson|values", {"obj": {"a": 1}}), [1]
        )
        # A JSON string still parses and then composes the same way.
        self.assertEqual(
            self.jexl.evaluate("""'{"a": 42}'|toJson['a']"""), 42
        )
        # NOTE: the empty-paren form (`x|toJson()`, `x|toJson()['a']`) does not
        # parse in this runtime for ANY transform - `'test'|length()` fails to
        # parse on main too - so it is out of scope here and not asserted.

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
        self.assertEqual(self.jexl.evaluate('trim("__baz--","--")'), "__baz")
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

    def test_form_url_encoded(self):
        self.assertEqual(
            self.jexl.evaluate('{foo:"bar",baz:"tek"}|formUrlEncoded'),
            "foo=bar&baz=tek",
        )

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
        self.assertEqual(self.jexl.evaluate("[4,5,6]|avg"), 5)
        # avg skips None (JEXL skip-nil convention) instead of raising TypeError
        self.assertEqual(self.jexl.evaluate("[1, None, 3]|avg"), 2)
        self.assertEqual(self.jexl.evaluate("[None, None]|avg"), 0.0)

    def test_booleans(self):
        self.assertTrue(self.jexl.evaluate("1|toBoolean"))
        self.assertTrue(self.jexl.evaluate("3|toBoolean"))
        self.assertTrue(self.jexl.evaluate("'1'|toBoolean"))
        self.assertIsNone(self.jexl.evaluate("'2'|toBoolean"))
        self.assertIsNone(self.jexl.evaluate("'a'|toBool"))
        self.assertIsNone(self.jexl.evaluate("''|toBool"))
        self.assertFalse(self.jexl.evaluate("0|toBool"))
        self.assertFalse(self.jexl.evaluate("0.0|toBool"))
        self.assertFalse(self.jexl.evaluate("'false'|toBool"))
        self.assertFalse(self.jexl.evaluate("'False'|toBool"))
        self.assertFalse(self.jexl.evaluate("'fALSE'|toBool"))
        self.assertTrue(self.jexl.evaluate("'tRUE       '|toBoolean"))
        self.assertTrue(self.jexl.evaluate("'False'|toBool|not"))
        self.assertFalse(self.jexl.evaluate("'TRUE'|toBool|not"))

    def test_arrays(self):
        self.assertEqual(
            self.jexl.evaluate('["foo", "bar", "baz"]|append("tek")'),
            ["foo", "bar", "baz", "tek"],
        )
        self.assertEqual(
            self.jexl.evaluate('["foo", "bar"]|append(["baz","tek"])'),
            ["foo", "bar", "baz", "tek"],
        )
        self.assertEqual(
            self.jexl.evaluate('"foo"|append(["bar", "baz","tek"])'),
            ["foo", "bar", "baz", "tek"],
        )
        self.assertEqual(
            self.jexl.evaluate('"foo"|append("bar", "baz","tek")'),
            ["foo", "bar", "baz", "tek"],
        )
        self.assertEqual(
            self.jexl.evaluate('["tek", "baz", "bar", "foo"]|reverse'),
            ["foo", "bar", "baz", "tek"],
        )
        self.assertEqual(
            self.jexl.evaluate('["tek", "baz", "bar", "foo", "foo"]|reverse|distinct'),
            ["foo", "bar", "baz", "tek"],
        )
        self.assertEqual(
            self.jexl.evaluate("{foo:0, bar:1, baz:2, tek:3}|keys"),
            ["foo", "bar", "baz", "tek"],
        )
        self.assertEqual(
            self.jexl.evaluate('{a:"foo", b:"bar", c:"baz", d:"tek"}|values'),
            ["foo", "bar", "baz", "tek"],
        )
        self.assertEqual(
            self.jexl.evaluate(
                '[{name:"foo"}, {name:"bar"}, {name:"baz"}, {name:"tek"}]|mapField("name")'
            ),
            ["foo", "bar", "baz", "tek"],
        )
        self.assertEqual(
            self.jexl.evaluate(
                '[{name:"tek",age:32}, {name:"bar",age:34}, {name:"baz",age:33}, {name:"foo",age:35}]|sort("age",true)|mapField("name")'
            ),
            # sort(field, true) = DESCENDING, matching the C# flow engine
            ["foo", "bar", "baz", "tek"],
        )
        self.assertEqual(
            self.jexl.evaluate('["foo"]|append(["tek","baz","bar"]|sort)'),
            ["foo", "bar", "baz", "tek"],
        )
        # First-match bracket property: `arr[.cond].prop` resolves `.prop`
        # against the FIRST element of the filtered array (JS/C# parity)
        self.assertEqual(
            self.jexl.evaluate(
                "arr[.age>34].name",
                {"arr": [{"name": "bar", "age": 34}, {"name": "foo", "age": 35}]},
            ),
            "foo",
        )
        self.assertEqual(
            self.jexl.evaluate(
                "arr[.age<=34][0].name",
                {"arr": [{"name": "bar", "age": 34}, {"name": "foo", "age": 35}]},
            ),
            "bar",
        )
        # Property access on a plain array resolves against its first element
        self.assertEqual(
            self.jexl.evaluate(
                "arr.name",
                {"arr": [{"name": "bar", "age": 34}, {"name": "foo", "age": 35}]},
            ),
            "bar",
        )
        # Filtering an undefined subject yields [] (JS parity), not a crash
        self.assertEqual(
            self.jexl.evaluate("missing[.age>34]", {}),
            [],
        )
        self.assertEqual(
            self.jexl.evaluate(
                '["foo"]|append(["tek", "baz", "bar", "foo", "foo"]|filter("value != \'foo\'")|sort)'
            ),
            ["foo", "bar", "baz", "tek"],
        )

    def test_map(self):
        context = {
            "assoc": [
                {"lastName": "Archer", "age": 32},
                {"lastName": "Poovey", "age": 34},
                {"lastName": "Figgis", "age": 45},
            ]
        }
        self.assertEqual(
            self.jexl.evaluate(
                '[{name:"foo"}, {name:"bar"}, {name:"baz"}, {name:"tek"}]|map("value.name")'
            ),
            ["foo", "bar", "baz", "tek"],
        )
        self.assertEqual(
            self.jexl.evaluate(
                '[{name:"tek",age:32}, {name:"bar",age:34}, {name:"baz",age:33}, {name:"foo",age:35}]|map("value.age")'
            ),
            [32, 34, 33, 35],
        )
        self.assertEqual(
            self.jexl.evaluate("assoc|map('value.age')", context),
            [32, 34, 45],
        )
        self.assertEqual(
            self.jexl.evaluate("assoc|map('value.lastName')", context),
            ["Archer", "Poovey", "Figgis"],
        )
        self.assertEqual(
            self.jexl.evaluate("assoc|map('value.age + index')", context),
            [32, 35, 47],
        )
        self.assertEqual(
            self.jexl.evaluate(
                "assoc|map('value.age + array[.age <= value.age][0].age + index')",
                context,
            ),
            [64, 67, 79],
        )
        self.assertEqual(
            self.jexl.evaluate("assoc|map('value.age')|avg", context),
            37,
        )

    def test_any_all(self):
        context = {
            "assoc": [
                {"lastName": "Archer", "age": 32},
                {"lastName": "Poovey", "age": 34},
                {"lastName": "Figgis", "age": 45},
            ]
        }
        self.assertTrue(
            self.jexl.evaluate(
                '[{name:"foo"}, {name:"bar"}, {name:"baz"}, {name:"tek"}]|any("value.name==\'foo\'")'
            )
        )
        self.assertTrue(self.jexl.evaluate("assoc|every('value.age>30')", context))
        self.assertFalse(self.jexl.evaluate("assoc|every('value.age>40')", context))
        self.assertTrue(self.jexl.evaluate("assoc|some('value.age>40')", context))
        self.assertTrue(
            self.jexl.evaluate(
                "assoc|some('value.lastName==''Figgis''')", context
            )
        )
        self.assertTrue(
            self.jexl.evaluate("assoc|map('value.age')|some('value>30')", context)
        )

    def test_reduce(self):
        context = {
            "assoc": [
                {"lastName": "Archer", "age": 32},
                {"lastName": "Poovey", "age": 34},
                {"lastName": "Figgis", "age": 45},
            ]
        }
        self.assertEqual(
            self.jexl.evaluate("assoc|reduce('accumulator + value.age', 0)", context),
            111,
        )
        self.assertEqual(
            self.jexl.evaluate(
                "assoc|reduce('(value.age > array|map(\"value.age\")|avg) ? accumulator|append(value.age) : accumulator', [])",
                context,
            ),
            [45],
        )
        self.assertEqual(
            self.jexl.evaluate(
                "assoc|reduce('(value.age < array|map(\"value.age\")|avg) ? accumulator|append(value.age) : accumulator', [])[1]",
                context,
            ),
            34,
        )

    def test_objects(self):
        self.assertEqual(
            self.jexl.evaluate("$merge({foo:'bar'},{baz:'tek'})"),
            {"foo": "bar", "baz": "tek"},
        )
        self.assertEqual(
            self.jexl.evaluate("{foo:'bar'}|merge({baz:'tek'})"),
            {"foo": "bar", "baz": "tek"},
        )
        self.assertEqual(
            self.jexl.evaluate("[{foo:'bar'},{baz:'tek'}]|merge"),
            {"foo": "bar", "baz": "tek"},
        )
        self.assertEqual(
            self.jexl.evaluate("[{foo:'bar'}]|merge([{baz:'tek'}])"),
            {"foo": "bar", "baz": "tek"},
        )
        self.assertEqual(
            self.jexl.evaluate('[["foo","bar"],["baz","tek"]]|toObject'),
            {"foo": "bar", "baz": "tek"},
        )
        self.assertEqual(
            self.jexl.evaluate('["foo","bar"]|toObject(true)'),
            {"foo": True, "bar": True},
        )
        self.assertEqual(
            self.jexl.evaluate('["a","b","c"]|toObject(true)'),
            {"a": True, "b": True, "c": True},
        )

    def test_convert_time_zone(self):
        # Windows timezone
        self.assertEqual(
            self.jexl.evaluate(
                "'2025-11-26T12:00:00Z'|convertTimeZone('Pacific Standard Time')"
            ),
            "2025-11-26T04:00:00.0000000-08:00",
        )
        self.assertEqual(
            self.jexl.evaluate(
                "'2025-06-26T12:00:00Z'|convertTimeZone('Pacific Standard Time')"
            ),
            "2025-06-26T05:00:00.0000000-07:00",
        )
        # IANA timezone
        self.assertEqual(
            self.jexl.evaluate(
                "'2025-06-26T12:00:00Z'|convertTimeZone('Europe/Amsterdam')"
            ),
            "2025-06-26T14:00:00.0000000+02:00",
        )
        self.assertEqual(
            self.jexl.evaluate("'2025-11-26T12:00:00Z'|convertTimeZone('UTC')"),
            "2025-11-26T12:00:00.0000000+00:00",
        )
        # Fixed offsets
        self.assertEqual(
            self.jexl.evaluate("'2025-11-26T12:00:00Z'|convertTimeZone('+02:00')"),
            "2025-11-26T14:00:00.0000000+02:00",
        )
        self.assertEqual(
            self.jexl.evaluate("'2025-06-26T12:00:00Z'|convertTimeZone('-08:00')"),
            "2025-06-26T04:00:00.0000000-08:00",
        )
        self.assertEqual(
            self.jexl.evaluate("'2025-12-26T12:00:00Z'|convertTimeZone('-08:00')"),
            "2025-12-26T04:00:00.0000000-08:00",
        )
