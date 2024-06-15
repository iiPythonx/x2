# Copyright (c) 2024 iiPython

# Modules
from typing import Any

from xpp.engine import Argument
from xpp.operators import operator

# Initialization
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

def evaluate_expression(engine: object, expr: list) -> Any:
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
            stack.append(item[1] if item[0] == "lit" else Argument(engine, *item).value)

    if len(stack) == 1:
        return stack[0]

    return comp(*stack)
    
# Handle operators
@operator("if")
def operator_if(expression: Argument, branch: Argument, *args) -> None:
    engine, expressions = expression.engine, [expression, branch, *args]
    for expr in [expressions[i:i + 2] for i in range(0, len(expressions), 2)]:
        if len(expr) == 1:  # This is an else branch
            engine.execute_line(expr[0].value)
            break

        elif evaluate_expression(engine, expr[0].value):
            engine.execute_line(expr[1].value)
            break

@operator("try")
def operator_try(expression: Argument, branch: Argument = None) -> None:
    engine = expression.engine
    if branch is None:
        engine.execute_line(expression.value)

    else:
        try:
            engine.execute_line(expression.value)

        except Exception:
            engine.execute_line(branch.value)

@operator("rep")
def operator_rep(amount: Argument, expression: Argument) -> None:
    for _ in range(amount.value):
        amount.engine.execute_line(expression.value)

@operator("whl")
def operator_whl(expression: Argument, branch: Argument) -> None:
    engine = expression.engine
    while evaluate_expression(engine, expression.value):
        expression.engine.execute_line(branch.value)
        expression.refresh()
