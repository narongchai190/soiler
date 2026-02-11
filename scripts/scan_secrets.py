#!/usr/bin/env python3
"""
Secret Scanner for S.O.I.L.E.R.

Scans the repository for potential hardcoded secrets.
Exits with code 1 if any secrets are found.

Usage:
    python scripts/scan_secrets.py
"""


import argparse
import subprocess
import re
import sys
from pathlib import Path

# Patterns that indicate potential secrets
SECRET_PATTERNS = [
    # Cloud API Keys
    (r"AIzaSy[0-9A-Za-z_-]{33}", "Google API Key"),
    (r"sk-[a-zA-Z0-9]{48}", "OpenAI API Key"),
    (r"sk-proj-[a-zA-Z0-9]{48}", "OpenAI Project Key"),

    # GitHub Tokens
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
    (r"gho_[a-zA-Z0-9]{36}", "GitHub OAuth Token"),
    (r"ghs_[a-zA-Z0-9]{36}", "GitHub Server Token"),
    (r"ghr_[a-zA-Z0-9]{36}", "GitHub Refresh Token"),

    # LINE Messaging API
    (r"[a-f0-9]{32}", "Potential LINE Channel Secret (32 hex)"),  # Only flag if in context

    # JWT / Bearer tokens
    (r"eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*", "JWT Token"),
    (r"(?i)bearer\s+[a-zA-Z0-9_-]{20,}", "Bearer Token"),

    # AWS
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    (r"(?i)aws_secret_access_key\s*=\s*['\"][^'\"]{20,}['\"]", "AWS Secret Key"),

    # Generic patterns
    (r"(?i)api[_-]?key\s*=\s*['\"][a-zA-Z0-9_-]{16,}['\"]", "API Key Assignment"),
    (r"(?i)password\s*=\s*['\"][^'\"]{8,}['\"]", "Hardcoded Password"),
    (r"(?i)secret\s*=\s*['\"][^'\"]{8,}['\"]", "Hardcoded Secret"),
    (r"(?i)token\s*=\s*['\"][a-zA-Z0-9_-]{20,}['\"]", "Hardcoded Token"),
]

# Directories/files to exclude (strict backup for fallback mode)
EXCLUDE_DIRS = {
    ".venv", "venv", "__pycache__", ".git", "node_modules",
    ".pytest_cache", "dist", "build", ".eggs", "*.egg-info",
    ".mypy_cache", ".ruff_cache", ".tox"
}
EXCLUDE_FILES = {".env", ".env.local", ".env.example", "secrets.toml"}
EXCLUDE_EXTENSIONS = {
    ".pyc", ".pyo", ".db", ".sqlite", ".sqlite3",
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg",
    ".whl", ".tar", ".gz", ".zip", ".exe", ".dll",
    ".json" # Often contains data, scan with care if needed
}


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
        # Extra check: some json files might be credentials
        if filepath.suffix.lower() == ".json":
            if "cred" in filepath.name.lower() or "secret" in filepath.name.lower() or "service" in filepath.name.lower():
                return True # Scan suspicious jsons
            return False
        return False

    return True


def scan_file(filepath: Path) -> list:
    """Scan a single file for secrets with line numbers."""
    findings = []

    try:
        # Skip if file doesn't exist (might be deleted but still in git index occasionally)
        if not filepath.exists():
            return []

        lines = filepath.read_text(encoding="utf-8", errors="ignore").splitlines()

        for line_num, line in enumerate(lines, start=1):
            for pattern, description in SECRET_PATTERNS:
                # Skip 32-hex pattern unless it looks like a real secret context
                if "32 hex" in description:
                    if not re.search(r"(?i)(channel|secret|token|key)", line):
                        continue

                matches = re.findall(pattern, line)
                for match in matches:
                    # Redact the actual secret in output
                    redacted = match[:8] + "..." + match[-4:] if len(match) > 12 else "***"
                    findings.append({
                        "file": str(filepath),
                        "line": line_num,
                        "type": description,
                        "match": redacted,
                    })

    except Exception:
        # Skip files that can't be read
        pass

    return findings


def get_tracked_files(root_dir: Path) -> list[Path]:
    """Get list of files tracked by git."""
    try:
        # Run git ls-files
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=root_dir,
            capture_output=True,
            text=True,
            check=True
        )
        files = [root_dir / f for f in result.stdout.splitlines() if f.strip()]
        return files
    except subprocess.CalledProcessError:
        print("Warning: Not a git repository or git not found. Falling back to simple scan.")
        return []


def scan_repository(repo_path: Path, mode: str = "tracked") -> list:
    """Scan repository for secrets."""
    all_findings = []
    files_to_scan = []

    if mode == "tracked":
        print("Mode: Tracked Files Only (via git ls-files)")
        tracked = get_tracked_files(repo_path)
        if tracked:
            files_to_scan = tracked
        else:
            # Fallback
            print("Fallback: Scanning all files (git ls-files failed)")
            files_to_scan = repo_path.rglob("*")
    else:
        print("Mode: All Files (recursive scan)")
        files_to_scan = repo_path.rglob("*")

    count = 0
    for filepath in files_to_scan:
        filepath = Path(filepath) # Ensure Path object
        if filepath.is_file() and should_scan_file(filepath):
            count += 1
            findings = scan_file(filepath)
            all_findings.extend(findings)
    
    print(f"Scanned {count} files.")
    return all_findings


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="S.O.I.L.E.R. Secret Scanner")
    parser.add_argument("--mode", choices=["tracked", "all"], default="tracked", 
                      help="Scan mode: 'tracked' (git files only) or 'all' (files on disk)")
    args = parser.parse_args()

    repo_path = Path.cwd()

    print("=" * 60)
    print("S.O.I.L.E.R. Secret Scanner")
    print("=" * 60)
    print(f"Scanning: {repo_path}")
    
    findings = scan_repository(repo_path, mode=args.mode)

    print()
    if findings:
        print(f"FAILED: Found {len(findings)} potential secret(s):")
        print()
        for finding in findings:
            print(f"  - {finding['type']}")
            print(f"    Location: {finding['file']}:{finding['line']}")
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
