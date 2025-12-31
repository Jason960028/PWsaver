#!/bin/bash
source venv/bin/activate
# Remove previous build artifacts
rm -rf build dist

# Run PyInstaller
# --windowed: No terminal window
# --onefile: Single executable
# --name: Output name
# Note: No need to include style.qss as theme is now generated dynamically
pyinstaller --name "PwKeeper" \
            --windowed \
            --onefile \
            --clean \
            src/main.py

echo "Build complete. Check 'dist/PwKeeper.app'"
