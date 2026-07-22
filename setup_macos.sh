#!/bin/sh

set -e
cd "$(dirname "$0")"

PYTHON_COMMAND="python3.11"

if ! command -v "$PYTHON_COMMAND" >/dev/null 2>&1; then
    echo "Python 3.11 was not found. Install it before continuing."
    exit 1
fi

echo "Creating the macOS virtual environment..."
"$PYTHON_COMMAND" -m venv .venv

echo "Installing project dependencies..."
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

echo "Setup complete. Run ./run_macos.sh to start the application."
