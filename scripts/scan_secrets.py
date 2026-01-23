#!/usr/bin/env python3
"""
Secret Scanner for S.O.I.L.E.R.

Scans the repository for potential hardcoded secrets.
Exits with code 1 if any secrets are found.

Usage:
    python scripts/scan_secrets.py
"""

import os
import re
import sys
from pathlib import Path


# Patterns that indicate potential secrets
SECRET_PATTERNS = [
    (r"AIzaSy[0-9A-Za-z_-]{33}", "Google API Key"),
    (r"sk-[a-zA-Z0-9]{48}", "OpenAI API Key"),
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
    (r"gho_[a-zA-Z0-9]{36}", "GitHub OAuth Token"),
    (r"(?i)password\s*=\s*['\"][^'\"]{8,}['\"]", "Hardcoded Password"),
    (r"(?i)secret\s*=\s*['\"][^'\"]{8,}['\"]", "Hardcoded Secret"),
]

# Directories/files to exclude
EXCLUDE_DIRS = {".venv", "__pycache__", ".git", "node_modules", ".pytest_cache"}
EXCLUDE_FILES = {".env", ".env.local", "secrets.toml"}
EXCLUDE_EXTENSIONS = {".pyc", ".pyo", ".db", ".sqlite", ".sqlite3", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".whl"}


def should_scan_file(filepath: Path) -> bool:
    """Check if file should be scanned."""
    # Check excluded directories
    for part in filepath.parts:
        if part in EXCLUDE_DIRS:
            return False

    # Check excluded files
    if filepath.name in EXCLUDE_FILES:
        return False

    # Check excluded extensions
    if filepath.suffix.lower() in EXCLUDE_EXTENSIONS:
        return False

    return True


def scan_file(filepath: Path) -> list:
    """Scan a single file for secrets."""
    findings = []

    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")

        for pattern, description in SECRET_PATTERNS:
            matches = re.findall(pattern, content)
            for match in matches:
                # Redact the actual secret in output
                redacted = match[:8] + "..." + match[-4:] if len(match) > 12 else "***"
                findings.append({
                    "file": str(filepath),
                    "type": description,
                    "match": redacted,
                })

    except Exception as e:
        # Skip files that can't be read
        pass

    return findings


def scan_repository(repo_path: Path) -> list:
    """Scan entire repository for secrets."""
    all_findings = []

    for filepath in repo_path.rglob("*"):
        if filepath.is_file() and should_scan_file(filepath):
            findings = scan_file(filepath)
            all_findings.extend(findings)

    return all_findings


def main():
    """Main entry point."""
    repo_path = Path(__file__).parent.parent

    print("=" * 60)
    print("S.O.I.L.E.R. Secret Scanner")
    print("=" * 60)
    print(f"Scanning: {repo_path}")
    print()

    findings = scan_repository(repo_path)

    if findings:
        print(f"FAILED: Found {len(findings)} potential secret(s):")
        print()
        for finding in findings:
            print(f"  - {finding['type']}")
            print(f"    File: {finding['file']}")
            print(f"    Match: {finding['match']}")
            print()

        print("ACTION REQUIRED:")
        print("  1. Remove hardcoded secrets from code")
        print("  2. Use environment variables or secret managers")
        print("  3. If keys were exposed, rotate them immediately")
        print()
        sys.exit(1)
    else:
        print("PASSED: No hardcoded secrets detected.")
        print()
        sys.exit(0)


if __name__ == "__main__":
    main()
