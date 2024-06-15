# Copyright (c) 2024 iiPython

# Modules
from types import FunctionType

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

# Load modules
from .stdlib import (   # noqa: E402
    mod_files,          # noqa: F401
    mod_internal,       # noqa: F401
    mod_math,           # noqa: F401
    mod_branch,         # noqa: F401
    mod_datatype        # noqa: F401
)
