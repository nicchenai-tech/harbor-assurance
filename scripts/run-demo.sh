#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
exec .venv/bin/python -m harbor.server --data demo-data --runtime runtime-demo --port 8766
