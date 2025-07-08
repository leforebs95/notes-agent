#!/bin/bash
# Handwritten Notes MCP Server Runner
# UV automatically creates venv and installs dependencies as needed

set -e # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# UV handles everything - venv creation, dependency installation, and execution
uv run python server.py
