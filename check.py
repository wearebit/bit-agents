#!/bin/env python
import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

exclude_files = [
    # Add files/directories to exclude from ruff formatting and linting here
    # e.g. "migrations/" or "some_script.py"
]


@dataclass
class Command:
    # Command to run, including args
    command: list[str]

    # Directory to run the command in, relative to the project root
    cwd: Path = Path(".")


def venv(s: str) -> str:
    """Ensure that the executable within a venv is used"""
    # This will be the bin directory of the current virtualenv
    bin = Path(sys.executable).parent
    return str(bin / s)


_exclude_args = [arg for f in exclude_files for arg in ("--exclude", f)]

# Run ruff across the whole repository ("."). Anything that should not be
# touched is handled by exclude_files above, ruff's built-in default excludes
# (.venv, .git, node_modules, build, dist, ...), and .gitignore.
_targets = ["."]

# Shared flags applied to every command:
# --isolated ignores config files (all config is done here).
_shared_args = ["--isolated"]

commands = {
    "fmt": Command([venv("ruff"), "format", *_targets, *_shared_args, *_exclude_args]),
    # Running formatter with --check flag avoids actually formatting any files,
    # returns non-zero status code if any unformatted files are encountered
    "fmt-check": Command(
        [venv("ruff"), "format", "--check", *_targets, *_shared_args, *_exclude_args]
    ),
    "lint": Command(
        [
            venv("ruff"),
            "check",
            "--fix",
            # Intentionally disabled rules:
            # E711 (comparison to None), E712 (comparison to True/False),
            # E731 (lambda assignment), E741 (ambiguous variable name),
            # E402 (top of file import).
            "--ignore=E402,E711,E712,E731,E741",
            *_targets,
            *_shared_args,
            *_exclude_args,
        ]
    ),
}


def print_divider(s, width):
    """Print the name of the command surrounded by '='"""
    print(f"{' ' + s + ' ':=^{width}}")


def main():
    """
    Run the checks for the CI. By default, runs fmt and lint.
    It is also possible to specify a list of commands to run.

    The development requirements should be installed for this
    program to work.

    The following commands are available:
    - fmt: formatting
    - lint: linting
    - fmt-check: check formatting but don't apply fixes (for CI)

    The checks run across the whole repository, except excluded directories.
    """
    parser = argparse.ArgumentParser(
        description="""
            Run the checks for the CI. By default, runs fmt and lint.
            It is also possible to specify a list of commands to run.

            The development requirements should be installed for this
            program to work.

            The following commands are available:
            - fmt: formatting
            - lint: linting
            - fmt-check: check formatting but don't apply fixes (for CI)

            The checks run across the whole repository, except excluded
            directories.
       """
    )
    parser.add_argument("commands", nargs="*", default=["fmt", "lint"])
    args = parser.parse_args()

    # The get_terminal_size command fails in some cases
    # where there isn't really a terminal width.
    # This is the case in the CI. 80 should be a reasonable default.
    # The width is used to print the dividers between the commands.
    try:
        width = os.get_terminal_size().columns
    except OSError:
        width = 80

    cwd = Path(__file__).parent

    for c in args.commands:
        command = commands[c]
        print_divider(c, width)

        result = subprocess.run(command.command, cwd=cwd / command.cwd)

        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print(result.stderr)

        if result.returncode > 0:
            print(f"Command '{c}' failed with code {result.returncode}")
            print("Exiting...")
            sys.exit(result.returncode)


if __name__ == "__main__":
    main()
