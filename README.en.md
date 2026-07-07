# sticker-forge

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)
[![Local-first](https://img.shields.io/badge/local--first-no_backend-brightgreen.svg)](docs/DEVELOPMENT.md)
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
- Local 3x3 grid splitting with 3% inset (handles non-divisible sizes like 1024×1024).
- Green or magenta chroma-key background cleanup with despill.
- Selection of 8 stickers from a 9-cell grid.
- LINE ZIP export with `01.png`–`08.png`, `main.png`, `tab.png`, and README.
- 9 PNG-only ZIP export for non-LINE use.
- ZIP structure validation and pre-export preview metadata.
- Native Windows GUI as the main executable, with a separate CLI executable and an offline HTML fallback.

## Entry Points

| Entry | Notes |
|-------|-------|
| `sticker-forge.exe` | Native Windows GUI, no console window |
| `sticker-forge-cli.exe` / `python -m sticker_forge` | Command line, `--lang zh-Hant\|en` |
| `app/index.html` | Offline HTML workspace, ZIP built locally with no CDN |

## Install From Source

```powershell
python -m pip install -e ".[dev,packaging]"
python -m pytest
python -m sticker_forge --lang en prompt
python -m sticker_forge --lang en app
```

## Build Windows Executable

```powershell
.\packaging\build-windows.ps1
```

The script installs `.[dev,packaging]`, runs tests, builds with PyInstaller, and smoke-tests `sticker-forge.exe --smoke` / `sticker-forge-cli.exe --help`. It uses `%TEMP%` for PyInstaller build/dist folders to avoid OneDrive file-locking in the repo directory. See [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) for details.

## CLI

```powershell
python -m sticker_forge --lang en prompt
python -m sticker_forge split examples\grid.png -o outputs\cells --inset-ratio 0.03
python -m sticker_forge cleanup examples\cell.png -o outputs\cell-clean.png --chroma-key green
python -m sticker_forge preview examples\grid.png --select 1,2,3,4,5,6,7,8
python -m sticker_forge export examples\grid.png -o outputs\line-stickers.zip --select 1,2,3,4,5,6,7,8
python -m sticker_forge stickers examples\grid.png -o outputs\transparent-stickers.zip
python -m sticker_forge validate outputs\line-stickers.zip
```

## Project Structure

```text
.
├── src/sticker_forge/      # Local toolkit core
├── app/                    # Offline HTML workspace
├── prompts/                # Prompt templates
├── packaging/              # Windows exe build scripts
├── tests/                  # Automated tests
├── examples/               # Input location, no infringing assets
├── docs/                   # Maintainer docs (DEVELOPMENT / DECISIONS / LINE_SUBMISSION)
└── reference/upstream-line-sticker-studio/   # Upstream reference, not the target architecture
```

## Roadmap

Version **v0.4.0**: local-first LINE static sticker toolkit with three entry points (CLI, native Windows GUI, offline HTML). `python -m pytest` passes.

### ✅ Done

- Local-first direction; reusable logic extracted from upstream (split inset, chroma-key, ZIP spec, LINE sizes).
- Prompt templates (Chinese/English, text/no-text, green/magenta, risk reminders).
- Image core: 3x3 split, cleanup, resize/padding, main/tab image, preview metadata.
- Export: LINE ZIP, PNG-only ZIP, `validate` and `preview` commands.
- Three entry points and PyInstaller packaging; released `v0.1.0` and `v0.2.0`.

### 🔧 2026-07-07 consistency fixes

- **Split sizing**: `split_grid` no longer requires divisible dimensions; it floors and drops edge remainder (matching the web app), so the common 1024×1024 AI export works in CLI/GUI/web.
- **`--key-color`**: removed the dead flag from `export`/`stickers`/`preview` (that path always uses green/magenta score-based cleanup); kept on `cleanup`.
- **Web despill**: `app/app.js` now despills to match Python, so all three paths produce identical output (verified 60/60 pixels).
- **Packaging verified**: PyInstaller build tested — GUI `--smoke`, CLI export/validate, and bundled resources all pass.
- **Cleanup on by default**: `export`/`stickers`/`preview` now remove the background by default (LINE requires transparent backgrounds, and the split step fills the key color specifically for removal). Use `--keep-background` to keep the solid fill.
- **`validate` checks transparency**: `validate` now flags fully opaque stickers (background not removed), catching the most common LINE rejection reason.

See [`REVIEW.md`](REVIEW.md) and [`docs/DECISIONS.md`](docs/DECISIONS.md).

### 🚀 New in v0.4.0

- **Prompt dropdown suggestions**: character / theme / tone / style / language and the 8 text and action slots offer dropdown suggestions — pick one when you are short on ideas, or type your own. The native GUI uses editable comboboxes, the HTML app uses `datalist`, and suggestions switch with the zh/en language.

### 🚀 New in v0.3.0

- **Drag-and-drop import** in the offline HTML workspace (native, zero-dep, browser-verified).
- **Windows icon** for the GUI/CLI executables (`packaging/icon.ico`).
- **Legacy cleanup**: removed `reference/.../worker/` (Cloudflare/Gemini backend) and the campaign-checker CI; kept the upstream UI reference for provenance.

### ⏳ Remaining (mostly decided)

- **Decided against** (see [`docs/DECISIONS.md`](docs/DECISIONS.md)): installer/auto-update (needs an update server, conflicts with local-first), user-data/temp directory (no hidden data written), tkinter GUI drag-drop (avoids an extra dependency).
- **Optional future**: per-sticker re-slice and preview zoom.
- Decide user data and temporary file locations.
- Remove no-longer-needed `reference/.../worker/` and upstream hosted config.

## License

This project keeps the original MIT License from the upstream fork. See [`LICENSE`](LICENSE) and [`NOTICE.md`](NOTICE.md).
