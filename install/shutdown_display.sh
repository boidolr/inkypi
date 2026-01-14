#!/bin/bash
# Shutdown script for InkyPi service
# This script clears the display and sets it to powersave mode

INSTALL_PATH="/usr/local/inkypi"
VENV_PATH="$INSTALL_PATH/venv_inkypi"
SCRIPT_PATH="$INSTALL_PATH/src/shutdown_display.py"

# Check if venv exists
if [ -d "$VENV_PATH" ]; then
    # Run the Python shutdown script using the venv
    "$VENV_PATH/bin/python3" "$SCRIPT_PATH"
else
    echo "Virtual environment not found at $VENV_PATH"
    exit 1
fi
