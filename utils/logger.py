import logging
import sys
import datetime

import streamlit as st

from core.encoding_bootstrap import bootstrap_utf8


class UILogger:
    @staticmethod
    def setup():
        """Configure logging to console with UTF-8 encoding."""
        # Ensure UTF-8 encoding is bootstrapped first
        bootstrap_utf8()

        # Create handler with UTF-8 encoding for Windows compatibility
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))

        # Set UTF-8 encoding for the stream (redundant after bootstrap, but safe)
        try:
            if hasattr(handler.stream, 'reconfigure'):
                handler.stream.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass  # Ignore if reconfigure fails

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.handlers.clear()
        root_logger.addHandler(handler)

    @staticmethod
    def log(message: str, level: str = "info"):
        """Log to console and optionally to Streamlit session state for debugging."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        
        # Console log
        if level.lower() == "error":
            logging.error(message)
        elif level.lower() == "warning":
            logging.warning(message)
        else:
            logging.info(message)
            
        # UI Log (store in session state if needed for debug expander)
        if "debug_logs" not in st.session_state:
            st.session_state["debug_logs"] = []
        st.session_state["debug_logs"].append(log_msg)

    @staticmethod
    def get_logs():
        if "debug_logs" not in st.session_state:
            return []
        return st.session_state["debug_logs"]
