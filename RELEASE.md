# Release Process

## Pre-Release Checklist

### 1. Code Quality
- [ ] All tests pass: `pytest -v`
- [ ] Lint passes: `ruff check .`
- [ ] Syntax check: `python -m py_compile main.py streamlit_app.py`
- [ ] No uncommitted changes: `git status`

### 2. Functionality
- [ ] CLI runs: `python main.py -q`
- [ ] Pipeline completes without errors
- [ ] Output shows "Analysis Complete"

### 3. Documentation
- [ ] CHANGELOG.md updated with new version
- [ ] VERSION file updated
- [ ] README.md accurate

### 4. Environment
- [ ] .env.example lists all optional vars
- [ ] requirements.txt is minimal and correct
- [ ] No hardcoded secrets in code

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
