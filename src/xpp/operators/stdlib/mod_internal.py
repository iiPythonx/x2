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
    return target.engine.execute_method(method_ = target.name, args = [x.value for x in args])

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

# Handle comparisons
class ExpressionError(Exception):
    pass

comparisons = {
    "==": lambda a, b: a == b,
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    "!=": lambda a, b: a != b,
    "||": lambda a, b: a or b,
    "&&": lambda a, b: a and b,
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b
}

@operator("if")
def operator_if(expression: Argument, branch: Argument, *args) -> None:
    def evaluate_expression(expr: list) -> Any:
        if any([isinstance(x[1], list) for x in expr]):
            object = []
            for item in expr:
                if isinstance(item[1], list):
                    object.append(("lit", evaluate_expression(item[1])))

                else:
                    object.append(item)

            expr = object

        stack, comp = [], None
        for index, item in enumerate(expr):
            if index > 3 or (item[1] in comparisons and index != 1):
                raise ExpressionError("xpp only supports three-way expressions (value comp value) in its current state")

            elif index == 1:
                if item[1] not in comparisons:
                    raise ExpressionError("unknown comparison operator")
                
                comp = comparisons[item[1]]

            else:
                stack.append(item[1] if item[0] == "lit" else Argument(expression.engine, *item).value)

        if len(stack) == 1:
            return stack[0]

        return comp(*stack)

    expressions = [expression, branch, *args]
    for expr in [expressions[i:i + 2] for i in range(0, len(expressions), 2)]:
        if len(expr) == 1:  # This is an else branch
            expression.engine.execute_line(expr[0].value)
            break

        elif evaluate_expression(expr[0].value):
            expression.engine.execute_line(expr[1].value)
            break
