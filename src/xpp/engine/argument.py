# Copyright (c) 2024 iiPython

# Modules
from typing import Any

# Main argument class
class Argument():
    def __init__(self, engine: object, type_: str, value: Any) -> None:
        self.engine, self.type, self.name, self.value = engine, type_, value, value

        # Handle the variable storage location
        self.target, self.class_ = self.engine.stack[-1]["variables"], "_global"
        if isinstance(self.name, str):
            if self.name[0] in [".", "@"]:
                if self.name[0] == ".":
                    self.class_ = self.engine.stack[-1]["class"]

                self.name = self.name[1:]
                self.target = self.engine.classes[self.class_]["variables"]

        # Engine: the execution engine, self explanatory.
        # Type: "ref", "lit", or "opr". Odds are, it's probably "ref" if Argument() is being called on it.
        # Value: list of tuples, representing the argument tokens.
        #   - Structure example:
        #       1. Operator: [("opr", <operator function>)]
        #       2. Reference: [("ref", [...more of these structure objects])]
        #       3. Literal: [("lit", <int/float/str/bool/bytes/...>)]

        # Check that this is a reference (OR an operator):
        if self.type == "ref" and not (isinstance(self.value, list) and self.value[0][0] == "ref"):
            if isinstance(self.value, list):
                self.name, self.value = None, engine.execute_line(self.value)

            else:
                self.set(self.target.get(self.name))

    def __str__(self) -> str:
        return str(self.value)
    
    def __repr__(self) -> str:
        return f"<Argument T='{self.type}' N='{self.name}' V={repr(self.value)} />"

    def set(self, value: Any) -> Any:
        if isinstance(value, Argument):
            value = value.value

        self.value = value
        self.target[self.name] = value
        return value

    def remove(self) -> None:
        if self.name in self.target:
            del self.target[self.name]
        
        self.value, self.target = None, None

    def refresh(self) -> None:
        self.value = self.target.get(self.name)
