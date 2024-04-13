# Copyright (c) 2024 iiPython

# Modules
from typing import Any

# Main argument class
class Argument():
    def __init__(self, engine: object, type_: str, value: Any, *extra) -> None:
        self.engine, self.type, self.value = engine, type_, value

    def __str__(self) -> str:
        return str(self.value)
