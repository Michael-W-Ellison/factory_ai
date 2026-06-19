#!/bin/bash
# Linux Uninstaller for Recycling Factory

set -e

APP_NAME="RecyclingFactory"
DESKTOP_NAME="recycling-factory"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"

echo "============================================================"
echo "Recycling Factory - Linux Uninstaller"
echo "============================================================"
echo

read -p "Are you sure you want to uninstall Recycling Factory? (y/N) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstall cancelled."
    exit 0
fi

echo "Uninstalling Recycling Factory..."

# Remove symlink
if [ -L "$BIN_DIR/RecyclingFactory" ]; then
    echo "  Removing command symlink..."
    rm "$BIN_DIR/RecyclingFactory"
fi

# Remove desktop file
if [ -f "$DESKTOP_DIR/$DESKTOP_NAME.desktop" ]; then
    echo "  Removing desktop entry..."
    rm "$DESKTOP_DIR/$DESKTOP_NAME.desktop"
fi

# Remove icon
if [ -f "$ICON_DIR/$DESKTOP_NAME.png" ]; then
    echo "  Removing icon..."
    rm "$ICON_DIR/$DESKTOP_NAME.png"
fi

# Remove install directory
if [ -d "$INSTALL_DIR" ]; then
    echo "  Removing application files..."
    rm -rf "$INSTALL_DIR"
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

echo
echo "============================================================"
echo "Uninstall complete!"
echo "============================================================"
