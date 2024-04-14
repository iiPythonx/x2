# Copyright (c) 2024 iiPython

# Modules
from typing import Any

# Main argument class
class Argument():
    def __init__(self, engine: object, type_: str, value: Any, *extra) -> None:
        self.engine, self.type, self.name, self.value = engine, type_, value, value
        if self.type == "ref":
            if isinstance(self.value, list):
                self.name, self.value = None, engine.execute_line(self.value)

            else:
                self.set(self.engine.stack[-1]["variables"].get(self.value))

    def __str__(self) -> str:
        return str(self.value)
    
    def __repr__(self) -> str:
        return f"<Argument T='{self.type}' N='{self.name}' V={repr(self.value)} />"

    def set(self, value: Any) -> None:
        if isinstance(value, Argument):
            value = value.value

        self.value = value
        self.engine.stack[-1]["variables"][self.name] = value
