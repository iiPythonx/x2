# Copyright (c) 2024 iiPython

# Modules
from pathlib import Path

from xpp.engine import Argument
from xpp.operators import operator

# Handle operators
@operator("load")
def load(path: Argument) -> str:
    return Path(path).read_text()

@operator("save")
def save(path: Argument, data: Argument) -> None:
    Path(path).write_text(data.value)