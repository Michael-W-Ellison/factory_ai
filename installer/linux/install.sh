#!/bin/bash
# Linux Installer for Recycling Factory
# This script installs the game to the user's local applications

set -e

APP_NAME="RecyclingFactory"
DESKTOP_NAME="recycling-factory"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"

echo "============================================================"
echo "Recycling Factory - Linux Installer"
echo "============================================================"
echo

# Find the script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Check if executable exists
if [ -f "$PROJECT_ROOT/dist/RecyclingFactory" ]; then
    EXE_PATH="$PROJECT_ROOT/dist/RecyclingFactory"
elif [ -f "$PROJECT_ROOT/dist/RecyclingFactory/RecyclingFactory" ]; then
    EXE_PATH="$PROJECT_ROOT/dist/RecyclingFactory/RecyclingFactory"
    ONEDIR_BUILD=true
else
    echo "ERROR: Executable not found!"
    echo "Please build the game first: python build.py"
    exit 1
fi

echo "Installing Recycling Factory..."
echo "  Install directory: $INSTALL_DIR"
echo

# Create directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$DESKTOP_DIR"
mkdir -p "$ICON_DIR"

# Copy executable
if [ "$ONEDIR_BUILD" = true ]; then
    echo "  Copying application files..."
    cp -r "$PROJECT_ROOT/dist/RecyclingFactory/"* "$INSTALL_DIR/"
else
    echo "  Copying executable..."
    cp "$EXE_PATH" "$INSTALL_DIR/"
fi

# Make executable
chmod +x "$INSTALL_DIR/RecyclingFactory"

# Create symlink in bin directory
echo "  Creating command symlink..."
ln -sf "$INSTALL_DIR/RecyclingFactory" "$BIN_DIR/RecyclingFactory"

# Copy icon if available
if [ -f "$PROJECT_ROOT/assets/icons/icon.png" ]; then
    echo "  Installing icon..."
    cp "$PROJECT_ROOT/assets/icons/icon.png" "$ICON_DIR/$DESKTOP_NAME.png"
fi

# Install desktop file
echo "  Installing desktop entry..."
cat > "$DESKTOP_DIR/$DESKTOP_NAME.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Recycling Factory
GenericName=Factory Management Game
Comment=AI-controlled automated recycling factory management game
Exec=$INSTALL_DIR/RecyclingFactory
Icon=$DESKTOP_NAME
Terminal=false
Categories=Game;Simulation;StrategyGame;
Keywords=factory;recycling;management;simulation;robots;
StartupNotify=true
StartupWMClass=RecyclingFactory
EOF

chmod +x "$DESKTOP_DIR/$DESKTOP_NAME.desktop"

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

echo
echo "============================================================"
echo "Installation complete!"
echo "============================================================"
echo
echo "You can now:"
echo "  - Find 'Recycling Factory' in your application menu"
echo "  - Run from terminal: RecyclingFactory"
echo "  - Run directly: $INSTALL_DIR/RecyclingFactory"
echo
echo "To uninstall, run: $SCRIPT_DIR/uninstall.sh"
