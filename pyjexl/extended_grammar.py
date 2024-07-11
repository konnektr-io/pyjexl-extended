import functools
import json
import re


class ExtendedGrammar:

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
    def concat(list_value):
        return functools.reduce(lambda a, b: a + b, list_value)

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
