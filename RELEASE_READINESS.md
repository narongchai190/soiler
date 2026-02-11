# Production Readiness Gate (Strict Mode)

This repository enforces a **Strict CI Gate** for all changes. Fails in this gate block merging to the default branch (`master` or `main`).

## 1. Gate Architecture

We divide checks into two levels to optimize feedback loops:

### **P0 Gate (Blocker)**
- **Speed:** Fast (< 2 mins)
- **Environment:** No browser, no external network.
- **Checks:**
  - 🔒 **Secrets:** Scans git-tracked files for keys/tokens (`scripts/scan_secrets.py --mode=tracked`).
  - 🐍 **Syntax:** `compileall` validation.
  - 🧹 **Lint:** `ruff` enforcement.
  - 🧪 **Unit Tests:** `pytest` (excluding E2E).
  - 🏗️ **Import Smoke:** Verifies app importability via `python -c`.

### **P1 Gate (High Priority)**
- **Speed:** Slower (app boot + browser launch)
- **Checks:**
  - 🕸️ **UI Smoke:** Playwright E2E tests (dropdowns, run button).
  - 🏥 **Healthcheck:** Deterministic Streamlit boot & HTTP 200 check.

## 2. Running Locally

**Prerequisites:**
```bash
pip install -r requirements-dev.txt
playwright install chromium  # Only needed for P1
```

**Run P0 Only (fast, no browser):**
```bash
python scripts/release_gate.py --level p0
```

**Run P1 Only (UI smoke + healthcheck):**
```bash
python scripts/release_gate.py --level p1
```

**Run All Checks:**
```bash
python scripts/release_gate.py --level all
```

**Secret Scanner (standalone):**
```bash
python scripts/scan_secrets.py --mode=tracked
```

## 3. Branch Protection (GitHub)

To ensure strict enforcement, repository admins **MUST** enable Branch Protection on `master` (or `main`):

1. Go to **Settings** > **Branches**.
2. Add rule for `master` (or currently active default branch).
3. Check **Require status checks to pass before merging**.
4. Search for and select these exact job names:
   - `gate_p0`
   - `gate_p1_ui`
5. (Optional) Check "Do not allow bypassing the above settings".

## 4. Troubleshooting Failures

| Failure | Fix |
|---------|-----|
| `no_secrets` | Remove the secret file or add to `.gitignore`. **ROTATE ANY EXPOSED KEYS.** |
| `syntax_check` | Fix Python syntax errors. Run `python -m compileall .` locally. |
| `lint_check` | Run `ruff check . --fix`. |
| `app_launch` | Ensure `streamlit_app.py` runs without errors via `python -c "import streamlit_app"`. |
| `ui_smoke` | Run `pytest tests_e2e/ --headed` to debug UI interactions. |

## 5. Notes

- **Windows encoding:** The release gate runner reconfigures stdout/stderr to UTF-8 on Windows to avoid `UnicodeEncodeError` with emoji output.
- **Line endings:** Repository uses `.gitattributes` to normalize to LF. Windows `.bat`/`.ps1` scripts use CRLF.
