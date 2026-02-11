#!/usr/bin/env python3
"""Check Python syntax for git-tracked files only.

Compiles only *.py files known to git, skipping .git, .venv,
.pytest_cache, .ruff_cache and other non-source directories.
"""

import subprocess
import sys
import py_compile


def main() -> int:
    result = subprocess.run(
        ["git", "ls-files", "*.py"],
        capture_output=True,
        text=True,
        check=True,
    )
    files = [f for f in result.stdout.strip().splitlines() if f]

    if not files:
        print("No tracked Python files found.")
        return 0

    errors = 0
    for path in files:
        try:
            py_compile.compile(path, doraise=True)
        except py_compile.PyCompileError as exc:
            print(f"SYNTAX ERROR: {exc}", file=sys.stderr)
            errors += 1

    print(f"Checked {len(files)} files, {errors} error(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
