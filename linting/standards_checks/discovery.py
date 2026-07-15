"""File discovery and reading for the checks.

Turns CLI arguments into the concrete list of source files to inspect, and reads
them robustly, while skipping vendored and generated directories so the report
stays focused on code the user actually owns."""

from pathlib import Path

from .models import PYTHON_EXTS, TS_EXTS

SKIP_DIRS = {"node_modules", ".venv", "venv", ".git", "dist", "build", "__pycache__"}


def is_source(path: Path) -> bool:
    """Return True if a path isn't inside a vendored or generated directory.

    Args:
        path (Path): Candidate source file.

    How:
        Checks each path component against SKIP_DIRS so dependencies and build
        output don't drown the report in violations the user can't fix.

    Returns:
        bool: True if the file should be checked.
    """
    return not any(part in SKIP_DIRS for part in path.parts)


def gather_paths(args: list[str]) -> list[Path]:
    """Expand CLI arguments into concrete source files to check.

    Args:
        args (list[str]): Files or directories; defaults to "." when empty.

    How:
        Directories are walked recursively for known source extensions while
        explicit files are kept as given, so the script works both in CI (the
        whole tree) and in a pre-commit hook (only the staged files).

    Returns:
        list[Path]: Source files to inspect.
    """
    roots = [Path(arg) for arg in args] or [Path(".")]
    exts = PYTHON_EXTS | TS_EXTS
    files: list[Path] = []
    for root in roots:
        if root.is_file():
            files.append(root)
            continue
        files.extend(p for p in root.rglob("*") if p.suffix in exts and is_source(p))
    return files


def read_lines(path: Path) -> list[str]:
    """Read a file's lines, tolerating undecodable bytes.

    Args:
        path (Path): File to read.

    How:
        Decodes as UTF-8 and replaces invalid bytes so a single binary-ish file
        can't abort the whole run; unreadable files raise with context instead
        of a bare OSError.

    Returns:
        list[str]: The file's lines without trailing newlines.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as err:
        raise RuntimeError(f"Could not read {path}: {err}") from err
    return text.splitlines()
