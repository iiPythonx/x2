# Copyright 2022 iiPython

# Modules
import os
from typing import Any

from .datastore import Memory
from ..exceptions import SectionConflict

# Section class
class Section(object):
    """
    x2 Section Class
    Holds all section data: id, path, lines, etc.
    """
    def __init__(self, sid: str, path: str, lines: list, start: int) -> None:
        self.sid = sid
        self.path = os.path.abspath(path)
        self.lines = lines
        self.start = start

        self.return_value = None
        self.current_line = start

    def __repr__(self) -> str:
        return f"<Section ID='{self.sid}' SourcePath='{self.path}' StartLine={self.start}>"

    def initialize(self, mem: Memory) -> None:
        self._mem = mem
        if self.path not in self._mem.variables["file"]:
            self._mem.variables["file"][self.path] = {}

        self._mem.variables["scope"][self.sid] = {}

    def trash(self) -> Any:
        if self.path in self._mem.variables["file"]:

            # Check that this is the last running scope in our file before garbage collecting
            ns = self.path.replace("\\", "/").split("/")[-1].removesuffix(".x2")
            if [s for s in self._mem.variables["scope"] if s.split(".")[0] == ns] == [self.sid]:
                del self._mem.variables["file"][self.path]

        if self.sid in self._mem.variables["scope"]:
            del self._mem.variables["scope"][self.sid]

        return self.return_value

# Section loader
def load_sections(source: str, filepath: str, namespace: str = None) -> list:
    """
    Takes an x2 source file and breaks it into a list of sections.
    """

    # Calculate file name
    filepath = filepath.replace("\\", "/")
    filename = filepath.split("/")[-1].removesuffix(".x2") or namespace

    # Initialization
    data = {"sections": [{"sid": f"{filename}.main", "path": filepath, "lines": [], "start": 1}]}

    # Split sections
    for lno, line in enumerate(source.splitlines()):
        line = line.strip()
        if line and line[0] == ":" and line[:2] != "::":
            sid = f"{filename}.{line[1:]}"
            if sid in [s["sid"] for s in data["sections"]]:
                raise SectionConflict(f"section '{sid}' is already registered")

            data["sections"].append({"sid": sid, "path": filepath, "lines": [], "start": lno + 2})
            continue

        data["sections"][-1]["lines"].append(line)

    return data["sections"]
