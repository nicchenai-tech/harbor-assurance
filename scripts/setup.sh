#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python -m pip install --no-deps -e .
printf '\nReady. Start with: .venv/bin/python -m harbor.server --data demo-data\n'
