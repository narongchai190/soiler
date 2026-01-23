"""
UTF-8 Encoding Bootstrap Tests

Ensures that Thai text can be logged/printed without encoding errors
on Windows systems with various terminal encodings.
"""

import sys



def test_bootstrap_import():
    """Test that bootstrap module can be imported."""
    from core.encoding_bootstrap import bootstrap_utf8, get_utf8_logger, safe_print
    assert callable(bootstrap_utf8)
    assert callable(get_utf8_logger)
    assert callable(safe_print)


def test_bootstrap_idempotent():
    """Test that bootstrap can be called multiple times safely."""
    from core.encoding_bootstrap import bootstrap_utf8
    # Should not raise
    bootstrap_utf8()
    bootstrap_utf8()
    bootstrap_utf8()


def test_utf8_logger_thai_text():
    """Test that UTF-8 logger can handle Thai text without exception."""
    from core.encoding_bootstrap import bootstrap_utf8, get_utf8_logger

    bootstrap_utf8()
    logger = get_utf8_logger("test_thai")

    # These should not raise UnicodeEncodeError
    thai_texts = [
        "สวัสดีครับ",
        "ระบบแนะนำการปรับปรุงดินอัจฉริยะ",
        "ผู้เชี่ยวชาญชุดดิน",
        "ข้าวไรซ์เบอร์รี่",
        "อำเภอเด่นชัย จังหวัดแพร่",
        "ไนโตรเจน ฟอสฟอรัส โพแทสเซียม",
    ]

    for text in thai_texts:
        # Should not raise
        logger.info(text)
        logger.warning(f"Warning: {text}")
        logger.error(f"Error: {text}")


def test_safe_print_thai_text():
    """Test that safe_print handles Thai text without exception."""
    from core.encoding_bootstrap import bootstrap_utf8, safe_print

    bootstrap_utf8()

    # These should not raise UnicodeEncodeError
    thai_texts = [
        "สวัสดีครับ",
        "การวิเคราะห์ดิน",
        "ผลผลิตเป้าหมาย 600 กก./ไร่",
    ]

    for text in thai_texts:
        # Should not raise
        safe_print(text)


def test_stdout_stderr_encoding():
    """Test that stdout/stderr have UTF-8 encoding after bootstrap."""
    from core.encoding_bootstrap import bootstrap_utf8

    bootstrap_utf8()

    # On Windows with reconfigure support, encoding should be UTF-8
    if sys.platform == "win32" and hasattr(sys.stdout, "encoding"):
        # After bootstrap, should be utf-8 (or already was)
        assert sys.stdout.encoding.lower() in ("utf-8", "utf8", "cp65001")


def test_orchestrator_import_no_crash():
    """Test that orchestrator can be imported without encoding crash."""
    from core.encoding_bootstrap import bootstrap_utf8
    bootstrap_utf8()

    # This import should not crash with encoding errors
    from core.orchestrator import SoilerOrchestrator

    # Basic instantiation should work
    orchestrator = SoilerOrchestrator(verbose=False)
    assert orchestrator is not None


def test_environment_variables_set():
    """Test that bootstrap sets proper environment variables."""
    import os
    from core.encoding_bootstrap import bootstrap_utf8

    bootstrap_utf8()

    assert os.environ.get("PYTHONUTF8") == "1"
    assert os.environ.get("PYTHONIOENCODING") == "utf-8"
