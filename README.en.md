# sticker-forge

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)
[![Local-first](https://img.shields.io/badge/local--first-no_backend-brightgreen.svg)](docs/DEVELOPMENT.md)
[![LINE sticker packs](https://img.shields.io/badge/LINE-sticker_packs-00B900.svg)](prompts/line-static-3x3.md)
[![Tests: pytest](https://img.shields.io/badge/tests-pytest-blueviolet.svg)](tests)

[繁體中文](README.md) | English

`sticker-forge` is a local-first toolkit for making chat sticker packs. It supports LINE static stickers, Big Stickers, emoji, message stickers, animated stickers, and exports for Telegram, WhatsApp, Discord and Signal sizes/formats. It does not run an AI server, host API keys, upload user images, or automate submission. Users generate sticker assets with ChatGPT, Gemini, or another image tool, then import them back into the local app for cleanup and export.

## Workflow

1. Choose a sticker theme, character, tone, text, and output settings in `sticker-forge`.
2. Copy the generated prompt.
3. Generate a 3x3 sticker grid, or multiple GIF/APNG files for animated stickers, in an external AI image tool.
4. Import the generated image back into `sticker-forge`.
5. Split, clean up, preview, select/reorder stickers, and prepare animated files locally.
6. Export a ZIP for LINE Creators Market or another supported platform.

The current scope covers LINE static stickers, Big Stickers, emoji, message stickers, animated stickers, and multi-platform size exports. This project does not auto-submit to LINE and does not guarantee review approval.

## Features

- Traditional Chinese and English CLI/app language support.
- 3x3 LINE sticker prompt templates, with text and no-text variants.
- Local 3x3 grid splitting with 3% inset (handles non-divisible sizes like 1024×1024).
- Multiple animated GIF/APNG import for LINE animated stickers.
- Green or magenta chroma-key background cleanup with despill.
- Sticker selection, ordering, and main/tab image selection.
- LINE static sticker, Big Stickers, emoji, message sticker, animated sticker ZIP exports.
- 9 PNG-only ZIP export and multi-platform ZIP exports for non-LINE use.
- ZIP structure validation and pre-export preview metadata.
- Native Windows desktop GUI (a pywebview window rendering the HTML UI, backed by the Python core) plus a separate CLI executable.

## Entry Points

| Entry | Notes |
|-------|-------|
| `sticker-forge.exe` | Desktop GUI: a pywebview window rendering the `app/` HTML UI; split/cleanup/export all run in the local Python core. No console. |
| `sticker-forge-cli.exe` / `python -m sticker_forge` | Command line, `--lang zh-Hant\|en` |

General usage is documented in [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) (Traditional Chinese). Source install and packaging notes are in [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md).

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
├── docs/                   # User and maintainer docs (USER_GUIDE / DEVELOPMENT / DECISIONS / LINE_SUBMISSION)
├── README.md / README.en.md / CHANGELOG.md / REVIEW.md
```

## Roadmap

Version **v0.16.0**: local-first sticker-pack toolkit (LINE stickers/Big Stickers/emoji/message/animated stickers and other platforms). The desktop GUI (a pywebview window rendering the HTML) and the CLI share one Python core. `python -m pytest` passes.

### ✅ Done

- Local-first direction; the needed fork-source concepts have been folded into the local Python core, pywebview GUI, and project docs.
- Prompt templates (Chinese/English, text/no-text, green/magenta, risk reminders).
- Image core: 3x3 split, cleanup, resize/padding, main/tab image, preview metadata.
- Export: LINE static sticker, Big Stickers, emoji, message sticker, animated sticker ZIPs, PNG-only ZIP, platform ZIPs, `validate` and `preview` commands.
- PyInstaller Windows packaging and releases through `v0.16.0` (GitHub Releases with SHA256 checksums).
- Desktop drag-and-drop import (the webview's HTML dropzone); WebView2 runs with `private_mode`, an ephemeral profile, so nothing persistent is written.
- User guide and reproducible local sample asset generator (generated images and ZIPs are not committed).
- Signal platform export now includes `cover.png`, `signal_manifest.json`, and `validate --signal`.
- LINE Big Stickers export now includes CLI / GUI support and `validate --big`.

Detailed version history is in [`CHANGELOG.md`](CHANGELOG.md); design decisions are in [`docs/DECISIONS.md`](docs/DECISIONS.md).

### Next

- Run one manual LINE Creators Market upload check with non-infringing assets, especially for animated APNG stickers.
- Verify LINE pop-up / effect sticker APNG specs one by one before adding them.

### ⏳ Decided

- **Decided against** (see [`docs/DECISIONS.md`](docs/DECISIONS.md)): auto-update (needs an update server, conflicts with local-first) and an installer (the portable unzip-and-run zip fits local-first better than an install flow).

## Credits

These projects informed the design as references only, not runtime dependencies. The fork source `yazelin/line-sticker-studio` is preserved through MIT attribution, external links, and git history; this repo no longer vendors upstream reference source. GPL / unlicensed projects can't be merged into an MIT repo, so they are credited for concepts only. Full credits in [`NOTICE.md`](NOTICE.md).

| Project | License | What it informed |
| --- | --- | --- |
| [LINE Creators Market](https://creator.line.me/) / [LINE Sticker Maker](https://creator.line.me/en/stickermaker/) | Official | Static sticker specs, pack sizes, transparency, submission flow. |
| [LINE Big Stickers guideline](https://creator.line.me/en/guideline/bigsticker/) | Official spec | Big Stickers pack sizes, 396x660 maximum size, main/tab images, and transparent-background requirements. |
| [Signal Stickers Support](https://support.signal.org/hc/en-us/articles/360031836512-Stickers) | Official support docs | Signal sticker size, format, cover, title, author, and emoji-assignment requirements. |
| [yazelin/line-sticker-studio](https://github.com/yazelin/line-sticker-studio) | MIT (**fork source**) | 3x3 grid, chroma-key, ZIP structure, submission notes, UI flow; provenance kept through attribution and git history, no longer vendored. |
| [laggykiller/sticker-convert](https://github.com/laggykiller/sticker-convert) | GPL-2.0 | The multi-platform export concept; implemented independently from public specs. |
| [MarvNC/StampNyaa](https://github.com/MarvNC/StampNyaa) | Unlicensed | The "use LINE stickers on other platforms" desktop workflow. |
| [ittner/signal-sticker-tool](https://github.com/ittner/signal-sticker-tool) | GPL-3.0 | Signal sticker-pack packaging (possible future feature). |
| [suchipi/line-sticker-downloader](https://github.com/suchipi/line-sticker-downloader) | MIT | Fetching existing LINE packs (possible future import feature). |
| [curegit/line-sticker-downloader](https://github.com/curegit/line-sticker-downloader) | WTFPL | Browser/CLI download and ZIP output patterns. |

## License

This project keeps the original MIT License from the upstream fork. See [`LICENSE`](LICENSE) and [`NOTICE.md`](NOTICE.md).
