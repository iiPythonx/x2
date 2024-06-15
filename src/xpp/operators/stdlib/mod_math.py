# Copyright (c) 2024 iiPython

# Modules
import random
import functools
import operator as op
from typing import List

from xpp.engine import Argument
from xpp.operators import operator

# Handle operators
@operator("add")
def operator_add(*args: List[Argument]) -> int | float | str:
    return functools.reduce(op.add, [a.value for a in args])

@operator("sub")
def operator_sub(*args: List[Argument]) -> int | float:
    return functools.reduce(op.sub, [a.value for a in args])

@operator("mul")
def operator_mul(*args: List[Argument]) -> int | float | str:
    return functools.reduce(op.mul, [a.value for a in args])

@operator("div")
def operator_div(*args: List[Argument]) -> int | float:
    return functools.reduce(op.truediv, [a.value for a in args])

@operator("pow")
def operator_pow(*args: List[Argument]) -> int | float:
    return functools.reduce(op.pow, [a.value for a in args])

@operator("inc")
def operator_inc(object: Argument) -> int | float:
    object.set(object.value + 1)
    return object.value

@operator("dec")
def operator_dec(object: Argument) -> int | float:
    object.set(object.value - 1)
    return object.value

@operator("rng")
def operator_rng(min: Argument, max: Argument) -> int:
    return random.randint(min.value, max.value)

@operator("rnd")
def operator_rnd(object: Argument, places: Argument = None) -> int | float:
    object.set(round(object.value, places and places.value))
    return object.value
