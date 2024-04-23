# Copyright (c) 2024 iiPython

# Modules
import time
from typing import Any, List

from xpp.engine import Argument
from xpp.operators import operator

# Handle operators
@operator("prt")
def operator_prt(*args: List[Argument]) -> None:
    print(*args)

@operator("set")
def operator_set(variable: Argument, data: Argument) -> None:
    variable.set(data)

@operator("ret")
def operator_ret(return_value: Argument) -> Any:
    return_value.engine.stack[-1]["return"] = return_value.value
    return return_value.value

@operator("jmp")
def operator_jmp(target: Argument, *args: List[Argument]) -> Any:
    class_, method_ = target.class_, target.name
    if "." in target.name:
        class_, method_ = target.name.split(".")

    return target.engine.execute_method(class_, method_, [x.value for x in args])

@operator("ext")
def operator_ext(code: Argument = None) -> None:
    exit(code.value if code is not None else 1)

@operator("cls")
def operator_cls() -> None:
    print("\033c\033[3J", end = "")

@operator("inp")
def operator_inp(prompt: Argument = None) -> str:
    return input(prompt.value if prompt is not None else "")

@operator("thw")
def operator_thw(message: Argument = None) -> None:
    raise Exception(message.value if message else "exception thrown in xpp thread")

@operator("hlt")
def operator_hlt(delay: Argument) -> None:
    time.sleep(delay.value)
