import functools
import json


class ExtendedGrammar:

    @staticmethod
    def to_string(value):
        if isinstance(value, (dict, list)):
            value = json.dumps(value, separators=(",", ":"))
        return str(value)

    @staticmethod
    def concat(list_value):
        return functools.reduce(lambda a, b: a + b, list_value)
