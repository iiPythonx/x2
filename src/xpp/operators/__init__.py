# Copyright (c) 2024 iiPython

# Modules
from typing import List
from types import FunctionType

from xpp.engine import Argument

# Handle wrapping
class OperatorWrapper():
    def __init__(self) -> None:
        self.operators = {}

    def operator(self, name: str) -> None:
        def callback(func: FunctionType) -> None:
            self.operators[name] = func
            return func

        return callback

# Handle exporting
wrapper = OperatorWrapper()
operator, operators = wrapper.operator, wrapper.operators

# Testing
@operator("prt")
def operator_prt(*args: List[Argument]) -> None:
    print(*args)

@operator("set")
def operator_set(variable: Argument, data: Argument) -> None:
    variable.set(data)

@operator("add")
def operator_add(*args: List[Argument]) -> int | float | str:
    return sum([a.value for a in args])
