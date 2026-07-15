"""Optional delegation to installed linters (ruff, eslint).

The native checks cover line thresholds; everything else the standard can check
mechanically — naming, docstring presence, param counts, magic numbers, broad
excepts — is enforced by ruff and eslint using the bundled configs. Both are
optional: a missing tool is announced rather than silently passing."""

from __future__ import annotations

import shutil
import subprocess


def run_external(tool: str, command: list[str]) -> str | None:
    """Run an optional external linter, returning its output or None if absent.

    Args:
        tool (str): Executable to probe on PATH.
        command (list[str]): Full command to run when the tool exists.

    How:
        Missing tools return None (these checks are optional). A non-zero exit is
        expected when violations exist, so output is captured regardless of the
        exit code rather than treated as an error.

    Returns:
        str | None: The tool's combined output, or None if it isn't installed.
    """
    if shutil.which(tool) is None:
        return None
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except OSError as err:
        return f"{tool} could not run: {err}"
    return (result.stdout + result.stderr).strip()


def echo_tool(name: str, output: str | None, install_hint: str = "") -> None:
    """Print an external linter's output, or note how to install it if absent.

    Args:
        name (str): Display name of the tool.
        output (str | None): Its output, or None when the tool isn't installed.
        install_hint (str): Command that installs the tool, shown on skip so the
            user can fix the gap instead of silently losing that check's coverage.

    How:
        None means "not installed" — the line checks still ran, so this is a
        heads-up, not an error; empty output means the tool ran and found nothing.

    Returns:
        None: Output goes to stdout.
    """
    if output is None:
        suffix = f" — install with: {install_hint}" if install_hint else ""
        print(f"{name}: not installed (skipped){suffix}")
    elif output:
        print(f"{name}:\n{output}")
    else:
        print(f"{name}: no violations.")


def run_optional_linters(paths: list[str]) -> None:
    """Run ruff and eslint when present and echo their reports.

    Args:
        paths (list[str]): Files to hand to the linters.

    How:
        Each tool is run independently so one missing tool doesn't suppress the
        other; eslint is invoked via npx with --no-install so it only runs when
        already present in the project. Skipped tools print an install hint.

    Returns:
        None: Output goes to stdout.
    """
    ruff_out = run_external("ruff", ["ruff", "check", *paths])
    echo_tool("ruff", ruff_out, "pip install ruff  (or: pipx install ruff)")
    eslint_out = run_external("npx", ["npx", "--no-install", "eslint", *paths])
    echo_tool("eslint", eslint_out, "npm i -D eslint typescript-eslint eslint-plugin-jsdoc")
