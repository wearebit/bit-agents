"""Formatting of native findings for the terminal.

Kept separate from the checks themselves so how violations are detected stays
independent of how they're presented."""

from .models import Finding


def print_report(findings: list[Finding]) -> None:
    """Print native findings sorted by file then line.

    Args:
        findings (list[Finding]): All collected native findings.

    How:
        Sorts so each file's issues appear together and top-to-bottom; an empty
        list prints an explicit all-clear so silence is never ambiguous.

    Returns:
        None: Output goes to stdout.
    """
    if not findings:
        print("Native line checks: no violations.")
        return
    findings.sort(key=lambda finding: (str(finding.path), finding.line))
    print("Native line checks:")
    for finding in findings:
        print(f"  {finding.path}:{finding.line}  [{finding.rule}]  {finding.message}")
