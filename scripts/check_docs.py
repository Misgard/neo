#!/usr/bin/env python3
"""Documentation integrity gate.

Validates the requirement identifiers in docs/system/prd.md and the ADR index.
Catches the two failure modes that matter when several sessions edit the PRD:
a reference to a requirement that does not exist, and two requirements sharing
an identifier.

Exit code 0 on success, 1 on any error.
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRD = ROOT / "docs" / "system" / "prd.md"
ADR_DIR = ROOT / "docs" / "system" / "adr"

# A requirement is *defined* by a table row that opens with its identifier.
DEFINITION = re.compile(r"^\|\s*`((?:FR|NFR|INV|A)-\d+)`\s*\|", re.MULTILINE)
# An open question is defined by a bold heading.
OQ_DEFINITION = re.compile(r"\*\*`(OQ-\d+)`")
# Any inline-code identifier is a *reference*.
REFERENCE = re.compile(r"`((?:FR|NFR|INV|OQ|A)-\d+)`")

# Ranges reserved for parallel design sessions; see docs/prompts/.
RESERVED = {
    "identity-and-security": {"FR": (1400, 1499), "NFR": (1000, 1099),
                              "INV": (60, 69), "OQ": (40, 49)},
    "process-workflows": {"FR": (1500, 1599), "NFR": (1100, 1199),
                          "INV": (70, 79), "OQ": (50, 59)},
}


def sort_key(identifier: str) -> tuple[str, int]:
    prefix, number = identifier.split("-")
    return prefix, int(number)


def check_prd(errors: list[str], notes: list[str]) -> None:
    if not PRD.exists():
        errors.append(f"{PRD} does not exist")
        return

    text = PRD.read_text(encoding="utf-8")
    defined_list = DEFINITION.findall(text) + OQ_DEFINITION.findall(text)
    defined = set(defined_list)
    referenced = set(REFERENCE.findall(text))

    dangling = referenced - defined
    if dangling:
        errors.append(
            "referenced but never defined: "
            + ", ".join(sorted(dangling, key=sort_key))
        )

    duplicates = [i for i, n in Counter(defined_list).items() if n > 1]
    if duplicates:
        errors.append(
            "defined more than once: " + ", ".join(sorted(duplicates, key=sort_key))
        )

    if text.count("```") % 2:
        errors.append("unbalanced code fences in prd.md")

    counts = Counter(i.split("-")[0] for i in defined)
    notes.append(
        "prd.md defines "
        + ", ".join(f"{counts[p]} {p}" for p in ("FR", "NFR", "INV", "OQ", "A") if counts[p])
    )

    for track, ranges in RESERVED.items():
        used = [
            i for i in defined
            if (r := ranges.get(i.split("-")[0])) and r[0] <= int(i.split("-")[1]) <= r[1]
        ]
        if used:
            notes.append(f"{track} range in use: {len(used)} identifiers")


def check_adr_index(errors: list[str]) -> None:
    index = ADR_DIR / "README.md"
    if not index.exists():
        errors.append(f"{index} does not exist")
        return

    listed = set(re.findall(r"\((\d{4}-[a-z0-9-]+\.md)\)", index.read_text(encoding="utf-8")))
    on_disk = {p.name for p in ADR_DIR.glob("[0-9][0-9][0-9][0-9]-*.md")}

    for missing in sorted(on_disk - listed):
        errors.append(f"ADR not listed in adr/README.md: {missing}")
    for phantom in sorted(listed - on_disk):
        errors.append(f"adr/README.md links a file that does not exist: {phantom}")


def main() -> int:
    errors: list[str] = []
    notes: list[str] = []

    check_prd(errors, notes)
    check_adr_index(errors)

    for note in notes:
        print(f"  {note}")

    if errors:
        print("\nFAIL: documentation integrity", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print("\nOK: documentation integrity")
    return 0


if __name__ == "__main__":
    sys.exit(main())
