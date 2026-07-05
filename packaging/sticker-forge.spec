# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

block_cipher = None
spec_dir = Path(SPECPATH)
repo_dir = spec_dir.parent

a = Analysis(
    [str(spec_dir / "sticker_forge_entry.py")],
    pathex=[str(repo_dir / "src")],
    binaries=[],
    datas=[
        (str(repo_dir / "prompts" / "line-static-3x3.md"), "prompts"),
        (str(repo_dir / "app"), "app"),
    ],
    hiddenimports=[],
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
    exclude_binaries=True,
    name="sticker-forge",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
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
    upx=True,
    upx_exclude=[],
    name="sticker-forge",
)
