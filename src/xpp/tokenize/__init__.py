# Copyright (c) 2024 iiPython
# This file is an absolute nightmare. Rewrite using classes soonish?

# Modules
import re
import pickle
from pathlib import Path

from os.path import getmtime
from typing import Any, List, Tuple

from xpp.operators import operators
from xpp.engine.types import ItemType

from .tokenizer import tokenize
from .expressions import REGX_GROUP_CLASS, REGX_GROUP_FUNCT, REGX_GROUP_OCALL, REGX_GROUP_FLOAT

# Initialization
cache_location = Path.cwd() / ".xpp"
configured_indent = " " * 4  # 4 spaces OR \t

# Exceptions
class InvalidSyntax(Exception):
    pass

# Rewrite portions
class OperatorHandleMode:
    ENABLED     = 1
    REFERENCE   = 2

# Exported functions
literals = {"true": True, "false": False, "none": None}

def typehint_tokens(tokens: List[str], opmode: int) -> List[Tuple[str, Any]]:
    hinted_tokens = []
    for index, token in enumerate(tokens):
        if token.lstrip("-").isnumeric():
            hinted_tokens.append((ItemType.LITERAL, int(token)))

        elif token[0] in ["\"", "'"]:
            hinted_tokens.append((ItemType.LITERAL, token[1:][:-1]))

        elif re.match(REGX_GROUP_FLOAT, token):
            hinted_tokens.append((ItemType.LITERAL, float(token)))

        elif token in literals:
            hinted_tokens.append((ItemType.LITERAL, literals[token]))

        else:
            object_match = re.match(REGX_GROUP_OCALL, token)
            if object_match is not None:
                hinted_tokens.append(("obj", *object_match.groups()))

            else:
                match token[0]:
                    case "{":
                        hinted_tokens.append((ItemType.REFERENCE, typehint_tokens(
                            tokenize(token[1:][:-1]),
                            OperatorHandleMode.REFERENCE
                        )))

                    case "(":
                        token_data = typehint_tokens(
                            tokenize(token[1:][:-1]),
                            OperatorHandleMode.ENABLED
                        )

                        # This is unideal, but it's the best way I can come up with right now.
                        if len(token_data) == 3 and all([
                            token_data[0][0] in [ItemType.LITERAL, ItemType.REFERENCE, ItemType.COMPARISON],
                            token_data[1][0] == ItemType.REFERENCE,
                            token_data[2][0] in [ItemType.LITERAL, ItemType.REFERENCE, ItemType.COMPARISON]
                        ]):
                            hinted_tokens.append((ItemType.COMPARISON, token_data))

                        else:
                            hinted_tokens.append((ItemType.REFERENCE, token_data))

                    case _:
                        if index == 0 and token in operators:  # and opmode != OperatorHandleMode.DISABLED:
                            if opmode == OperatorHandleMode.ENABLED:
                                hinted_tokens.append((ItemType.OPERATOR, operators[token]))
                                continue

                            elif opmode == OperatorHandleMode.REFERENCE:
                                hinted_tokens.append((ItemType.REFERENCE, operators[token]))
                                continue

                        hinted_tokens.append((
                            ItemType.REFERENCE,
                            operators.get(token, token)
                        ))

    return hinted_tokens

def fetch_tokens_from_file(file: Path) -> dict:
    match file.suffix:
        case ".json":
            exit("xpp: unable to read json token files, please use the bytecode format.")

        case ".x":
            return pickle.loads(file.read_bytes())

    cached_path = cache_location / file.with_suffix(".x")
    if cached_path.is_file() and getmtime(cached_path) >= getmtime(file):
        return pickle.loads(cached_path.read_bytes())

    tokens = {"classes": {"_global": {"methods": {"_main": {"lines": [], "args": [], "variables": {}, "offset": 0}}, "variables": {}, "file": file}}}
    active_class, active_method, last_indent = None, None, 0

    content, modified_index = file.read_text().splitlines(), 0
    for index, raw_line in enumerate(content):
        line = raw_line.lstrip()
        if not line or line[:2] == "::":
            continue

        indent_level = raw_line[:-len(line)].replace(configured_indent, "\t").count("\t")
        previous_line = (index and content[index - 1]) or ""
        if previous_line and previous_line[-1] == "\\":
            indent_level = last_indent

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
            tokenized_line = tokenize(line)
            method_to_add_to = tokens["classes"][active_class or "_global"]["methods"][active_method or "_main"]
            if index and content[index - 1].strip() and content[index - 1][-1] == "\\":
                method_to_add_to["lines"][-1] = method_to_add_to["lines"][-1][:-1] + typehint_tokens(
                    tokenized_line,
                    OperatorHandleMode.ENABLED
                )

            else:
                method_to_add_to["lines"].append(typehint_tokens(
                    tokenized_line,
                    OperatorHandleMode.ENABLED
                ))

        else:
            groupings = line_match.groups()
            match groupings[0]:
                case "class":
                    if active_class is not None or indent_level != 0:
                        raise InvalidSyntax
                    
                    active_class = groupings[1]
                    if active_class in tokens["classes"]:
                        raise InvalidSyntax

                    tokens["classes"][active_class] = {"methods": {}, "variables": {}, "file": file}

                case "func":
                    active_method = groupings[1]
                    if (active_class is not None) and (indent_level != 1):
                        raise InvalidSyntax

                    class_to_add_to = tokens["classes"][active_class or "_global"]
                    if active_method in class_to_add_to["methods"]:
                        raise InvalidSyntax

                    class_to_add_to["methods"][active_method] = {"lines": [], "args": groupings[2].split(" ") if groupings[2] else [], "variables": {}, "offset": modified_index}

        # Continue
        last_indent = indent_level
        if line[0] != ":":
            modified_index += 1

    cache_location.mkdir(exist_ok = True)
    cached_path.write_bytes(pickle.dumps(tokens))
    return tokens
