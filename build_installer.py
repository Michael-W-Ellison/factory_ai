#!/usr/bin/env python3
"""
Installer build script for Recycling Factory.

This script builds the game executable and creates platform-specific installers.

Usage:
    python build_installer.py              # Build executable + installer
    python build_installer.py --exe-only   # Build executable only
    python build_installer.py --installer-only  # Build installer only (exe must exist)

Platforms:
    Windows: Creates .exe installer using Inno Setup
    Linux: Creates install.sh script with desktop integration
    macOS: Creates .app bundle (future)
"""

import os
import sys
import platform
import subprocess
import shutil
import argparse
from pathlib import Path


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.absolute()


def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed with code {result.returncode}")
    return result


def build_executable(project_root):
    """Build the game executable using PyInstaller."""
    print("\n" + "=" * 60)
    print("Building executable...")
    print("=" * 60 + "\n")

    build_script = project_root / 'build.py'
    result = subprocess.run([sys.executable, str(build_script)], cwd=str(project_root))

    if result.returncode != 0:
        print("ERROR: Failed to build executable")
        return False

    # Verify executable exists
    if platform.system() == 'Windows':
        exe_path = project_root / 'dist' / 'RecyclingFactory.exe'
    else:
        exe_path = project_root / 'dist' / 'RecyclingFactory'

    if not exe_path.exists():
        print(f"ERROR: Executable not found at {exe_path}")
        return False

    print(f"Executable built: {exe_path}")
    return True


def build_windows_installer(project_root):
    """Build Windows installer using Inno Setup."""
    print("\n" + "=" * 60)
    print("Building Windows installer...")
    print("=" * 60 + "\n")

    iss_file = project_root / 'installer' / 'windows' / 'recycling_factory.iss'

    if not iss_file.exists():
        print(f"ERROR: Inno Setup script not found: {iss_file}")
        return False

    # Check for Inno Setup compiler
    iscc_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe",
    ]

    iscc_exe = None
    for path in iscc_paths:
        if os.path.exists(path):
            iscc_exe = path
            break

    # Also check PATH
    if not iscc_exe:
        iscc_exe = shutil.which("ISCC")

    if not iscc_exe:
        print("ERROR: Inno Setup Compiler (ISCC.exe) not found!")
        print("Please install Inno Setup from: https://jrsoftware.org/isdl.php")
        print("\nAlternatively, you can run the .iss script manually in Inno Setup.")
        return False

    # Create output directory
    output_dir = project_root / 'dist' / 'installer'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run Inno Setup compiler
    try:
        run_command([iscc_exe, str(iss_file)])
        print(f"\nWindows installer created in: {output_dir}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to build installer: {e}")
        return False


def build_linux_installer(project_root):
    """Prepare Linux installer scripts."""
    print("\n" + "=" * 60)
    print("Preparing Linux installer...")
    print("=" * 60 + "\n")

    install_script = project_root / 'installer' / 'linux' / 'install.sh'
    uninstall_script = project_root / 'installer' / 'linux' / 'uninstall.sh'

    if not install_script.exists():
        print(f"ERROR: Install script not found: {install_script}")
        return False

    # Make scripts executable
    os.chmod(install_script, 0o755)
    os.chmod(uninstall_script, 0o755)

    # Create a distributable archive
    dist_dir = project_root / 'dist'
    exe_path = dist_dir / 'RecyclingFactory'

    if not exe_path.exists():
        print(f"ERROR: Executable not found: {exe_path}")
        return False

    # Create tarball with executable and installer
    archive_name = 'RecyclingFactory_Linux'
    archive_dir = dist_dir / archive_name
    archive_dir.mkdir(exist_ok=True)

    # Copy files
    shutil.copy(exe_path, archive_dir / 'RecyclingFactory')
    shutil.copy(install_script, archive_dir / 'install.sh')
    shutil.copy(uninstall_script, archive_dir / 'uninstall.sh')

    # Copy desktop file
    desktop_file = project_root / 'installer' / 'linux' / 'recycling-factory.desktop'
    if desktop_file.exists():
        shutil.copy(desktop_file, archive_dir / 'recycling-factory.desktop')

    # Create tarball
    archive_path = dist_dir / f'{archive_name}.tar.gz'
    if archive_path.exists():
        archive_path.unlink()

    shutil.make_archive(
        str(dist_dir / archive_name),
        'gztar',
        str(dist_dir),
        archive_name
    )

    print(f"Linux installer archive created: {archive_path}")
    print(f"\nTo install:")
    print(f"  1. Extract: tar -xzf {archive_name}.tar.gz")
    print(f"  2. Run: cd {archive_name} && ./install.sh")

    return True


def build_macos_app(project_root):
    """Build macOS .app bundle (placeholder for future implementation)."""
    print("\n" + "=" * 60)
    print("Building macOS app bundle...")
    print("=" * 60 + "\n")

    print("NOTE: macOS .app bundle creation is not yet implemented.")
    print("The standalone executable can be run directly on macOS.")
    print("\nFor a proper .app bundle, consider using py2app or")
    print("manually creating the bundle structure.")

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Build Recycling Factory installer'
    )
    parser.add_argument(
        '--exe-only',
        action='store_true',
        help='Build executable only, skip installer'
    )
    parser.add_argument(
        '--installer-only',
        action='store_true',
        help='Build installer only (executable must exist)'
    )
    parser.add_argument(
        '--platform',
        choices=['windows', 'linux', 'macos', 'auto'],
        default='auto',
        help='Target platform (default: auto-detect)'
    )

    args = parser.parse_args()
    project_root = get_project_root()

    print("=" * 60)
    print("Recycling Factory - Installer Build")
    print("=" * 60)
    print(f"Project root: {project_root}")
    print(f"Platform: {platform.system()}")

    # Determine target platform
    if args.platform == 'auto':
        target = platform.system().lower()
        if target == 'darwin':
            target = 'macos'
    else:
        target = args.platform

    success = True

    # Build executable
    if not args.installer_only:
        if not build_executable(project_root):
            return 1

    # Build platform-specific installer
    if not args.exe_only:
        if target == 'windows':
            success = build_windows_installer(project_root)
        elif target == 'linux':
            success = build_linux_installer(project_root)
        elif target == 'macos':
            success = build_macos_app(project_root)
        else:
            print(f"Unknown platform: {target}")
            success = False

    if success:
        print("\n" + "=" * 60)
        print("BUILD COMPLETE!")
        print("=" * 60)
        print(f"\nOutput directory: {project_root / 'dist'}")
        return 0
    else:
        print("\n" + "=" * 60)
        print("BUILD FAILED!")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
