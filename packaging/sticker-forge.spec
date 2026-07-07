# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

block_cipher = None
spec_dir = Path(SPECPATH)
repo_dir = spec_dir.parent
icon_path = str(spec_dir / "icon.ico")

datas = [
    (str(repo_dir / "prompts"), "prompts"),
    (str(repo_dir / "app"), "app"),
]

common_kwargs = {
    "pathex": [str(repo_dir / "src")],
    "binaries": [],
    "datas": datas,
    "hiddenimports": [],
    "hookspath": [],
    "hooksconfig": {},
    "runtime_hooks": [],
    "excludes": [],
    "win_no_prefer_redirects": False,
    "win_private_assemblies": False,
    "cipher": block_cipher,
    "noarchive": False,
}

gui_analysis = Analysis(
    [str(spec_dir / "sticker_forge_gui_entry.py")],
    **common_kwargs,
)
gui_pyz = PYZ(gui_analysis.pure, gui_analysis.zipped_data, cipher=block_cipher)
gui_exe = EXE(
    gui_pyz,
    gui_analysis.scripts,
    [],
    exclude_binaries=True,
    name="sticker-forge",
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
    icon=icon_path,
)

cli_analysis = Analysis(
    [str(spec_dir / "sticker_forge_cli_entry.py")],
    **common_kwargs,
)
cli_pyz = PYZ(cli_analysis.pure, cli_analysis.zipped_data, cipher=block_cipher)
cli_exe = EXE(
    cli_pyz,
    cli_analysis.scripts,
    [],
    exclude_binaries=True,
    name="sticker-forge-cli",
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
    icon=icon_path,
)

coll = COLLECT(
    gui_exe,
    cli_exe,
    gui_analysis.binaries,
    gui_analysis.zipfiles,
    gui_analysis.datas,
    cli_analysis.binaries,
    cli_analysis.zipfiles,
    cli_analysis.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="sticker-forge",
)
