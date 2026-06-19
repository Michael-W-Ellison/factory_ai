@echo off
REM Build script for Windows
REM Creates a standalone executable of Recycling Factory

echo ============================================================
echo Recycling Factory - Windows Build Script
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Check if Pygame is installed
python -c "import pygame" >nul 2>&1
if errorlevel 1 (
    echo Pygame not found. Installing...
    pip install pygame
    if errorlevel 1 (
        echo ERROR: Failed to install Pygame
        pause
        exit /b 1
    )
)

REM Run the build script
echo.
echo Starting build...
echo.
python build.py %*

if errorlevel 1 (
    echo.
    echo Build failed! Check errors above.
    pause
    exit /b 1
)

echo.
echo Build complete! Executable is in the 'dist' folder.
echo.
pause
