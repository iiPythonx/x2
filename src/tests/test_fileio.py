# Copyright (c) 2024 iiPython

# Modules
import os
from pathlib import Path

from xpp.modules.ops.stdlib.fileio import XOperators

from . import run, FakeDatastore

# Begin test definitions
def test_load():
    Path("_xpp.test").write_text("hello, world!")
    assert run(XOperators.load, [FakeDatastore("_xpp.test")]) == "hello, world!"
    os.remove("_xpp.test")

def test_save():
    run(XOperators.save, [FakeDatastore("_xpp.test"), FakeDatastore("hello, world!")])
    assert Path("_xpp.test").read_text() == "hello, world!"
    os.remove("_xpp.test")
