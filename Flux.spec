# -*- mode: python ; coding: utf-8 -*-
# Flux Windows build specification.
# Build with: python -m PyInstaller Flux.spec --noconfirm

from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

project_root = Path.cwd()

hiddenimports = []
for package in ("themes", "animations", "ui", "utils", "database"):
    hiddenimports += collect_submodules(package)

a = Analysis(
    ["main.py"],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        ("assets", "assets"),
        ("database/flux.db", "database"),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Flux",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/flux.ico",
    version="version_info.txt",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Flux",
)
