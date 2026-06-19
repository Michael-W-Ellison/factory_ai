#!/bin/bash
# Build script for Linux/Mac
# Creates a standalone executable of Recycling Factory

echo "============================================================"
echo "Recycling Factory - Build Script"
echo "============================================================"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.10+ using your package manager"
    exit 1
fi

echo "Python version: $(python3 --version)"

# Check if PyInstaller is installed
if ! python3 -c "import PyInstaller" &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip3 install pyinstaller
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install PyInstaller"
        exit 1
    fi
fi

# Check if Pygame is installed
if ! python3 -c "import pygame" &> /dev/null; then
    echo "Pygame not found. Installing..."
    pip3 install pygame
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install Pygame"
        exit 1
    fi
fi

echo
echo "Starting build..."
echo

# Run the build script
python3 build.py "$@"

if [ $? -eq 0 ]; then
    echo
    echo "Build complete! Executable is in the 'dist' folder."
else
    echo
    echo "Build failed! Check errors above."
    exit 1
fi
