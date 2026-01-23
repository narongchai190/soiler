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

### Best Practices

1. **Never commit secrets** - Use `.env` files (excluded via `.gitignore`)
2. **Rotate exposed keys** - If a key is ever committed, rotate it immediately
3. **Use API key restrictions** - Limit keys to specific APIs and referrers
4. **Review access regularly** - Audit who has access to production secrets

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
