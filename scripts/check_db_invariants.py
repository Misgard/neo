#!/usr/bin/env python3
"""Database invariant gate.

Runs scripts/sql/db_invariants.sql, which asserts INV-012 (evidentiary records
are append-only, enforced by the absence of UPDATE/DELETE grants) and INV-001
(every tenant table has row-level security actually enforced).

Skips cleanly when no database is configured, so it is safe to wire into CI
before the schema exists. It becomes a live gate the moment DATABASE_URL is set.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

SQL = Path(__file__).resolve().parent / "sql" / "db_invariants.sql"


def main() -> int:
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("SKIP: db invariants — DATABASE_URL is not set (no schema yet)")
        return 0

    if not shutil.which("psql"):
        print("FAIL: db invariants — psql is not available", file=sys.stderr)
        return 1

    result = subprocess.run(
        ["psql", url, "--quiet", "--no-psqlrc", "--file", str(SQL)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("FAIL: db invariants", file=sys.stderr)
        print(result.stderr.strip(), file=sys.stderr)
        return 1

    print("OK: db invariants")
    return 0


if __name__ == "__main__":
    sys.exit(main())
