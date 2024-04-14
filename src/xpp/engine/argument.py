# Copyright (c) 2024 iiPython

# Modules
from typing import Any

# Main argument class
class Argument():
    def __init__(self, engine: object, type_: str, value: Any) -> None:
        self.engine, self.type, self.name, self.value = engine, type_, value, value

        # Engine: the execution engine, self explanatory.
        # Type: "ref", "lit", or "opr". Odds are, it's probably "ref" if Argument() is being called on it.
        # Value: list of tuples, representing the argument tokens.
        #   - Structure example:
        #       1. Operator: [("opr", <operator function>, <active True/False>)]
        #            o. `Active` determines whether the expression will get evaluated for its value.
        #       2. Reference: [("ref", [...more of these structure objects])]
        #       3. Literal: [("lit", <int/float/str/bool/bytes/...>)]

        # Check that this is a reference (OR an operator), and make sure it's active (if it is an operator):
        if self.type == "ref" and not (isinstance(self.value, list) and self.value[0][0] == "ref"):
            if (self.value[0][0] == "opr" and self.value[0][2]) or self.value[0][0] != "opr":
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
