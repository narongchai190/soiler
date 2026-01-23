# Release Process

## Pre-Release Checklist

### 1. Security (P0 - Must Pass)
- [ ] Secret scan passes: `python scripts/scan_secrets.py`
- [ ] No API keys in docs or code
- [ ] SECURITY.md is up to date
- [ ] No DB files tracked: `git ls-files | findstr ".db"`

### 2. Code Quality
- [ ] Syntax check: `python -m compileall .`
- [ ] Lint passes: `ruff check .`
- [ ] All tests pass: `pytest -v`
- [ ] Evals pass (30 cases): `pytest tests/test_evals.py -v`
- [ ] No uncommitted changes: `git status`

### 3. Functionality
- [ ] CLI runs: `python main.py -q`
- [ ] Import works: `python -c "import streamlit_app"`
- [ ] Pipeline completes without errors
- [ ] E2E smoke tests pass: `pytest tests_e2e/ -v`

### 4. Documentation
- [ ] CHANGELOG.md updated with new version
- [ ] VERSION file matches release
- [ ] README.md accurate
- [ ] RUNBOOK.md current

### 5. Environment
- [ ] .env.example lists all optional vars
- [ ] requirements.txt is minimal and correct
- [ ] .gitignore covers sensitive files
- [ ] Seed data available for fresh installs

## Cutting a Release

```bash
# 1. Run all checks
pytest -v
ruff check .
python main.py -q

# 2. Update version
echo "X.Y.Z" > VERSION

# 3. Update CHANGELOG.md
# Add new section for version

# 4. Commit release prep
git add -A
git commit -m "release: prepare vX.Y.Z"

# 5. Tag release (annotated)
git tag -a vX.Y.Z -m "Release vX.Y.Z"

# 6. Push (if remote configured)
git push origin master --tags
```

## Version Numbering

- **MAJOR**: Breaking changes to CLI or output format
- **MINOR**: New features, new agents, new reports
- **PATCH**: Bug fixes, documentation updates

## Rollback

```bash
# Revert to previous tag
git checkout vX.Y.Z

# Or reset to specific commit
git reset --hard <commit-hash>
```
