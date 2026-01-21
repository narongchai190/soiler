# S.O.I.L.E.R. Audit Backlog

**Generated:** 2026-01-20
**Based on:** AUDIT_REPORT.md findings

---

## Priority Levels

| Priority | Definition | SLA |
|----------|------------|-----|
| **P0** | Critical/Blocking - Security issue, data loss, system unusable | Fix before any release |
| **P1** | High - Major feature broken, frequent crashes, CI unreliable | Fix this sprint |
| **P2** | Medium - Edge-case bugs, UX issues, maintainability | Fix next sprint |
| **P3** | Low - Polish, minor refactors, nice-to-have | Backlog |

---

## P0 - Critical (Must Fix Before Release)

### [P0-001] Remove Hardcoded Google Maps API Key
**Finding:** F-001
**File:** `streamlit_app.py:55-57`
**Effort:** 30 minutes

**Steps:**
1. Go to Google Cloud Console and rotate/delete the exposed key: `<REDACTED_GOOGLE_MAPS_KEY>`
2. Update code:
   ```python
   # Before (lines 54-57):
   try:
       GOOGLE_MAPS_API_KEY = st.secrets.get("GOOGLE_MAPS_API_KEY", "<REDACTED_GOOGLE_MAPS_KEY>")
   except Exception:
       GOOGLE_MAPS_API_KEY = "<REDACTED_GOOGLE_MAPS_KEY>"

   # After:
   GOOGLE_MAPS_API_KEY = None
   try:
       GOOGLE_MAPS_API_KEY = st.secrets.get("GOOGLE_MAPS_API_KEY")
   except Exception:
       pass

   # Note: Map currently uses Folium/OSM, so this key is unused anyway
   ```
3. Verify: Search for hardcoded Google API keys - should return 0 results
4. Commit: `git commit -m "security: remove hardcoded Google Maps API key (F-001)"`

---

## P1 - High Priority (Fix This Sprint)

### [P1-001] Fix Flaky E2E Test
**Finding:** F-002
**File:** `tests/test_ui_e2e.py:85`
**Effort:** 15 minutes

**Steps:**
1. Update the assertion:
   ```python
   # Before (line 85):
   expect(page.get_by_text("กำลังวิเคราะห์")).to_be_visible()

   # After:
   expect(page.get_by_text("กำลังวิเคราะห์").first()).to_be_visible()
   ```
2. Run: `pytest tests/test_ui_e2e.py -v`
3. Verify all 3 tests pass
4. Commit: `git commit -m "test: fix flaky E2E selector (F-002)"`

---

### [P1-002] Clean Up Ruff Lint Errors
**Finding:** F-003
**Files:** Multiple in `agents/`
**Effort:** 15 minutes

**Steps:**
1. Run auto-fix: `ruff check . --select=E,F --ignore=E501,E402 --fix`
2. Review changes: `git diff`
3. If any manual fixes needed:
   - `agents/crop_agent.py:7` - Remove unused `Optional` import
   - `agents/crop_agent.py:402` - Remove `current_day = 0` line
   - `agents/crop_biology_agent.py:208` - Remove `crop_name = ...` line
   - `agents/env_agent.py:9` - Remove unused `Optional` import
   - `agents/env_agent.py:205` - Remove `end_month = ...` line
4. Verify: `ruff check . --select=E,F --ignore=E501,E402` shows 0 errors
5. Update CI to remove `--exit-zero` flag
6. Commit: `git commit -m "refactor: clean up unused imports and variables (F-003)"`

---

## P2 - Medium Priority (Fix Next Sprint)

### [P2-001] Add Missing requests Dependency
**Finding:** F-004
**File:** `requirements.txt`
**Effort:** 10 minutes

**Steps:**
1. Add to `requirements.txt`:
   ```
   requests>=2.28.0
   ```
2. Test in clean venv: `pip install -r requirements.txt`
3. Commit: `git commit -m "deps: add explicit requests dependency (F-004)"`

---

### [P2-002] Add .venv to .gitignore
**Finding:** F-005
**File:** `.gitignore`
**Effort:** 5 minutes

**Steps:**
1. Add to `.gitignore`:
   ```
   .venv/
   ```
2. Verify: `git status` no longer shows .venv files
3. Commit: `git commit -m "chore: add .venv to gitignore (F-005)"`

---

### [P2-003] Optimize CI Playwright Installation
**Finding:** F-006
**File:** `.github/workflows/ci.yml:30-31`
**Effort:** 15 minutes

**Steps:**
1. Add condition:
   ```yaml
   - name: Install Playwright browsers
     if: matrix.python-version == '3.11'
     run: playwright install chromium --with-deps

   - name: Run tests (Unit + E2E)
     if: matrix.python-version == '3.11'
     run: pytest -v

   - name: Run tests (Unit only)
     if: matrix.python-version != '3.11'
     run: pytest -v --ignore=tests/test_ui_e2e.py
   ```
2. Push and verify CI times improve
3. Commit: `git commit -m "ci: optimize Playwright installation (F-006)"`

---

### [P2-004] Wire observation_th in main.py
**Finding:** F-007
**File:** `main.py:195-222`
**Effort:** 15 minutes

**Steps:**
1. Find the observation display code and update:
   ```python
   # Change:
   observation = obs.get("observation", "No observation")
   # To:
   observation = obs.get("observation_th", obs.get("observation", "No observation"))
   ```
2. Test: `python main.py -q` and verify Thai text appears
3. Commit: `git commit -m "fix: wire observation_th in CLI display (F-007)"`

---

### [P2-005] Namespace Session State Keys
**Finding:** F-008
**File:** `streamlit_app.py`
**Effort:** 1 hour

**Steps:**
1. Search for all `st.session_state[` usages
2. Rename keys with `soiler_` prefix:
   - `farm_lat` → `soiler_farm_lat`
   - `farm_lng` → `soiler_farm_lng`
   - `crop_idx` → `soiler_crop_idx`
   - `texture_idx` → `soiler_texture_idx`
   - `irrigation` → `soiler_irrigation`
   - `prefer_organic` → `soiler_prefer_organic`
   - `debug_logs` → `soiler_debug_logs`
3. Test UI thoroughly
4. Commit: `git commit -m "refactor: namespace session state keys (F-008)"`

---

## P3 - Low Priority (Backlog)

### [P3-001] Improve Exception Handling
**Finding:** F-009
**File:** `streamlit_app.py:1657-1658`
**Effort:** 15 minutes

**Steps:**
1. Search for `except:` (bare exceptions)
2. Replace with specific exception types:
   ```python
   except (ValueError, TypeError):
       record_date = "N/A"
   ```
3. Commit: `git commit -m "refactor: use specific exception types (F-009)"`

---

### [P3-002] Add Type Hints to Agent Methods
**Finding:** F-010
**Files:** `agents/*.py`
**Effort:** 2 hours

**Steps:**
1. Add return type hints to public methods
2. Consider running mypy for validation
3. Commit: `git commit -m "typing: add return type hints to agents (F-010)"`

---

### [P3-003] Create VERSION File
**Finding:** F-011
**Effort:** 5 minutes

**Steps:**
1. Create file: `echo "0.1.0" > VERSION`
2. Update main.py to read from VERSION if desired
3. Commit: `git commit -m "release: add VERSION file (F-011)"`

---

## Summary Table

| ID | Title | Priority | Effort | Status |
|----|-------|----------|--------|--------|
| P0-001 | Remove hardcoded API key | P0 | 30m | TODO |
| P1-001 | Fix flaky E2E test | P1 | 15m | TODO |
| P1-002 | Clean up ruff lint errors | P1 | 15m | TODO |
| P2-001 | Add requests dependency | P2 | 10m | TODO |
| P2-002 | Add .venv to gitignore | P2 | 5m | TODO |
| P2-003 | Optimize CI Playwright | P2 | 15m | TODO |
| P2-004 | Wire observation_th | P2 | 15m | TODO |
| P2-005 | Namespace session state | P2 | 1h | TODO |
| P3-001 | Improve exception handling | P3 | 15m | TODO |
| P3-002 | Add type hints | P3 | 2h | TODO |
| P3-003 | Create VERSION file | P3 | 5m | TODO |

**Total Estimated Effort:** ~5 hours

---

## Quick Wins (< 15 minutes each)

1. [P2-002] Add .venv to gitignore (5m)
2. [P3-003] Create VERSION file (5m)
3. [P2-001] Add requests dependency (10m)
4. [P1-001] Fix flaky E2E test (15m)
5. [P1-002] Clean up ruff lint errors (15m)

**Combined Quick Wins:** ~50 minutes to fix 5 issues

---

## Merge with Existing TODO.md

The following items from TODO.md are confirmed by this audit:

| TODO.md Item | Audit Finding | Status |
|--------------|---------------|--------|
| Wire up observation_th in report | F-007 | Confirmed |
| Add logging framework | Not blocking | Backlog |
| Consolidate duplicate climate data | Not blocking | Backlog |
| Remove unused imports | F-003 | Confirmed |
| Add type hints | F-010 | Confirmed |

**Recommendation:** Merge BACKLOG_AUDIT.md with TODO.md after P0/P1 fixes are complete.
