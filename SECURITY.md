# Security Policy

## Reporting Vulnerabilities

If you discover a security vulnerability, please report it privately by emailing the maintainers.
Do not create public issues for security vulnerabilities.

## API Keys and Secrets

### No Secrets in Repository

This repository does **NOT** ship any API keys or secrets. All sensitive configuration must be provided via:

1. **Environment variables** - Set `GOOGLE_MAPS_API_KEY`, etc. in your shell
2. **Streamlit secrets** - Create `.streamlit/secrets.toml` (untracked by git)

### Required Action: Key Rotation

If you previously used a version of this code that contained a hardcoded Google Maps API key:

**You MUST rotate (regenerate) your Google Maps API key immediately:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Find the compromised API key
3. Click "Regenerate Key" or delete and create a new one
4. Update your environment/secrets with the new key
5. Review API key restrictions (recommended: restrict to specific APIs and referrers)

### Security Scanning

This repository includes a secret scanner that runs in CI:

```bash
python scripts/scan_secrets.py
```

This script checks for common secret patterns (API keys, tokens, passwords) and fails the build if any are detected.

### Local Development Setup

For local development, create a `.env` file in the project root (this file is gitignored):

```bash
# .env (DO NOT COMMIT)
GOOGLE_MAPS_API_KEY=your_key_here
```

Or set environment variables directly:

```bash
# Windows
set GOOGLE_MAPS_API_KEY=your_key_here

# Linux/Mac
export GOOGLE_MAPS_API_KEY=your_key_here
```

### Streamlit Cloud Deployment

For Streamlit Cloud, configure secrets in the dashboard:

1. Go to your app's settings
2. Click "Secrets"
3. Add your secrets in TOML format:

```toml
GOOGLE_MAPS_API_KEY = "your_key_here"
```

Or create `.streamlit/secrets.toml` locally (gitignored).

### What To Do If a Key Is Exposed

If you accidentally commit a secret:

1. **Immediately rotate the key** - The old key is compromised forever
2. **Remove from git history** (optional but recommended):
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch path/to/file" \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. **Force push** (if already pushed to remote):
   ```bash
   git push origin --force --all
   ```
4. **Review access logs** - Check for unauthorized usage
5. **Report to team** - Document the incident

### Best Practices

1. **Never commit secrets** - Use `.env` files (excluded via `.gitignore`)
2. **Rotate exposed keys** - If a key is ever committed, rotate it immediately
3. **Use API key restrictions** - Limit keys to specific APIs and referrers
4. **Review access regularly** - Audit who has access to production secrets
5. **Use secret scanning** - Run `python scripts/scan_secrets.py` before commits

## Dependencies

We regularly update dependencies to patch security vulnerabilities. Run:

```bash
pip install --upgrade -r requirements.txt
```

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 2.x     | Yes       |
| 1.x     | No        |
