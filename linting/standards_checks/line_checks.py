"""Native size and docstring checks: the thresholds and content no linter measures.

Off-the-shelf linters don't measure the standard's exact 50/250 line limits, nor the
custom ``How:`` docstring section, so they're implemented here for Python via ast:
file length (docstring lines excluded), function length, and docstring content. File
length for non-Python languages falls back to a raw line count; TS/JS function length
is left to eslint's max-lines-per-function (bundled config)."""

from __future__ import annotations

import ast

from pathlib import Path

from .discovery import read_lines
from .docstring_checks import check_docstring_sections
from .models import PYTHON_EXTS, Finding

MAX_FUNCTION_LINES = 50   # rule 1: ~50 lines of real logic per function
MAX_FILE_LINES = 250      # rule 3: ~250 lines per file before splitting
_TEST_DIR = "tests"       # docstring content is waived here, mirroring ruff's tests/** D-waiver


def check_file_length(path: Path, code_line_count: int) -> list[Finding]:
    """Flag files longer than the standard's per-file line budget.

    Args:
        path: File being checked.
        code_line_count: Line count to judge, with docstring lines already excluded
            for Python so documentation isn't penalised.

    How:
        Compares the count against MAX_FILE_LINES and reports a single file-level
        finding when it is over budget.

    Returns:
        Zero or one finding for this file.
    """
    if code_line_count <= MAX_FILE_LINES:
        return []
    message = f"file has {code_line_count} code lines excluding docstrings (> {MAX_FILE_LINES}); split via subfolders"
    return [Finding(path, 1, "3-file-length", message)]


def is_docstring(stmt: ast.stmt) -> bool:
    """Return True if a statement is a bare string literal (a docstring).

    Args:
        stmt: A statement node from a module/class/function body.

    How:
        Recognises the ``Expr`` wrapping a string ``Constant`` that Python treats
        as a docstring when it is the first statement of a body.

    Returns:
        True when the statement is a docstring expression.
    """
    return (
        isinstance(stmt, ast.Expr)
        and isinstance(stmt.value, ast.Constant)
        and isinstance(stmt.value.value, str)
    )


def docstring_line_count(tree: ast.AST) -> int:
    """Total physical lines occupied by module/class/function docstrings.

    Args:
        tree: The file's parsed AST.

    How:
        Inspects every module, class and function node and, when its first body
        statement is a docstring, adds that literal's line span. This is what
        ``check_file_length`` subtracts so documentation doesn't count toward the
        file-size budget (rule 4).

    Returns:
        The number of source lines taken up by docstrings.
    """
    total = 0
    scoped = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    for node in ast.walk(tree):
        body = getattr(node, "body", [])
        if isinstance(node, scoped) and body and is_docstring(body[0]):
            doc = body[0]
            total += doc.end_lineno - doc.lineno + 1
    return total


def function_code_lines(node: ast.AST, lines: list[str]) -> int:
    """Estimate the real-logic line count of a Python function body.

    Args:
        node: A FunctionDef/AsyncFunctionDef node with line numbers.
        lines: Full source lines of the file.

    How:
        Spans from the first body statement (skipping a leading docstring) to the
        function's end line and counts only non-blank lines — mirroring rule 1's
        "real statements, not signature/docstring/blanks" so documentation isn't
        penalized.

    Returns:
        Estimated real-logic line count.
    """
    body = node.body
    start = body[0].lineno
    if is_docstring(body[0]):
        # Skip the docstring: next statement, or one past it if it stands alone.
        start = body[1].lineno if len(body) > 1 else body[0].end_lineno + 1
    span = lines[start - 1:node.end_lineno]
    return sum(1 for line in span if line.strip())


def find_long_python_functions(path: Path, tree: ast.AST, lines: list[str]) -> list[Finding]:
    """Flag Python functions whose real-logic length exceeds the standard.

    Args:
        path: Python file to inspect.
        tree: The file's parsed AST.
        lines: Its source lines, used to measure real-logic spans.

    How:
        Walks the AST and measures each function via function_code_lines, flagging
        those over MAX_FUNCTION_LINES.

    Returns:
        One finding per over-long function.
    """
    defs = (n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
    findings: list[Finding] = []
    for node in defs:
        length = function_code_lines(node, lines)
        if length > MAX_FUNCTION_LINES:
            msg = f"{node.name}() has ~{length} logic lines (> {MAX_FUNCTION_LINES}); extract helpers"
            findings.append(Finding(path, node.lineno, "1-function-length", msg, node.name))
    return findings


def _check_python_file(path: Path, lines: list[str]) -> list[Finding]:
    """Run every Python-specific native check off a single parse.

    Args:
        path: Python file being checked.
        lines: Its source lines.

    How:
        Parses once (a syntax error becomes one finding rather than crashing the
        run), then runs file length on the docstring-excluded count, function
        length, and — outside test files — docstring content.

    Returns:
        All native findings for the Python file.
    """
    try:
        tree = ast.parse("\n".join(lines))
    except SyntaxError as err:
        return [Finding(path, err.lineno or 1, "parse-error", f"cannot parse: {err.msg}")]
    code_lines = len(lines) - docstring_line_count(tree)
    findings = check_file_length(path, code_lines)
    findings.extend(find_long_python_functions(path, tree, lines))
    if _TEST_DIR not in path.parts:
        findings.extend(check_docstring_sections(path, tree))
    return findings


def check_file(path: Path) -> list[Finding]:
    """Run all native (no-external-tool) checks for one file.

    Args:
        path: Source file to check.

    How:
        Reads the file once, then dispatches to the Python-specific checks or, for
        other languages, a raw file-length check.

    Returns:
        All native findings for the file.
    """
    lines = read_lines(path)
    if path.suffix in PYTHON_EXTS:
        return _check_python_file(path, lines)
    return check_file_length(path, len(lines))
