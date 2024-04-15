# Copyright (c) 2024 iiPython

# Modules
from typing import Any, List, Tuple

from .argument import Argument

# Engine class
# Handles everything execution related in the language
class ExecutionEngine():
    def __init__(self, tokens: dict) -> None:
        self.stack = []
        self.classes = tokens["classes"]

    def execute_line(self, line: List[Tuple[str, Any]]) -> Any:
        return line[0][1](*[Argument(self, *arg) for arg in line[1:]])

    def execute_method(self, class_: str = "_global", method_: str = "_main", args: List[Any] = []) -> None:
        self.stack.append(self.classes[class_]["methods"][method_])
        self.stack[-1] = self.stack[-1] | {"class": class_, "method": method_, "return": None}

        for index, key in enumerate(self.stack[-1]["args"]):
            self.stack[-1]["variables"][key] = args[index]

        for idx, line in enumerate(self.stack[-1]["lines"]):
            self.execute_line(line)
            self.stack[-1]["index"] = idx

        return self.stack.pop()["return"]
