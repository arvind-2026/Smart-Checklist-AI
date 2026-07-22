#!/bin/sh

set -e
cd "$(dirname "$0")"

if [ ! -x .venv/bin/python ]; then
    echo "The virtual environment is missing. Run ./setup_macos.sh first."
    exit 1
fi

exec .venv/bin/python -m streamlit run streamlit_app.py
