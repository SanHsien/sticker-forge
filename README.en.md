# Sticker Forge

[![Release](https://img.shields.io/github/v/release/SanHsien/sticker-forge?sort=semver)](https://github.com/SanHsien/sticker-forge/releases/latest)
[![CI](https://github.com/SanHsien/sticker-forge/actions/workflows/ci.yml/badge.svg)](https://github.com/SanHsien/sticker-forge/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)
[![Local-first](https://img.shields.io/badge/architecture-local--first-2E7D32.svg)](#privacy-and-product-boundaries)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Turn AI-generated character art into deliverable chat sticker packs.**

[繁體中文](README.md) · English

Sticker Forge is a Windows-first, local-processing sticker production tool. It does not manage your AI accounts or upload images to a Sticker Forge server. Generate artwork with ChatGPT, Gemini, or another tool of your choice, then bring the result back into Sticker Forge for slicing, background cleanup, outlining, sizing, preview, validation, and multi-platform export.

## Quick start

1. Download the Windows ZIP from [Latest Release](https://github.com/SanHsien/sticker-forge/releases/latest).
2. Extract it and run `sticker-forge.exe`.
3. Build a prompt in the GUI, or import images / GIF / APNG files you already generated.
4. Slice, clean, order, decorate, preview, and validate everything locally.
5. Export ZIPs or image assets for LINE or other chat platforms.

No hosted backend is required, and Sticker Forge never asks you to hand over an AI API key.

## Core workflow

```text
Theme / character / copy
        │
        ▼
 Sticker Forge builds a prompt
        │
        ▼
User chooses an external AI image tool
        │
        ▼
Import grid / PNG / GIF / APNG
        │
        ▼
Slice → clean → outline → order → preview → validate
        │
        ▼
LINE / Telegram / WhatsApp / Discord / Signal
```

This separation is intentional: image generation happens in the service you choose; Sticker Forge focuses on turning the results into production-ready assets. There is no hosted AI backend, shared quota, or centralized key management.

## What it does

- **Prompt generation** — build editable sticker prompts from a character, theme, tone, language, text, and actions, with text and no-text variants.
- **3×3 grid slicing** — split common AI sticker grids into individual assets, including non-even dimensions, selection, and ordering.
- **Background and edge cleanup** — green / magenta chroma key, `safe` / `balanced` / `aggressive` / `continuous` modes, plus advanced GUI tuning.
- **Outline and shadow** — `simple` white outline or `fancy` outline + feathering + shadow for better contrast on dark chat themes.
- **LINE export** — static stickers, Big Stickers, emoji, message stickers, animated stickers, pop-up stickers, and effect stickers.
- **Multi-platform export** — Telegram, WhatsApp, Discord, and Signal sizing and package structures.
- **Validation and preview** — check dimensions, counts, filenames, ZIP structure, main / tab images, and per-sticker previews.
- **GUI + CLI** — the desktop GUI and `python -m sticker_forge` / `sticker-forge` share the same Python core.

## Privacy and product boundaries

Sticker Forge processes and exports images locally:

- It does not operate a Sticker Forge image-upload service.
- It does not hold API keys for ChatGPT, Gemini, or other AI services.
- User images, generated ZIPs, and local temporary data do not belong in this repository.
- You choose the external image-generation service. Data sent to that service is governed by that service's own policies.
- Sticker Forge does not automatically upload or submit packs to LINE Creators Market.

Sticker Forge is not an official LINE product and cannot guarantee platform approval. Users remain responsible for trademarks, copyright, likeness rights, and other content rights.

## LINE and multi-platform support

| Type | Support |
|---|---|
| LINE static stickers | ✅ |
| LINE Big Stickers | ✅ |
| LINE emoji | ✅ |
| LINE message stickers | ✅ |
| LINE animated stickers | ✅ |
| LINE pop-up / effect stickers | ✅ |
| Telegram / WhatsApp / Discord / Signal | ✅ |

The local validator checks known file rules but cannot replace LINE Creators Market's actual platform validation. See [`docs/LINE_SUBMISSION.md`](docs/LINE_SUBMISSION.md) and [`docs/WINDOWS_VALIDATION.md`](docs/WINDOWS_VALIDATION.md) for manual submission and validation.

## Run from source

Requires Python 3.11+.

```powershell
python -m pip install -e ".[dev,gui]"
python -m sticker_forge
python -m pytest
```

Windows releases are built with PyInstaller. CI tests Python 3.11–3.14 and also builds and smoke-tests the Windows EXE on a Windows runner.

See [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) for architecture, packaging, and contributor details.

## Documentation

- [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) — normal usage, export modes, and troubleshooting.
- [`docs/LINE_SUBMISSION.md`](docs/LINE_SUBMISSION.md) — manual LINE Creators Market submission.
- [`docs/WINDOWS_VALIDATION.md`](docs/WINDOWS_VALIDATION.md) — Windows GUI, Release, and platform validation.
- [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) — architecture, tests, and packaging.
- [`docs/DECISIONS.md`](docs/DECISIONS.md) — important product and engineering decisions.
- [`CHANGELOG.md`](CHANGELOG.md) — version history.

## Origin and license

This repository is an MIT-licensed fork of [`yazelin/line-sticker-studio`](https://github.com/yazelin/line-sticker-studio). The upstream project started from a one-image → AI-generated LINE sticker workflow; this fork has moved toward a Windows local-first Python / pywebview production tool and removed the original web app / Worker vendored reference source.

See [`NOTICE.md`](NOTICE.md) for upstream attribution, modification history, and third-party notices. Sticker Forge is released under the [MIT License](LICENSE).
