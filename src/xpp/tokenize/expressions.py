# Copyright (c) 2024 iiPython

# Modules
import re

# Expressions
REGX_GROUP_CLASS = re.compile(r":(class) (\w+)")
REGX_GROUP_FUNCT = re.compile(r":(func) (\w+) \(([\w ]*)\)")
REGX_GROUP_OCALL = re.compile(r"(\w+)\[([\w\{\}\[\]\"\' ]*)\]")
REGX_GROUP_FLOAT = re.compile(r"^-?\d+\.\d+$")
