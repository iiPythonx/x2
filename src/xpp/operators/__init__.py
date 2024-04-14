# Copyright (c) 2024 iiPython

# Modules
from typing import Any, List
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

@operator("ret")
def operator_ret(return_value: Argument) -> Any:
    return_value.engine.stack[-1]["return"] = return_value.value
    return return_value.value

@operator("jmp")
def operator_jmp(target: Argument, *args: List[Argument]) -> Any:
    return target.engine.execute_method(method_ = target.name, args = [x.value for x in args])
