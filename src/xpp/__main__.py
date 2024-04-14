# Copyright 2022-2024 iiPython

# Modules
import sys
from pathlib import Path

from . import __version__, fetch_tokens_from_file, ExecutionEngine

# CLI class
class CLI(object):
    def __init__(self) -> None:
        self.argv, self.vals = sys.argv[1:], {}
        self.options = [
            {"args": ["-h", "--help"], "fn": self.show_help, "desc": "Displays the help menu"},
            {"args": ["-hl", "--helplong"], "fn": self.show_help_long, "desc": "Displays a more detailed help menu"},
            {"args": ["-v", "--ver", "--version"], "fn": self.show_version, "desc": "Prints the x++ version"}
        ]
        self.usage = f"""x++ (x{__version__})
(c) 2021-24 iiPython; (c) 2022-23 Dm123321_31mD "DmmD" Gaming

Usage:
    xpp [options] [flags] <file>
    File can be replaced by a dot ('.'), using the 'main' value of .xconfig instead

See '{sys.executable} -m xpp -hl' for more detailed usage."""

        # Load filepath
        self.filepath = None
        if self.argv:
            self.filepath = Path(([a for a in self.argv if a[0] != "-"] or [None])[-1])

        # Handle options
        for opt in self.options:
            if any([a in self.argv for a in opt["args"]]):
                opt["fn"]()

    def show_help(self) -> None:
        print(self.usage)
        return sys.exit(0)

    def show_help_long(self) -> None:
        print("\n".join(self.usage.split("\n")[:-1]))
        print("\nOptions:")
        for opt in self.options:
            print(f"  {', '.join(opt['args'])}\n    {opt['desc']}")

        return sys.exit(0)

    def show_version(self) -> None:
        return sys.exit(__version__)

# Initialization
cli = CLI()

# Main handler
def main() -> None:
    filepath = cli.filepath
    if filepath is None:
        cli.show_help()

    elif not filepath.is_file():
        sys.exit("x++ Exception: no such file")

    tokens = fetch_tokens_from_file(filepath)

    engine = ExecutionEngine(tokens)
    engine.execute_method()

if __name__ == "__main__":  # Don't run twice from setup.py import
    main()
