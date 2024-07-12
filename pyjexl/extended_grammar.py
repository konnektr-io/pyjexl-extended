import functools
import json
import math
import random
import re
import base64


class ExtendedGrammar:
    """String functions"""

    @staticmethod
    def to_string(value, prettify=False):
        if isinstance(value, (dict, list)):
            value = (
                json.dumps(value)
                if prettify
                else json.dumps(value, separators=(",", ":"))
            )
        return str(value)

    @staticmethod
    def length(value):
        return len(value)

    @staticmethod
    def substring(value: any, start: int, length: int = None):
        if not isinstance(value, str):
            value = ExtendedGrammar.to_string(value)
        fin = start + length if length else len(value)
        return value[start:fin]

    @staticmethod
    def substring_before(value: any, chars: any):
        if not isinstance(value, str):
            value = ExtendedGrammar.to_string(value)
        if not isinstance(chars, str):
            chars = ExtendedGrammar.to_string(chars)
        index = value.find(chars)
        if index == -1:
            return value
        return value[:index]

    @staticmethod
    def substring_after(value: any, chars: any):
        if not isinstance(value, str):
            value = ExtendedGrammar.to_string(value)
        if not isinstance(chars, str):
            chars = ExtendedGrammar.to_string(chars)
        index = value.find(chars)
        if index == -1:
            return ""
        ini = index + len(chars)
        return value[ini:]

    @staticmethod
    def uppercase(value):
        return ExtendedGrammar.to_string(value).upper()

    @staticmethod
    def lowercase(value):
        return ExtendedGrammar.to_string(value).lower()

    @staticmethod
    def camel_case(value):
        value = ExtendedGrammar.to_string(value)
        value = re.sub(
            r"(?<!^)(?=[A-Z])|[`~!@#%^&*()|+\\\-=?;:'.,\s_']+", "_", value
        ).lower()
        parts = value.split("_")
        camel_case_value = parts[0] + "".join(x.title() for x in parts[1:])
        return camel_case_value

    @staticmethod
    def pascal_case(value):
        value = ExtendedGrammar.to_string(value)
        value = re.sub(
            r"(?<!^)(?=[A-Z])|[`~!@#%^&*()|+\\\-=?;:'.,\s_']+", "_", value
        ).lower()
        parts = value.split("_")
        camel_case_value = "".join(x.title() for x in parts)
        return camel_case_value

    @staticmethod
    def trim(value):
        return ExtendedGrammar.to_string(value).strip()

    @staticmethod
    def pad(value, width, char=" "):
        value = ExtendedGrammar.to_string(value)
        if not isinstance(char, str):
            char = str(char)
        if width > 0:
            return value.ljust(width, char)
        else:
            return value.rjust(-width, char)

    @staticmethod
    def contains(value, search):
        return search in value

    @staticmethod
    def split(value: str, sep=","):
        return value.split(sep)

    @staticmethod
    def join(value, sep=","):
        return sep.join(value)

    @staticmethod
    def replace(value: str, search: str, replace=""):
        return value.replace(search, replace)

    @staticmethod
    def base64_encode(input: str):
        return base64.b64encode(input.encode("utf-8")).decode("utf-8")

    @staticmethod
    def base64_decode(input: str):
        return base64.b64decode(input.encode("utf-8")).decode("utf-8")

    """Number functions"""

    @staticmethod
    def to_number(value):
        return float(value)

    @staticmethod
    def to_int(value):
        if isinstance(value, str):
            value = value.strip('"')
        return int(float(value))

    @staticmethod
    def abs(value):
        return abs(value)

    @staticmethod
    def floor(value):
        return math.floor(value)

    @staticmethod
    def ceil(value):
        return math.ceil(value)

    @staticmethod
    def round(value, precision=0):
        return round(value, precision)

    @staticmethod
    def power(value, power=2):
        return math.pow(value, power)

    @staticmethod
    def sqrt(value):
        return math.sqrt(value)

    @staticmethod
    def random():
        return random.random()

    @staticmethod
    def format_number(value, precision=2):
        return "{:.{}f}".format(value, precision)

    @staticmethod
    def format_base(value, base=10):
        return format(value, "0" + str(base) + "d")

    @staticmethod
    def format_integer(value, base=10):
        return int(value, base)

    @staticmethod
    def sum(value, *rest):
        if not isinstance(value, list):
            value = [value]
        rest = [v for v in rest]
        if len(rest) > 0 and isinstance(rest[0], list):
            rest = [v for va in rest for v in va]
        values = value + rest
        return sum(values)

    @staticmethod
    def max(value, *rest):
        if not isinstance(value, list):
            value = [value]
        rest = [v for v in rest]
        if len(rest) > 0 and isinstance(rest[0], list):
            rest = [v for va in rest for v in va]
        values = value + rest
        return max(values)

    @staticmethod
    def min(value, *rest):
        if not isinstance(value, list):
            value = [value]
        rest = [v for v in rest]
        if len(rest) > 0 and isinstance(rest[0], list):
            rest = [v for va in rest for v in va]
        values = value + rest
        return min(values)

    """ Array functions """

    @staticmethod
    def array_append(list_value):
        return functools.reduce(lambda a, b: a + b, list_value)
