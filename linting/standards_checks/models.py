"""Shared types and constants for the coding-standards checks.

Holds the Finding record and the source-file extensions recognized across the
checks. These are shared by several modules, so per rule 11 they live in one
central place; the per-check numeric thresholds instead live beside the code
that applies them."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PYTHON_EXTS = {".py"}
TS_EXTS = {".ts", ".tsx", ".js", ".jsx"}


@dataclass
class Finding:
    """A single rule violation: where it is and which standard it breaks.

    Attributes:
        path (Path): File the violation is in.
        line (int): 1-indexed line to point the reader at.
        rule (str): Short id of the broken rule (e.g. "1-function-length").
        message (str): Human-readable description plus the suggested fix.
        symbol (str | None): Function name for symbol-specific findings.
    """

    path: Path
    line: int
    rule: str
    message: str
    symbol: str | None = None
