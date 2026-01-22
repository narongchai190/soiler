"""
S.O.I.L.E.R. Encoding Bootstrap Module

Ensures UTF-8 encoding works deterministically across all Windows environments
(CMD, PowerShell, VS Code terminal, etc.) without requiring user intervention.

Must be imported and called VERY EARLY in both CLI and Streamlit entrypoints,
before any Thai text is printed or logged.
"""

import os
import sys
import logging

_bootstrapped = False


def bootstrap_utf8() -> None:
    """
    Initialize UTF-8 encoding for the entire application.

    This function:
    1. Sets PYTHONUTF8=1 for any subprocesses
    2. Reconfigures sys.stdout/sys.stderr to UTF-8 with error handling
    3. Ensures logging handlers use UTF-8 explicitly

    Safe to call multiple times (idempotent).
    """
    global _bootstrapped
    if _bootstrapped:
        return

    # 1. Set environment variables for subprocesses
    os.environ["PYTHONUTF8"] = "1"
    os.environ["PYTHONIOENCODING"] = "utf-8"

    # 2. Reconfigure stdout/stderr for UTF-8 (Windows-specific fix)
    if sys.platform == "win32":
        _reconfigure_streams()

    # 3. Configure logging to use UTF-8
    _configure_utf8_logging()

    _bootstrapped = True


def _reconfigure_streams() -> None:
    """
    Reconfigure sys.stdout and sys.stderr to use UTF-8 encoding.

    Uses errors='replace' to prevent crashes on unencodable characters.
    Guarded against AttributeError if reconfigure is not available.
    """
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        # Some environments don't support reconfigure
        pass

    try:
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def _configure_utf8_logging() -> None:
    """
    Configure the root logger to use UTF-8 encoding on all handlers.
    """
    root_logger = logging.getLogger()

    # Update existing handlers to use UTF-8
    for handler in root_logger.handlers:
        _set_handler_encoding(handler)


def _set_handler_encoding(handler: logging.Handler) -> None:
    """
    Set UTF-8 encoding on a logging handler.
    """
    try:
        if isinstance(handler, logging.StreamHandler):
            if hasattr(handler.stream, "reconfigure"):
                handler.stream.reconfigure(encoding="utf-8", errors="replace")
        elif isinstance(handler, logging.FileHandler):
            # FileHandler: close and reopen with UTF-8
            if handler.stream and not handler.stream.closed:
                handler.close()
                handler.stream = open(
                    handler.baseFilename,
                    handler.mode,
                    encoding="utf-8",
                    errors="replace"
                )
    except Exception:
        # Silently ignore if encoding can't be set
        pass


def safe_print(*args, **kwargs) -> None:
    """
    A safe print wrapper that handles encoding errors gracefully.

    Use this instead of raw print() when outputting Thai or other
    non-ASCII text in contexts where encoding might fail.

    Falls back to replacing unencodable characters with '?'.
    """
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Fallback: encode with replace and decode back
        text = " ".join(str(arg) for arg in args)
        safe_text = text.encode("utf-8", errors="replace").decode("utf-8")
        print(safe_text, **kwargs)


def get_utf8_logger(name: str) -> logging.Logger:
    """
    Get a logger configured with UTF-8 safe handlers.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))

        # Ensure UTF-8 encoding
        if hasattr(handler.stream, "reconfigure"):
            try:
                handler.stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger
