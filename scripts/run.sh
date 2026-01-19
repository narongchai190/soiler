#!/bin/bash
# S.O.I.L.E.R. - Run Script for Linux/Mac
# Usage: ./scripts/run.sh [mode]
# Modes: cli (default), web, test, install

set -e

cd "$(dirname "$0")/.."

case "${1:-cli}" in
    install)
        echo "Installing dependencies..."
        pip install -r requirements.txt
        pip install pytest ruff
        ;;
    cli)
        echo "Running S.O.I.L.E.R. CLI..."
        export PYTHONIOENCODING=utf-8
        python main.py "${@:2}"
        ;;
    web)
        echo "Starting S.O.I.L.E.R. Web Dashboard..."
        streamlit run streamlit_app.py
        ;;
    test)
        echo "Running tests..."
        pytest -v
        ;;
    *)
        echo "Unknown mode: $1"
        echo "Usage: ./scripts/run.sh [cli|web|test|install]"
        exit 1
        ;;
esac
