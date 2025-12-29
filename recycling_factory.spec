# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Recycling Factory game.

To build the executable:
    pyinstaller recycling_factory.spec

Or use the build script:
    python build.py
"""

import os
import sys

# Get the project root directory
project_root = os.path.dirname(os.path.abspath(SPEC))

block_cipher = None

# Collect all data files
datas = [
    # Include data directory with JSON configs
    (os.path.join(project_root, 'data'), 'data'),
    # Include config.py
    (os.path.join(project_root, 'config.py'), '.'),
]

# Hidden imports that PyInstaller might miss
hiddenimports = [
    'pygame',
    'pygame.locals',
    'pygame.font',
    'pygame.mixer',
    'pygame.image',
    'pygame.transform',
    'pygame.draw',
    'pygame.display',
    'pygame.event',
    'pygame.time',
    'pygame.key',
    'pygame.mouse',
    'pygame.rect',
    'pygame.surface',
    'json',
    'random',
    'math',
    'heapq',
    'collections',
    'typing',
    'enum',
    'dataclasses',
    'pathlib',
    'os',
    'sys',
]

a = Analysis(
    [os.path.join(project_root, 'main.py')],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'PIL',
        'cv2',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='RecyclingFactory',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want console window for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here when available: icon='assets/icon.ico'
)
