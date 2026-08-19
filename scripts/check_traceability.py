#!/usr/bin/env python3
"""Traceability gate.

Every commit that touches something other than documentation must reference a
requirement that actually exists in docs/system/prd.md.

This is what keeps an implementation anchored to the specification. Behaviour
that no requirement describes is either a defect or a missing requirement, and
either way it should surface at review time rather than months later.

If you need behaviour the PRD does not specify: add the requirement, then
implement it.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRD = ROOT / "docs" / "system" / "prd.md"

IDENTIFIER = re.compile(r"\b((?:FR|NFR|INV)-\d+)\b")
DEFINITION = re.compile(r"^\|\s*`((?:FR|NFR|INV|A)-\d+)`\s*\|", re.MULTILINE)

# Paths that describe rather than implement, and so need no requirement.
DOC_ONLY_PREFIXES = ("docs/", "CLAUDE.md", "README.md", ".gitignore")


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, cwd=ROOT, check=False
    ).stdout.strip()


def base_ref() -> str:
    for candidate in ("origin/main", "main"):
        merge_base = git("merge-base", "HEAD", candidate)
        if merge_base:
            return merge_base
    return ""


def main() -> int:
    if not PRD.exists():
        print("FAIL: traceability — prd.md not found", file=sys.stderr)
        return 1

    known = set(DEFINITION.findall(PRD.read_text(encoding="utf-8")))
    base = base_ref()
    if not base:
        print("SKIP: traceability — no base ref to compare against")
        return 0

    revisions = git("rev-list", "--no-merges", f"{base}..HEAD").splitlines()
    if not revisions:
        print("OK: traceability — no commits to check")
        return 0

    errors: list[str] = []
    checked = 0

    for revision in revisions:
        files = git("show", "--name-only", "--format=", revision).splitlines()
        files = [f for f in files if f]
        if not files or all(f.startswith(DOC_ONLY_PREFIXES) for f in files):
            continue

        checked += 1
        subject = git("show", "--no-patch", "--format=%s", revision)
        message = git("show", "--no-patch", "--format=%B", revision)
        cited = set(IDENTIFIER.findall(message))

        if not cited:
            errors.append(f"{revision[:8]} {subject}\n      cites no requirement")
            continue

        unknown = cited - known
        if unknown:
            errors.append(
                f"{revision[:8]} {subject}\n      cites unknown: {', '.join(sorted(unknown))}"
            )

    if errors:
        print("\nFAIL: traceability", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        print(
            "\n  Reference the FR-###/NFR-###/INV-### the change implements.\n"
            "  If the PRD does not specify it, add the requirement first.",
            file=sys.stderr,
        )
        return 1

    print(f"OK: traceability — {checked} implementation commit(s) checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
