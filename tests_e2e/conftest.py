"""
E2E Test Configuration for S.O.I.L.E.R.

Starts Streamlit server with E2E mode enabled for deterministic testing.
"""

import os
import subprocess
import sys
import time

import pytest
import requests


# E2E Test Port (different from default to avoid conflicts)
E2E_PORT = 8502
E2E_BASE_URL = f"http://127.0.0.1:{E2E_PORT}"


def wait_for_streamlit(url: str, timeout: int = 30) -> bool:
    """Wait for Streamlit server to be responsive."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(f"{url}/_stcore/health", timeout=5)
            if response.status_code == 200:
                return True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            pass
        time.sleep(1)
    return False


@pytest.fixture(scope="session")
def streamlit_server():
    """
    Start Streamlit app with E2E mode for the test session.

    Environment:
        - SOILER_E2E=1: Enable deterministic E2E mode
        - PYTHONUTF8=1: Force UTF-8 encoding
        - PYTHONIOENCODING=utf-8: Force UTF-8 encoding for streams
    """
    # E2E environment variables
    env = {
        **os.environ,
        "SOILER_E2E": "1",
        "PYTHONUTF8": "1",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONPATH": os.getcwd(),
    }

    # Command to run Streamlit
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "streamlit_app.py",
        "--server.port",
        str(E2E_PORT),
        "--server.headless",
        "true",
    ]

    # Start process
    process = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.getcwd(),
    )

    # Wait for server to be ready
    if not wait_for_streamlit(E2E_BASE_URL):
        process.terminate()
        stdout, stderr = process.communicate(timeout=5)
        print(f"Streamlit stdout: {stdout.decode('utf-8', errors='replace')}")
        print(f"Streamlit stderr: {stderr.decode('utf-8', errors='replace')}")
        pytest.fail("Streamlit failed to start within timeout")

    yield E2E_BASE_URL

    # Cleanup
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


@pytest.fixture(scope="function")
def page(browser, streamlit_server):
    """Create a new page for each test and navigate to the app."""
    context = browser.new_context()
    page = context.new_page()
    page.goto(streamlit_server)

    # Wait for Streamlit app to fully load (not just network idle)
    # The app is ready when the main title appears
    page.wait_for_load_state("networkidle")

    # Wait for Streamlit to finish loading (title changes from "Streamlit")
    try:
        page.wait_for_function(
            "document.title !== 'Streamlit'",
            timeout=30000
        )
    except Exception:
        pass  # Continue even if title doesn't change

    # Extra wait for JavaScript to initialize
    page.wait_for_timeout(2000)

    yield page
    context.close()
