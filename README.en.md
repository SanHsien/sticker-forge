# sticker-forge

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)
[![Local-first](https://img.shields.io/badge/local--first-no_backend-brightgreen.svg)](docs/DEVELOPMENT.md)
[![LINE sticker packs](https://img.shields.io/badge/LINE-sticker_packs-00B900.svg)](prompts/line-static-3x3.md)
[![Tests: pytest](https://img.shields.io/badge/tests-pytest-blueviolet.svg)](tests)

[繁體中文](README.md) | English

`sticker-forge` is a local-first toolkit for making chat sticker packs. It supports LINE static stickers, emoji, message stickers, animated stickers, and exports for Telegram, WhatsApp, Discord and Signal sizes/formats. It does not run an AI server, host API keys, upload user images, or automate submission. Users generate sticker assets with ChatGPT, Gemini, or another image tool, then import them back into the local app for cleanup and export.

## Workflow

1. Choose a sticker theme, character, tone, text, and output settings in `sticker-forge`.
2. Copy the generated prompt.
3. Generate a 3x3 sticker grid, or multiple GIF/APNG files for animated stickers, in an external AI image tool.
4. Import the generated image back into `sticker-forge`.
5. Split, clean up, preview, select/reorder stickers, and prepare animated files locally.
6. Export a ZIP for LINE Creators Market or another supported platform.

The current scope covers LINE static stickers, emoji, message stickers, animated stickers, and multi-platform size exports. This project does not auto-submit to LINE and does not guarantee review approval.

## Features

- Traditional Chinese and English CLI/app language support.
- 3x3 LINE sticker prompt templates, with text and no-text variants.
- Local 3x3 grid splitting with 3% inset (handles non-divisible sizes like 1024×1024).
- Multiple animated GIF/APNG import for LINE animated stickers.
- Green or magenta chroma-key background cleanup with despill.
- Sticker selection, ordering, and main/tab image selection.
- LINE static sticker, emoji, message sticker, animated sticker ZIP exports.
- 9 PNG-only ZIP export and multi-platform ZIP exports for non-LINE use.
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
sticker-forge-gui --lang en
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
├── app/                    # HTML/CSS/JS frontend assets loaded by the pywebview GUI
├── prompts/                # Prompt templates
├── packaging/              # Windows exe build scripts
├── tests/                  # Automated tests
├── examples/               # Input location, no infringing assets
├── docs/                   # Maintainer docs (DEVELOPMENT / DECISIONS / LINE_SUBMISSION)
```

## Roadmap

Version **v0.13.0**: local-first sticker-pack toolkit (LINE stickers/emoji/message/animated stickers and other platforms). The desktop GUI (a pywebview window rendering the HTML) and the CLI share one Python core. `python -m pytest` passes.

### ✅ Done

- Local-first direction; the needed fork-source concepts have been folded into the local Python core, pywebview GUI, and project docs.
- Prompt templates (Chinese/English, text/no-text, green/magenta, risk reminders).
- Image core: 3x3 split, cleanup, resize/padding, main/tab image, preview metadata.
- Export: LINE static sticker, emoji, message sticker, animated sticker ZIPs, PNG-only ZIP, platform ZIPs, `validate` and `preview` commands.
- PyInstaller Windows packaging and releases through `v0.13.0` (GitHub Releases with SHA256 checksums).
- Desktop drag-and-drop import (the webview's HTML dropzone); WebView2 runs with `private_mode`, an ephemeral profile, so nothing persistent is written.

### 🔧 2026-07-07 consistency fixes

- **Split sizing**: `split_grid` no longer requires divisible dimensions; it floors and drops edge remainder (matching the web app), so the common 1024×1024 AI export works in CLI/GUI/web.
- **`--key-color`**: removed the dead flag from `export`/`stickers`/`preview` (that path always uses green/magenta score-based cleanup); kept on `cleanup`.
- **Web despill**: `app/app.js` now despills to match Python, so all three paths produce identical output (verified 60/60 pixels).
- **Packaging verified**: PyInstaller build tested — GUI `--smoke`, CLI export/validate, and bundled resources all pass.
- **Cleanup on by default**: `export`/`stickers`/`preview` now remove the background by default (LINE requires transparent backgrounds, and the split step fills the key color specifically for removal). Use `--keep-background` to keep the solid fill.
- **`validate` checks transparency**: `validate` now flags fully opaque stickers (background not removed), catching the most common LINE rejection reason.

See [`REVIEW.md`](REVIEW.md) and [`docs/DECISIONS.md`](docs/DECISIONS.md).

### 🚀 New in v0.13.0

- **Animated stickers: "import multiple animated GIFs" model + GUI.** Corrects the v0.12.0 input shape — a non-professional user generating with AI ends up with **one animated GIF per sticker**, not an animated grid. Now you **import 8/16/24 animated GIF/APNG files (one per sticker)** → per-frame background cleanup, resize to ≤320×270 (one side ≥270), and **APNG (5–20 frames)**, plus an animated 240×240 main and a static 96×74 tab, following the official spec ([creator.line.me/en/guideline/animationsticker](https://creator.line.me/en/guideline/animationsticker/)). GUI "Import animated" (multi-file) + "Export animated" buttons (static exports are blocked in animated mode); CLI `sticker-forge animated a.gif b.gif … -o out.zip`. **16/24 just means importing more files** — no multi-grid needed.

### 🚀 New in v0.12.0

- **LINE animated sticker export (CLI, first cut)**: APNG animated sticker packs per the official spec (≤320×270, 5–20 frames, animated main + static tab). (v0.13.0 switched the input to "import multiple animated GIFs" and added the GUI.)

### 🚀 New in v0.11.0

- **LINE message sticker export**: message stickers (the sender types a short message onto the sticker) — **8/16/24 images, up to 370×320, no baked-in margin (LINE adds one), main 240×240 + tab 96×74** — following the official spec ([creator.line.me/en/guideline/messagesticker](https://creator.line.me/en/guideline/messagesticker/)). GUI "Export message stickers" button; CLI `sticker-forge message <grid…> -o out.zip`. Text position/font are set in LINE's editor.

### 🚀 New in v0.10.0

- **LINE custom emoji export**: export the tile pool as a LINE emoji set — **8–40 images, 180×180 transparent PNG, filenames `001.png…` plus a 96×74 chat thumbnail** — following the official spec ([creator.line.me/en/guideline/emoji](https://creator.line.me/en/guideline/emoji/)). GUI "Export LINE emoji" button; CLI `sticker-forge emoji <grid…> -o out.zip --thumb 1` and `validate --emoji`.

### 🚀 New in v0.9.0

- **Theme presets**: one click applies a themed starter pack (healing bear / office cat / couple bears / festive) — filling character/theme/tone/style plus 8 texts and 8 actions, ready to tweak. GUI dropdown; CLI `sticker-forge prompt --preset office-cat`.
- **Pack title / author (GUI)**: set the LINE pack title and author in the GUI (written into the ZIP's README; the CLI already had `--title` / `--author`).

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
- **Legacy cleanup**: removed the legacy Cloudflare/Gemini backend, campaign-checker CI, and now-unused upstream vendored reference source; kept attribution and external fork links for provenance.

### 💡 Reference-inspired candidates

Drawn from the fork source ([yazelin/line-sticker-studio](https://github.com/yazelin/line-sticker-studio)) and the other reference projects (sticker-convert, StampNyaa, signal-sticker-tool, LINE Creators Market):

- **More platform formats**: a full Signal pack (with manifest).
- **Big / pop-up / effect stickers**: other LINE sticker types, each with its own spec — can be added after verifying each one.
- **ML background removal**: for non-chroma-key sources (e.g. rembg). **Leaning no**: first run downloads a model (breaks offline use) and the dependency is heavy — against the lightweight local-first principle.
- **Grid history**: keep imported grids for reuse. **Leaning no**: needs persistent storage, which conflicts with the current `private_mode` "no persistent data" decision.

### ⏳ Decided

- **Decided against** (see [`docs/DECISIONS.md`](docs/DECISIONS.md)): auto-update (needs an update server, conflicts with local-first) and an installer (the portable unzip-and-run zip fits local-first better than an install flow).

## Credits

These projects informed the design as references only, not runtime dependencies. The fork source `yazelin/line-sticker-studio` is preserved through MIT attribution, external links, and git history; this repo no longer vendors upstream reference source. GPL / unlicensed projects can't be merged into an MIT repo, so they are credited for concepts only. Full credits in [`NOTICE.md`](NOTICE.md).

| Project | License | What it informed |
| --- | --- | --- |
| [LINE Creators Market](https://creator.line.me/) / [LINE Sticker Maker](https://creator.line.me/en/stickermaker/) | Official | Static sticker specs, pack sizes, transparency, submission flow. |
| [yazelin/line-sticker-studio](https://github.com/yazelin/line-sticker-studio) | MIT (**fork source**) | 3x3 grid, chroma-key, ZIP structure, submission notes, UI flow; provenance kept through attribution and git history, no longer vendored. |
| [laggykiller/sticker-convert](https://github.com/laggykiller/sticker-convert) | GPL-2.0 | The multi-platform export concept; implemented independently from public specs. |
| [MarvNC/StampNyaa](https://github.com/MarvNC/StampNyaa) | Unlicensed | The "use LINE stickers on other platforms" desktop workflow. |
| [ittner/signal-sticker-tool](https://github.com/ittner/signal-sticker-tool) | GPL-3.0 | Signal sticker-pack packaging (possible future feature). |
| [suchipi/line-sticker-downloader](https://github.com/suchipi/line-sticker-downloader) | MIT | Fetching existing LINE packs (possible future import feature). |
| [curegit/line-sticker-downloader](https://github.com/curegit/line-sticker-downloader) | WTFPL | Browser/CLI download and ZIP output patterns. |

## License

This project keeps the original MIT License from the upstream fork. See [`LICENSE`](LICENSE) and [`NOTICE.md`](NOTICE.md).
