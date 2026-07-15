"""Native docstring-content checks: the Args/How/Returns sections rule 6 requires.

Ruff's pydocstyle enforces only that a docstring *exists*; it cannot check for the
custom ``How:`` section, nor make ``Args:``/``Returns:`` conditional on the function's
signature. Those content rules live here, walking the Python AST so each requirement
keys off the function's real parameters and return statements. Presence of the
docstring itself stays ruff's job, so functions without one are skipped here."""

from __future__ import annotations

import ast
import re

from pathlib import Path

from .models import Finding

# Sections rule 6 requires. ``How`` is unconditional; ``Args`` and ``Returns`` are
# gated on the signature (a no-arg function needs no Args, a void function no Returns).
_ALWAYS_REQUIRED = ("How",)
_IMPLICIT_ARG_NAMES = {"self", "cls"}


def _has_section(docstring: str, section: str) -> bool:
    """Whether a Google-style section header appears in a docstring.

    Args:
        docstring: The function docstring text.
        section: Section name without the colon (e.g. "Args").

    How:
        Matches the header at the start of a line, tolerating leading indentation,
        so it recognises the section wherever it sits in the block.

    Returns:
        True if the ``Section:`` header is present.
    """
    return re.search(rf"(?m)^[ \t]*{section}:", docstring) is not None


def _real_params(node: ast.AST) -> list[str]:
    """The function's caller-supplied parameters, excluding ``self``/``cls``.

    Args:
        node: A FunctionDef/AsyncFunctionDef node.

    How:
        Gathers positional-only, normal, keyword-only, ``*args`` and ``**kwargs``
        names, then drops the implicit instance/class parameter.

    Returns:
        The parameter names that an ``Args:`` section would document.
    """
    args = node.args
    names = [a.arg for a in args.posonlyargs + args.args + args.kwonlyargs]
    if args.vararg:
        names.append(args.vararg.arg)
    if args.kwarg:
        names.append(args.kwarg.arg)
    return [name for name in names if name not in _IMPLICIT_ARG_NAMES]


def _returns_value(node: ast.AST) -> bool:
    """Whether the function body has a ``return <value>`` of its own.

    Args:
        node: A FunctionDef/AsyncFunctionDef node.

    How:
        Walks the body iteratively but does not descend into nested functions or
        lambdas, whose returns belong to another scope; a bare ``return`` (value
        ``None``) does not count, so void procedures are exempt from ``Returns:``.

    Returns:
        True if the function returns a real value.
    """
    stack = list(node.body)
    while stack:
        current = stack.pop()
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            continue
        if isinstance(current, ast.Return) and current.value is not None:
            return True
        stack.extend(ast.iter_child_nodes(current))
    return False


def _required_sections(node: ast.AST) -> list[str]:
    """The docstring sections this function must document.

    Args:
        node: A FunctionDef/AsyncFunctionDef node.

    How:
        Starts from the always-required sections, adds ``Args`` when the function
        takes parameters and ``Returns`` when it returns a value.

    Returns:
        Section names (without colons) in report order.
    """
    required = list(_ALWAYS_REQUIRED)
    if _real_params(node):
        required.append("Args")
    if _returns_value(node):
        required.append("Returns")
    return required


def _missing_section_findings(path: Path, node: ast.AST, docstring: str) -> list[Finding]:
    """Findings for each required section a function's docstring omits.

    Args:
        path: File the function lives in.
        node: The FunctionDef/AsyncFunctionDef node.
        docstring: Its docstring text (already known to be present).

    How:
        Compares the required sections against those actually present and emits one
        finding per omission, keyed by function name so a baseline can grandfather it.

    Returns:
        Zero or more findings, one per missing section.
    """
    findings: list[Finding] = []
    for section in _required_sections(node):
        if not _has_section(docstring, section):
            rule = f"6-docstring-{section.lower()}"
            message = f"{node.name}() docstring is missing a '{section}:' section (rule 6)"
            findings.append(Finding(path, node.lineno, rule, message, node.name))
    return findings


def check_docstring_sections(path: Path, tree: ast.AST) -> list[Finding]:
    """Flag functions whose docstrings omit a required Args/How/Returns section.

    Args:
        path: Python file being checked (used only for the finding location).
        tree: The file's already-parsed AST.

    How:
        Walks every function definition, skips those with no docstring (ruff owns
        docstring *presence*), and reports each required section the docstring lacks.

    Returns:
        All docstring-content findings for the file.
    """
    findings: list[Finding] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        docstring = ast.get_docstring(node)
        if docstring is None:
            continue
        findings.extend(_missing_section_findings(path, node, docstring))
    return findings
