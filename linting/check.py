"""CLI entrypoint for the mechanically-checkable coding-standards rules.

Wires discovery, the native line checks (50 lines/function, 250 lines/file),
reporting, and the optional external linters together. Run it on files or
directories, or with no arguments to check the current tree:

    python scripts/check.py                # whole tree
    python scripts/check.py src/ app.py    # specific paths

Exit code is non-zero when a native violation is found, so CI and pre-commit can
fail on it. The heavy lifting lives in the standards_checks package."""

import sys

from standards_checks import check_file, gather_paths, print_report, run_optional_linters


def main(argv: list[str]) -> int:
    """Run native checks, then optional external linters.

    Args:
        argv (list[str]): CLI args after the program name (files/dirs).

    How:
        Collects native findings first (always available) and prints them, then
        appends ruff/eslint output when installed. Returns non-zero when any
        native violation exists so CI/pre-commit can fail the commit.

    Returns:
        int: Process exit code (0 clean, 1 violations found).
    """
    files = gather_paths(argv)
    findings = [finding for path in files for finding in check_file(path)]
    print_report(findings)
    run_optional_linters([str(path) for path in files])
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
