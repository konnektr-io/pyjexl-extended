from .jexl import JEXL
from .extended_grammar import ExtendedGrammar
import random
import datetime
import math
import functools

from datetime import timezone


class JexlExtended(JEXL):
    def __init__(self, context=None):
        super().__init__(context=context)

        super().add_function("string", ExtendedGrammar.to_string)
        super().add_function("$string", ExtendedGrammar.to_string)
        super().add_transform("toString", ExtendedGrammar.to_string)
        super().add_transform("string", ExtendedGrammar.to_string)
        super().add_function("length", len)
        super().add_function("$length", len)
        super().add_transform("length", len)
        super().add_transform("uppercase", lambda x: str(x).upper())
        super().add_transform("lowercase", lambda x: str(x).lower())
        super().add_transform("substring", lambda x, ini, fin: x[ini:fin])
        super().add_transform("includes", lambda x, str: str in x)

        super().add_transform("floor", lambda x: math.floor(x))

        super().add_transform("parseInt", lambda x: int(x))
        super().add_transform("parseFloat", lambda x: float(x))

        super().add_function(
            "now",
            lambda x: self.now().strftime("%Y-%m-%dT%H:%M:%S") + ".000Z",
        )
        super().add_function(
            "$now",
            lambda x: self.now().strftime("%Y-%m-%dT%H:%M:%S") + ".000Z",
        )
        super().add_function(
            "toDateTime", lambda date: date.strftime("%Y-%m-%dT%H:%M:%S") + ".000Z"
        )
        super().add_function(
            "$toDateTime", lambda date: date.strftime("%Y-%m-%dT%H:%M:%S") + ".000Z"
        )

        super().add_transform("random", lambda ini, end: random.randrange(ini, end))
        super().add_transform("rndFloat", lambda ini, end: random.uniform(ini, end))
        super().add_transform("round", lambda x, decimals: round(x, decimals))


""" 
        # Tested by test_transforms_list.py
        super().add_transform("next", lambda x, arr: arr[(arr.index(x) + 1) % len(arr)])
        super().add_transform("indexOf", lambda x, str: x.index(str))
        super().add_transform(
            "rndList",
            lambda init, end, length: [
                random.randrange(init, end) for _ in range(length)
            ],
        )
        super().add_transform(
            "rndFloatList",
            lambda ini, end, length: [random.uniform(ini, end) for _ in range(length)],
        )
        super().add_transform("zipStringList", zipStrList)
        super().add_transform(
            "concatList",
            lambda list_value: functools.reduce(lambda a, b: a + b, list_value),
        )

        # Tested by test_transforms_date.py
        super().add_transform("currentTime", lambda x: self.now())
        super().add_transform(
            "currentTimeIso",
            lambda x: self.now().strftime("%Y-%m-%dT%H:%M:%S") + ".000Z",
        )
        super().add_transform(
            "toIsoString", lambda date: date.strftime("%Y-%m-%dT%H:%M:%S") + ".000Z"
        )
        super().add_transform(
            "currentTimeFormat", lambda x, string: self.now().strftime(string)
        )
        super().add_transform("timeFormat", lambda date, string: date.strftime(string))
        super().add_transform("currentHour24", lambda x: int(self.now().hour))
        super().add_transform("currentDay", lambda x: int(self.now().day))

        # Tested by test_transforms_interpolation.py
        super().add_transform(
            "interpolate",
            lambda step, ini, end, nSteps: ((end - ini) * (step % nSteps)) / nSteps,
        )

        # Tested by test_transforms_misc.py
        super().add_transform("typeOf", lambda x: f"{type(x)}"[8:-2])
        super().add_transform(
            "strToLocation", lambda str: [float(x) for x in str.split(",")]
        )

        # Tested by test_null.py
        super().add_transform("nullSafe", lambda x, y: x if x is not None else y) """
