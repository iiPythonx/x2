# Copyright (c) 2024 iiPython

# Modules
import re
import pickle
from pathlib import Path
from os.path import getmtime
from typing import Any, List, Tuple

from xpp.operators import operators
from .expressions import REGX_GROUP_CLASS, REGX_GROUP_FUNCT, REGX_GROUP_OCALL, REGX_GROUP_FLOAT

# Initialization
cache_location = Path.cwd() / ".xpp"
configured_indent = " " * 4  # 4 spaces OR \t

# Exceptions
class InvalidSyntax(Exception):
    pass

# Exported functions
default_method = {"lines": [], "args": [], "variables": {}}
blocks_start, blocks_end = ["{", "(", "\"", "'", "["], ["}", ")", "\"", "'", "]"]

def typehint_tokens(tokens: List[str]) -> List[Tuple[str, Any]]:
    hinted_tokens = []
    for index, token in enumerate(tokens):
        if token.lstrip("-").isnumeric():
            hinted_tokens.append(("lit", int(token)))

        elif token[0] in ["\"", "'"]:
            hinted_tokens.append(("lit", token[1:][:-1]))

        elif re.match(REGX_GROUP_FLOAT, token):
            hinted_tokens.append(("lit", float(token)))

        else:
            object_match = re.match(REGX_GROUP_OCALL, token)
            if object_match is not None:
                hinted_tokens.append(("obj", *object_match.groups()))

            else:
                match token[0]:
                    case "{" | "(":
                        hinted_tokens.append(("ref", tokenize_line(token[1:][:-1])))

                    case _:
                        if index == 0:
                            if token not in operators:
                                raise InvalidSyntax
                            
                            hinted_tokens.append(("opr", operators[token]))

                        else:
                            hinted_tokens.append(("ref", token))

    return hinted_tokens

def tokenize_line(line: str) -> List[str]:
    data = {"tokens": [], "buffer": "", "depth": [None, 0]}
    for character in line.strip():
        if not data["depth"][0] and character == " " and data["buffer"]:
            if data["buffer"].strip() == "::":
                data["buffer"] = ""
                break

            data["tokens"].append(data["buffer"])
            data["buffer"] = ""

        elif not data["depth"][0] and character in blocks_start:
            data["depth"] = [blocks_end[blocks_start.index(character)], 1]
            if character == "[":
                data["buffer"] += "["

        elif character == data["depth"][0] and data["depth"][1] == 1:
            if data["depth"][0] != "]":
                data["buffer"] = f"{blocks_start[blocks_end.index(data['depth'][0])]}{data['buffer']}{data['depth'][0]}"

            else:
                data["buffer"] += "]"

            data["depth"] = [None, 0]

        elif data["depth"][1] == 0 and character == "\\":
            continue

        else:
            data["buffer"] += character

    return typehint_tokens(data["tokens"] + ([data["buffer"]] if data["buffer"] else []))

def fetch_tokens_from_file(file: Path) -> dict:
    cached_path = cache_location / file.with_suffix(".x")
    if cached_path.is_file() and getmtime(cached_path) >= getmtime(file):
        return pickle.loads(cached_path.read_bytes())

    tokens = {"classes": {"_global": {"methods": {"_main": default_method}, "variables": {}}}}
    active_class, active_method, last_indent = None, None, 0

    content = file.read_text().splitlines()
    for index, raw_line in enumerate(content):
        line = raw_line.lstrip()
        if not line or line[:2] == "::":
            continue

        indent_level = raw_line[:-len(line)].replace(configured_indent, "\t").count("\t")

        # Check indentation level
        if indent_level < last_indent:
            if active_class is not None and indent_level < 1:
                active_class = None

            if active_method is not None:
                active_method = None

        # Handle parsing
        line_match = re.search(REGX_GROUP_CLASS, line) or re.search(REGX_GROUP_FUNCT, line)
        if line_match is None:
            if line[0] == ":":
                raise InvalidSyntax

            if indent_level != 2 and active_class is not None:
                raise InvalidSyntax

            # Save line data
            method_to_add_to = tokens["classes"][active_class or "_global"]["methods"][active_method or "_main"]
            if index and content[index - 1].strip() and content[index - 1][-1] == "\\":
                method_to_add_to["lines"][-1] += tokenize_line(line)

            else:
                method_to_add_to["lines"].append(tokenize_line(line))

        else:
            groupings = line_match.groups()
            match groupings[0]:
                case "class":
                    if active_class is not None or indent_level != 0:
                        raise InvalidSyntax
                    
                    active_class = groupings[1]
                    if active_class in tokens["classes"]:
                        raise InvalidSyntax

                    tokens["classes"][active_class] = {"methods": {}, "variables": {}}

                case "func":
                    active_method = groupings[1]
                    if (active_class is not None) and (indent_level != 1):
                        raise InvalidSyntax

                    class_to_add_to = tokens["classes"][active_class or "_global"]
                    if active_method in class_to_add_to["methods"]:
                        raise InvalidSyntax

                    class_to_add_to["methods"][active_method] = default_method | {"args": groupings[2].split(" ") if groupings[2] else []}

        # Continue
        last_indent = indent_level

    cache_location.mkdir(exist_ok = True)
    cached_path.write_bytes(pickle.dumps(tokens))
    return tokens
