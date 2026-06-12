# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for screenshot_tool.

Build:  pyinstaller screenshot_tool.spec
Output: dist/screenshot_tool/screenshot_tool.exe
"""

import sys
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# keyboard 库有隐式 import，PyInstaller 静态分析可能漏
hiddenimports = []
hiddenimports += collect_submodules('keyboard')
hiddenimports += collect_submodules('mss')

a = Analysis(
    ['screenshot_tool.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # onedir 关键：可执行文件不含二进制
    name='screenshot_tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,           # windowed：不弹 console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='screenshot_tool',
)
