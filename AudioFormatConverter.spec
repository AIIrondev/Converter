# -*- mode: python ; coding: utf-8 -*-
# MediaFormatConverter PyInstaller Specification
# Updated for Multiple Input Folders and Video Format support

import sys
from pathlib import Path

a = Analysis(
    ['audio_format_converter.py'],
    pathex=[],
    binaries=[],
    datas=[('bin', 'bin')] if Path('bin').exists() else [],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'threading',
        'queue',
        'concurrent.futures',
        'subprocess',
        'pathlib',
        'argparse',
        'urllib.request',
        'zipfile',
        'tempfile',
        'shutil'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy'],  # Exclude unused heavy libraries
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MediaFormatConverter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if Path('icon.ico').exists() else None,
    version_file=None,
    uac_admin=False,  # Set to True if admin privileges needed
    manifest=None,
)
