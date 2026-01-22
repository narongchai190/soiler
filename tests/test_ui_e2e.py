"""
Legacy E2E test file - tests moved to tests_e2e/ folder.

This file is kept for backwards compatibility but tests have been
relocated to tests_e2e/test_ui_smoke.py with improved fixtures.

Run E2E tests with: pytest tests_e2e/ -v
"""

import pytest

# Skip all tests in this file - use tests_e2e/ instead
pytestmark = pytest.mark.skip(reason="E2E tests moved to tests_e2e/ folder")
