# Copyright (c) 2022-2024 iiPython

# Modules
import json

# Initialization
block_pairs = {"(": ")", "\"": "\"", "'": "'", "{": "}"}

class InvalidSyntax(Exception):
    pass

# Handle tokenizing
def tokenize(line: str) -> list:
    tokens, mode, depth, val = [], None, 0, ""
    for char in line:
        val += char
        if mode is not None and char == block_pairs.get(mode):
            if depth > 1:
                depth -= 1

            else:
                if char == "(":
                    tokens.append(val)
                    val = ""

                mode, depth = None, 0

        elif char in block_pairs:
            if not depth:
                mode = char

            if char == mode:
                depth += 1

        elif mode is None and char == " ":
            if val == char:
                val = ""
                continue

            val = val[:-1]
            if val == "::":  # This is an in-line comment
                break

            tokens.append(val)
            val = ""

    if val:
        if mode is not None and not val.endswith(block_pairs.get(mode)):
            raise InvalidSyntax(f"Expected a closing '{block_pairs[mode]}', found nothing.")

        tokens.append(val)

    if depth > 0:
        raise InvalidSyntax(f"Unexpected depth value after tokenizing. Did you close all open blocks?\nRaw token information: {json.dumps({'mode': mode, 'depth': depth, 'val': val}, indent = 4)}")

    return tokens
