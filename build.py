#!/usr/bin/env python3
"""
Build script for Recycling Factory game.

This script creates a standalone executable using PyInstaller.

Usage:
    python build.py              # Build executable
    python build.py --clean      # Clean build artifacts
    python build.py --onedir     # Build as directory (faster, for testing)
    python build.py --debug      # Build with console window for debugging
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.absolute()


def clean_build_artifacts(project_root):
    """Remove build artifacts."""
    dirs_to_remove = ['build', 'dist', '__pycache__']
    files_to_remove = ['*.pyc', '*.pyo', '*.spec.bak']

    print("Cleaning build artifacts...")

    for dir_name in dirs_to_remove:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"  Removing {dir_path}")
            shutil.rmtree(dir_path)

    # Clean __pycache__ in subdirectories
    for pycache in project_root.rglob('__pycache__'):
        print(f"  Removing {pycache}")
        shutil.rmtree(pycache)

    print("Clean complete!")


def check_pyinstaller():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("ERROR: PyInstaller is not installed!")
        print("Install it with: pip install pyinstaller")
        return False


def check_pygame():
    """Check if Pygame is installed."""
    try:
        import pygame
        print(f"Pygame version: {pygame.version.ver}")
        return True
    except ImportError:
        print("ERROR: Pygame is not installed!")
        print("Install it with: pip install pygame")
        return False


def build_executable(project_root, onedir=False, debug=False):
    """Build the executable using PyInstaller."""

    if not check_pyinstaller():
        return False

    if not check_pygame():
        return False

    spec_file = project_root / 'recycling_factory.spec'

    if not spec_file.exists():
        print(f"ERROR: Spec file not found: {spec_file}")
        return False

    print("\n" + "=" * 60)
    print("Building Recycling Factory executable...")
    print("=" * 60 + "\n")

    # Build command
    cmd = [sys.executable, '-m', 'PyInstaller']

    if onedir:
        # Override to onedir mode for faster builds during testing
        cmd.extend([
            '--onedir',
            '--name', 'RecyclingFactory',
            '--add-data', f'data{os.pathsep}data',
            '--add-data', f'config.py{os.pathsep}.',
        ])
        if not debug:
            cmd.append('--windowed')
        cmd.append('main.py')
    else:
        # Use spec file for full build
        cmd.extend(['--clean', str(spec_file)])

    if debug:
        print("Debug mode: Console window will be visible")

    print(f"Running: {' '.join(cmd)}\n")

    # Run PyInstaller
    result = subprocess.run(cmd, cwd=str(project_root))

    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("BUILD SUCCESSFUL!")
        print("=" * 60)

        if onedir:
            exe_path = project_root / 'dist' / 'RecyclingFactory' / 'RecyclingFactory.exe'
        else:
            exe_path = project_root / 'dist' / 'RecyclingFactory.exe'

        # Check for Linux/Mac executable (no .exe)
        if not exe_path.exists():
            exe_path = exe_path.with_suffix('')

        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\nExecutable created: {exe_path}")
            print(f"Size: {size_mb:.1f} MB")
        else:
            print(f"\nExecutable location: {project_root / 'dist'}")

        return True
    else:
        print("\n" + "=" * 60)
        print("BUILD FAILED!")
        print("=" * 60)
        print("Check the error messages above for details.")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Build Recycling Factory executable'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean build artifacts only'
    )
    parser.add_argument(
        '--onedir',
        action='store_true',
        help='Build as directory (faster, for testing)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Build with console window for debugging'
    )

    args = parser.parse_args()
    project_root = get_project_root()

    print(f"Project root: {project_root}")

    if args.clean:
        clean_build_artifacts(project_root)
        return 0

    # Clean before building
    clean_build_artifacts(project_root)

    # Build
    success = build_executable(project_root, args.onedir, args.debug)

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
