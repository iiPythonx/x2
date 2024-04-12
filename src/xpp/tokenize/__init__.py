# Copyright (c) 2024 iiPython

# Modules
import re
from typing import Any, List, Tuple
from pathlib import Path

import orjson

from .expressions import REGX_GROUP_CLASS, REGX_GROUP_FUNCT, REGX_GROUP_OCALL, REGX_GROUP_FLOAT

# Initialization
configured_indent = " " * 4  # 4 spaces OR \t

# Exceptions
class InvalidSyntax(Exception):
    pass

# Exported functions
blocks_start, blocks_end = ["{", "(", "\"", "'", "["], ["}", ")", "\"", "'", "]"]

def typehint_tokens(tokens: List[str]) -> List[Tuple[str, Any]]:
    hinted_tokens = []
    for token in tokens[1:]:
        if token.lstrip("-").isnumeric():
            hinted_tokens.append(("lit", int(token)))

        elif token[0] in ["\"", "'"]:
            hinted_tokens.append(("lit", token[1:][:-1]))

        elif re.match(REGX_GROUP_FLOAT, token):
            hinted_tokens.append(("lit", float(token)))

        else:
            operator_match = re.match(REGX_GROUP_OCALL, token)
            if operator_match is not None:
                hinted_tokens.append(("ref", *operator_match.groups()))

            else:
                match token[0]:
                    case "{" | "(":
                        hinted_tokens.append(("ref", tokenize_line(token[1:][:-1])))

                    case _:
                        hinted_tokens.append(("ref", token))

    return [("opr", tokens[0])] + hinted_tokens

def tokenize_line(line: str) -> List[str]:
    data = {"tokens": [], "buffer": "", "depth": [None, 0]}
    for character in line.strip():
        if not data["depth"][0] and character == " " and data["buffer"]:
            data["tokens"].append(data["buffer"])
            data["buffer"] = ""

        elif not data["depth"][0] and character in blocks_start:
            data["depth"] = [blocks_end[blocks_start.index(character)], 1]
            if character == "[":
                data["tokens"].append(data["buffer"])
                data["buffer"] = ""

        elif character == data["depth"][0] and data["depth"][1] == 1:
            if data["depth"][0] != "]":
                data["buffer"] = f"{blocks_start[blocks_end.index(data['depth'][0])]}{data['buffer']}{data['depth'][0]}"

            data["depth"] = [None, 0]

        else:
            data["buffer"] += character

    return typehint_tokens(data["tokens"] + [data["buffer"]])

def fetch_tokens_from_file(file: Path) -> List[dict]:
    if file.suffix == ".json":
        return orjson.loads(file.read_text())

    tokens = {"classes": {"_global": {"methods": {"_main": {"lines": [], "args": []}}}}}
    active_class, active_method, last_indent = None, None, 0

    content = file.read_text().splitlines()
    for raw_line in content:
        line = raw_line.lstrip()
        if not line:
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

                    tokens["classes"][active_class] = {"methods": {}}

                case "func":
                    active_method = groupings[1]
                    if (active_class is not None) and (indent_level != 1):
                        raise InvalidSyntax

                    class_to_add_to = tokens["classes"][active_class or "_global"]
                    if active_method in class_to_add_to["methods"]:
                        raise InvalidSyntax

                    class_to_add_to["methods"][active_method] = {"lines": [], "args": groupings[2].split(" ") if groupings[2] else []}

        # Continue
        last_indent = indent_level

    file.with_suffix(".json").write_bytes(orjson.dumps(tokens))
    return tokens
