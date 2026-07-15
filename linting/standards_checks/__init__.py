"""Coding-standards checks package.

Re-exports the public surface the CLI entrypoint needs, so callers import from
the package rather than reaching into individual modules."""

from .discovery import gather_paths
from .external import run_optional_linters
from .line_checks import check_file
from .models import Finding
from .report import print_report

__all__ = ["gather_paths", "check_file", "print_report", "run_optional_linters", "Finding"]
