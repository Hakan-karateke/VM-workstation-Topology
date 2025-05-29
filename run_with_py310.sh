#!/bin/bash

# Run Python 3.10 script helper for SCADA Network Simulation
# Usage: ./run_with_py310.sh <script_name.py> [arguments]

# Define script directory
SCRIPTS_DIR="$(dirname "$0")/scripts"

# Check if a script name was provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <script_name.py> [arguments]"
    echo "Available scripts:"
    ls -1 "$SCRIPTS_DIR"/*.py | xargs -n1 basename
    exit 1
fi

SCRIPT_NAME="$1"
shift  # Remove script name from arguments

# Find the script
if [ -f "$SCRIPTS_DIR/$SCRIPT_NAME" ]; then
    SCRIPT_PATH="$SCRIPTS_DIR/$SCRIPT_NAME"
elif [ -f "$SCRIPT_NAME" ]; then
    SCRIPT_PATH="$SCRIPT_NAME"
else
    echo "Error: Script '$SCRIPT_NAME' not found in $SCRIPTS_DIR"
    echo "Available scripts:"
    ls -1 "$SCRIPTS_DIR"/*.py | xargs -n1 basename
    exit 1
fi

# Check if Python 3.10 is installed
if command -v python3.10 &>/dev/null; then
    PYTHON_CMD="python3.10"
else
    # Check if default python3 is version 3.10
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    if [[ "$PYTHON_VERSION" == 3.10* ]]; then
        PYTHON_CMD="python3"
    else
        echo "Error: Python 3.10 is not installed. Please run install_py310_deps.sh first."
        exit 1
    fi
fi

# Check if we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d "scada_venv" ]; then
        echo "Activating virtual environment..."
        source scada_venv/bin/activate
    else
        echo "Warning: Virtual environment not found. Dependencies may not be correctly installed."
    fi
fi

# Run the script with Python 3.10
echo "Running $SCRIPT_PATH with $PYTHON_CMD..."
$PYTHON_CMD "$SCRIPT_PATH" "$@"
