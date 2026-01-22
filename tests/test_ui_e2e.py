import pytest
import subprocess
import time
import sys
import os
import requests
from playwright.sync_api import Page, expect

# Constants
PORT = 8501
BASE_URL = f"http://localhost:{PORT}"

def wait_for_streamlit(url, timeout=15):
    """Wait for Streamlit server to be responsive."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(f"{url}/_stcore/health")
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    return False

@pytest.fixture(scope="module")
def streamlit_app():
    """Start Streamlit app and yield the URL."""
    # Command to run streamlit
    cmd = [
        sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
        "--server.port", str(PORT),
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    
    # Start process
    process = subprocess.Popen(
        cmd, 
        env={**os.environ, "PYTHONPATH": os.getcwd()},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server
    if not wait_for_streamlit(BASE_URL):
        process.terminate()
        stdout, stderr = process.communicate()
        print(f"Streamlit stdout: {stdout.decode()}")
        print(f"Streamlit stderr: {stderr.decode()}")
        pytest.fail("Streamlit failed to start")
        
    yield BASE_URL
    
    # Cleanup
    process.terminate()
    process.wait()

def test_app_loads(page: Page, streamlit_app):
    """Verify the app loads the title."""
    page.goto(streamlit_app)
    # Wait for Streamlit app to fully load (title changes from "Streamlit" to actual title)
    page.wait_for_load_state("networkidle")
    expect(page).to_have_title("S.O.I.L.E.R. | ระบบ AI เพื่อการเกษตรแม่นยำ", timeout=10000)
    expect(page.get_by_text("S.O.I.L.E.R.").first).to_be_visible()

def test_sidebar_summary_visible(page: Page, streamlit_app):
    """Verify the selection summary panel exists in sidebar."""
    page.goto(streamlit_app)
    page.wait_for_load_state("networkidle")
    # The summary title we added
    expect(page.get_by_text("สรุปข้อมูลที่เลือก").first).to_be_visible()

def test_run_analysis_smoke(page: Page, streamlit_app):
    """Verify clicking run triggers the pipeline."""
    page.goto(streamlit_app)
    page.wait_for_load_state("networkidle")

    # Wait for the button
    # The button text includes an icon "🔬 เริ่มวิเคราะห์"
    run_button = page.get_by_role("button", name="เริ่มวิเคราะห์")
    expect(run_button).to_be_visible(timeout=10000)
    
    # Click
    run_button.click()
    
    # Check for processing indicator
    # "กำลังวิเคราะห์" appears in multiple places, use .first to avoid strict mode error
    expect(page.get_by_text("กำลังวิเคราะห์").first).to_be_visible()
    
    # We don't wait for full completion in a fast smoke test unless we mock agents
    # But we can verify it doesn't immediately crash.
    # Check for error toast or message
    expect(page.locator(".stException")).not_to_be_visible()
