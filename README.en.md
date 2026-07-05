# sticker-forge

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)
[![Local-first](https://img.shields.io/badge/local--first-no_backend-brightgreen.svg)](docs/ARCHITECTURE.md)
[![LINE static stickers](https://img.shields.io/badge/LINE-static_stickers-00B900.svg)](prompts/line-static-3x3.md)
[![Tests: pytest](https://img.shields.io/badge/tests-pytest-blueviolet.svg)](tests)

[繁體中文](README.md) | English

`sticker-forge` is a local-first toolkit for preparing LINE static sticker packs. It does not run an AI server, host API keys, upload user images, or automate LINE submission. Users generate a 3x3 sticker grid with ChatGPT, Gemini, or another image tool, then import that image back into the local app for cleanup and export.

## Workflow

1. Choose a sticker theme, character, tone, text, and output settings in `sticker-forge`.
2. Copy the generated prompt.
3. Generate a 3x3 sticker grid in an external AI image tool.
4. Import the generated image back into `sticker-forge`.
5. Split, clean up, preview, and select 8 stickers locally.
6. Export a ZIP for LINE Creators Market static stickers.

The current scope is LINE static sticker packs. This project does not auto-submit to LINE and does not guarantee review approval.

## Features

- Traditional Chinese and English CLI/app language support.
- 3x3 LINE static sticker prompt templates, with text and no-text variants.
- Local 3x3 grid splitting with 3% inset.
- Green or magenta chroma-key background cleanup.
- Selection of 8 stickers from a 9-cell grid.
- LINE ZIP export with `01.png` to `08.png`, `main.png`, `tab.png`, and README.
- 9 PNG-only ZIP export for non-LINE use.
- ZIP structure validation.
- Preview metadata and selection validation model.
- Native Windows GUI as the main executable.
- CLI executable split out as `sticker-forge-cli.exe`.
- Local HTML workspace kept as an offline fallback.

## Install From Source

```powershell
python -m pip install -e ".[dev,packaging]"
python -m pytest
python -m sticker_forge --lang en prompt
python -m sticker_forge --lang en app
sticker-forge-gui --lang en
```

## Build Windows Executable

```powershell
.\packaging\build-windows.ps1
```

The build script installs `.[dev,packaging]`, runs tests, builds with PyInstaller, smoke-tests `sticker-forge.exe --smoke`, and checks `sticker-forge-cli.exe --help`.

Build output:

```text
%TEMP%\sticker-forge-pyinstaller-dist\sticker-forge\sticker-forge.exe
%TEMP%\sticker-forge-pyinstaller-dist\sticker-forge\sticker-forge-cli.exe
```

`sticker-forge.exe` opens the native GUI without a console window. `sticker-forge-cli.exe` is the console command-line tool. The script uses `%TEMP%` for PyInstaller build/dist folders to avoid OneDrive file-locking issues in the repo directory.

## CLI

```powershell
python -m sticker_forge --lang en prompt
python -m sticker_forge --lang en prompt --no-text --output outputs\prompt.md
python -m sticker_forge split examples\grid.png -o outputs\cells --inset-ratio 0.03
python -m sticker_forge cleanup examples\cell.png -o outputs\cell-clean.png --chroma-key green
python -m sticker_forge preview examples\grid.png --select 1,2,3,4,5,6,7,8
python -m sticker_forge export examples\grid.png -o outputs\line-stickers.zip --select 1,2,3,4,5,6,7,8 --chroma-key
python -m sticker_forge stickers examples\grid.png -o outputs\transparent-stickers.zip --chroma-key
python -m sticker_forge validate outputs\line-stickers.zip
python -m sticker_forge --lang en app
```

## Project Structure

```text
.
├── src/sticker_forge/      # Local toolkit core
├── app/                    # Offline HTML workspace
├── prompts/                # Prompt templates
├── packaging/              # Windows exe build scripts
├── tests/                  # Automated tests
├── examples/               # Example notes, no infringing assets
├── docs/                   # Project docs
└── reference/
    └── upstream-line-sticker-studio/
```

## Roadmap

Status: **Phase 0-6 are complete for the publishable local workflow; `v0.2.0` fixes Windows exe startup and adds a native GUI.**

### ✅ Done

- [x] Local-first project direction.
- [x] Prompt templates for LINE static sticker 3x3 grids.
- [x] Python CLI and testable image processing modules.
- [x] 3x3 splitting, chroma-key cleanup, LINE ZIP export, PNG-only ZIP export, ZIP validation.
- [x] Preview metadata model for sticker selection checks.
- [x] Offline local HTML workspace.
- [x] PyInstaller Windows packaging.
- [x] First Windows release artifact: `v0.1.0`.
- [x] Native GUI Windows release artifact: `v0.2.0`.
- [x] Traditional Chinese and English README.
- [x] Traditional Chinese and English CLI/app language support.
- [x] Native GUI main executable.
- [x] Separate CLI executable.
- [x] CLI `preview` command and HTML pre-export preview controls.

### ⏳ Next

- [ ] Drag-and-drop import.
- [ ] More detailed preview zoom and per-sticker adjustment.
- [ ] Decide user data and temporary file locations.
- [ ] Windows icon, installer, and update check.

## Related References

These services and projects are references only. They are not runtime dependencies.

| Name | Type | Useful reference |
| --- | --- | --- |
| [LINE Creators Market](https://creator.line.me/) | Official platform | Sticker, emoji, and theme creation and sales flow. |
| [LINE Sticker Maker](https://creator.line.me/en/stickermaker/) | Official mobile app | Mobile sticker creation and manual submission flow. |
| [yazelin/line-sticker-studio](https://github.com/yazelin/line-sticker-studio) | Upstream source | 3x3 grid, chroma-key, ZIP structure, submission notes, and UI flow. |
| [laggykiller/sticker-convert](https://github.com/laggykiller/sticker-convert) | Sticker conversion tool | GUI + CLI packaging and multi-platform sticker conversion. |
| [suchipi/line-sticker-downloader](https://github.com/suchipi/line-sticker-downloader) | LINE asset downloader | CLI output flow for LINE stickers and emojis. |
| [curegit/line-sticker-downloader](https://github.com/curegit/line-sticker-downloader) | LINE asset downloader | Browser/CLI modes and ZIP output. |
| [MarvNC/StampNyaa](https://github.com/MarvNC/StampNyaa) | LINE sticker desktop tool | Cross-platform desktop UI patterns. |
| [ittner/signal-sticker-tool](https://github.com/ittner/signal-sticker-tool) | Signal sticker CLI | Folder, metadata, and CLI packaging model. |

## License

This project keeps the original MIT License from the upstream fork. See [`LICENSE`](LICENSE) and [`NOTICE.md`](NOTICE.md).
