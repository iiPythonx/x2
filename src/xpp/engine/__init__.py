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

        # Default data
        self.active_method = None

    def execute_line(self, line: List[Tuple[str, Any]]) -> Any:
        return line[0][1](*[Argument(self, *arg) for arg in line[1:]])

    def execute_method(self, class_: str = "_global", method_: str = "_main", args: List[Tuple[str, Any]] = []) -> None:
        self.active_method = self.classes[class_]["methods"][method_]
        for index, key in enumerate(self.active_method["args"]):
            self.active_method["variables"][key] = args[index]

        for line in self.active_method["lines"]:
            self.execute_line(line)