# Copyright (c) 2024 iiPython

# Modules
from typing import Any, List

from xpp.engine import Argument
from xpp.operators import operator

# Middlemen functions
def convert_type(args: List[Argument], type_: Any) -> Any | List[Any]:
    results = [a.set(type_(a.value)) for a in args]
    return results if len(results) > 1 else results[0]

# Handle operators
@operator("int")
def operator_int(*args: List[Argument]) -> int | List[int]:
    return convert_type(args, int)

@operator("str")
def operator_str(*args: List[Argument]) -> str | List[str]:
    return convert_type(args, str)

@operator("flt")
def operator_flt(*args: List[Argument]) -> float | List[float]:
    return convert_type(args, float)

@operator("chr")
def operator_chr(string: Argument, index: Argument, stop: Argument = None) -> str:
    return string.value[index.value:(stop.value if stop is not None else index.value + 1)]

@operator("idx")
def operator_idx(string: Argument, substr: Argument) -> int:
    return string.value.index(substr.value)

@operator("len")
def operator_len(string: Argument) -> int:
    return len(string.value)

@operator("lwr")
def operator_lwr(string: Argument) -> str:
    string.set(string.value.lower())
    return string.value

@operator("upr")
def operator_upr(string: Argument) -> str:
    string.set(string.value.upper())
    return string.value

@operator("cap")
def operator_cap(string: Argument) -> str:
    string.set(string.value.capitalize())
    return string.value

