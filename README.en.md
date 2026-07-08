# sticker-forge

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)
[![Local-first](https://img.shields.io/badge/local--first-no_backend-brightgreen.svg)](docs/DEVELOPMENT.md)
[![LINE static stickers](https://img.shields.io/badge/LINE-static_stickers-00B900.svg)](prompts/line-static-3x3.md)
[![Tests: pytest](https://img.shields.io/badge/tests-pytest-blueviolet.svg)](tests)

[繁體中文](README.md) | English

`sticker-forge` is a local-first toolkit for making chat sticker packs. It focuses on LINE static stickers and can also export to Telegram, WhatsApp, Discord and Signal sizes/formats. It does not run an AI server, host API keys, upload user images, or automate submission. Users generate a 3x3 sticker grid with ChatGPT, Gemini, or another image tool, then import that image back into the local app for cleanup and export.

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
- Native Windows desktop GUI (a pywebview window rendering the HTML UI, backed by the Python core) plus a separate CLI executable.

## Entry Points

| Entry | Notes |
|-------|-------|
| `sticker-forge.exe` | Desktop GUI: a pywebview window rendering the `app/` HTML UI; split/cleanup/export all run in the local Python core. No console. |
| `sticker-forge-cli.exe` / `python -m sticker_forge` | Command line, `--lang zh-Hant\|en` |

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

Version **v0.8.0**: local-first sticker-pack toolkit (LINE and other platforms). The desktop GUI (a pywebview window rendering the HTML) and the CLI share one Python core. `python -m pytest` passes.

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

### 🚀 New in v0.8.0

- **Larger LINE packs (8/16/24/32/40)**: use "Add grid" to accumulate multiple 3×3 grids into a bigger tile pool, tick the stickers you want, and export a pack of the matching size.
- **Pick main/tab sticker**: no longer fixed to the first sticker — choose which one is `main.png` and which is `tab.png`.
- **Reorder stickers**: ▲▼ per tile to set the `01…NN` output order.
- CLI: `sticker-forge export grid1.png grid2.png -o out.zip --select 1,…,16 --main 2 --tab 3`.

### 🚀 New in v0.7.0

- **Multi-platform export**: beyond LINE, export the stickers sized and formatted for **Telegram (512 PNG), WhatsApp (512 WebP + 96 tray), Discord (320 PNG), and Signal (512 PNG)**. Pick a platform in the GUI and click "Export for platform", or run `sticker-forge platform <grid> -o out.zip --target telegram`. (Inspired by the sticker-convert and StampNyaa references.)

### 🚀 New in v0.6.0

- **Per-sticker zoom**: click any tile thumbnail to open an enlarged view (on a transparency checkerboard) to inspect the cleanup.
- **Per-sticker clean / reset**: the zoom view can clean up just that tile or reset it to the original slice. Both "clean all" and per-tile clean now work from the original slice, so re-running at a different strength never stacks fringe artifacts.

### 🚀 New in v0.5.0

- **One UI codebase**: the desktop GUI moved from tkinter to a **pywebview window rendering the HTML UI**, with split/cleanup/export/prompt all handled by the local Python core (JS is UI-only). The previously duplicated tkinter + JavaScript implementations are now a single core, ending the parity-maintenance burden. Dependency: pywebview (uses the built-in WebView2 on Windows).

### 🚀 New in v0.4.0

- **Prompt dropdown suggestions**: character / theme / tone / style / language and the 8 text and action slots offer dropdown suggestions — pick one when you are short on ideas, or type your own. The native GUI uses editable comboboxes, the HTML app uses `datalist`, and suggestions switch with the zh/en language.

### 🚀 New in v0.3.0

- **Drag-and-drop import** in the offline HTML workspace (native, zero-dep, browser-verified).
- **Windows icon** for the GUI/CLI executables (`packaging/icon.ico`).
- **Legacy cleanup**: removed `reference/.../worker/` (Cloudflare/Gemini backend) and the campaign-checker CI; kept the upstream UI reference for provenance.

### 💡 Reference-inspired candidates

Drawn from the fork source ([yazelin/line-sticker-studio](https://github.com/yazelin/line-sticker-studio)) and the other reference projects (sticker-convert, StampNyaa, signal-sticker-tool, LINE Creators Market):

- **More prompt templates**: LINE emoji (different size/count), message stickers, more themes.
- **Sticker naming**: name/label individual stickers before export.
- **More platform formats**: a full Signal pack (with manifest), animated stickers (beyond the current static scope).
- **ML background removal**: for non-chroma-key sources (e.g. rembg). **Leaning no**: first run downloads a model (breaks offline use) and the dependency is heavy — against the lightweight local-first principle.
- **Grid history**: keep imported grids for reuse. **Leaning no**: needs persistent storage, which conflicts with the current `private_mode` "no persistent data" decision.

### ⏳ Decided

- **Decided against** (see [`docs/DECISIONS.md`](docs/DECISIONS.md)): auto-update (needs an update server, conflicts with local-first) and an installer (the portable unzip-and-run zip fits local-first better than an install flow).
- **Resolved by the architecture**: desktop drag-and-drop (the webview's HTML dropzone already handles it, so the old tkinter drag-drop need is gone); user-data/temp (WebView2 runs with `private_mode`, an ephemeral profile, so nothing persistent is written).
- Decide user data and temporary file locations.
- Remove no-longer-needed `reference/.../worker/` and upstream hosted config.

## License

This project keeps the original MIT License from the upstream fork. See [`LICENSE`](LICENSE) and [`NOTICE.md`](NOTICE.md).
