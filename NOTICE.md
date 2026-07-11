# NOTICE

sticker-forge
Copyright 2026 SanHsien

This project is derived from [`yazelin/line-sticker-studio`](https://github.com/yazelin/line-sticker-studio), originally licensed under the MIT License.

Original work:

- Project: `line-sticker-studio`
- Author: `yazelin`
- License: MIT
- Original copyright notice: `Copyright (c) 2026 yazelin`

This repository keeps the original MIT license notice in [`LICENSE`](LICENSE). Modifications, documentation, and future project-specific changes in this fork are maintained by SanHsien unless otherwise noted.

## License Notes

The MIT License allows use, copying, modification, merging, publication, distribution, sublicensing, and commercial use, provided that the original copyright notice and permission notice are included in all copies or substantial portions of the software.

When redistributing this project or substantial parts of it:

- Keep [`LICENSE`](LICENSE) with the original MIT text.
- Keep attribution to `yazelin/line-sticker-studio`.
- Add separate attribution for new third-party libraries, fonts, icons, images, or generated assets when their licenses require it.

## Project Scope

`sticker-forge` is a local toolkit for making chat sticker packs: prompt templates, image cleanup, slicing, and export.

Current output targets:

- LINE Creators Market static sticker packs (8/16/24/32/40).
- Other chat platforms via resize/reformat: Telegram, WhatsApp, Discord, and Signal.

LINE static sticker requirements remain the primary validation target unless the roadmap explicitly changes.

## Credits and Acknowledgments

`sticker-forge` is a fork of `yazelin/line-sticker-studio` (MIT). This repository keeps the required attribution above. The old upstream vendored reference source has been removed because the maintained application now lives in `src/sticker_forge/`, `app/`, and the project documentation; historical source context remains available through git history and the upstream repository link.

Beyond the fork base, the projects below informed the design. **No source code from these projects is included in `sticker-forge`** — they are credited for concepts and publicly documented format specifications only, which were implemented independently. For the GPL / unlicensed projects, that license incompatibility with this repository's MIT license is an additional reason no code was copied.

| Project | License | What it informed |
| --- | --- | --- |
| [laggykiller/sticker-convert](https://github.com/laggykiller/sticker-convert) | GPL-2.0 | The concept of exporting one sticker set to multiple chat platforms; sticker-forge's multi-platform export was written independently from public platform specs. |
| [MarvNC/StampNyaa](https://github.com/MarvNC/StampNyaa) | No declared license | The "use LINE stickers on other platforms" desktop workflow. |
| [ittner/signal-sticker-tool](https://github.com/ittner/signal-sticker-tool) | GPL-3.0 | Reference for Signal sticker-pack packaging (a possible future feature). |
| [suchipi/line-sticker-downloader](https://github.com/suchipi/line-sticker-downloader) | MIT | Reference for fetching existing LINE packs (a possible future import feature). |
| [curegit/line-sticker-downloader](https://github.com/curegit/line-sticker-downloader) | WTFPL | Browser/CLI download and ZIP output patterns. |
| [LINE Creators Market](https://creator.line.me/) / [LINE Sticker Maker](https://creator.line.me/en/stickermaker/) | Official platform | Static sticker specs: sizes, pack sizes, transparency, and the manual submission flow. |

If a future version incorporates any third-party source code, that code together with its own license and attribution will be added here and kept in a clearly marked location. Copyleft-licensed code (GPL, etc.) will not be merged into `sticker-forge`'s own MIT-licensed modules.

## LINE And Third-Party Services

This project is not affiliated with, endorsed by, or sponsored by LINE Corporation, LY Corporation, Google, Gemini, OpenAI, Cloudflare, or any other third-party service mentioned in the code or documentation.

Names such as LINE, LINE Creators Market, ChatGPT, OpenAI, Gemini, Google, Vertex AI, Cloudflare, Turnstile, and Wrangler are used only for identification and interoperability.

Users and maintainers are responsible for complying with:

- LINE Creators Market review guidelines and submission rules.
- The terms of whichever AI image generation tool they choose to use.
- Google/Gemini/Vertex AI or OpenAI terms when using those services manually.
- Cloudflare Worker, KV, and Turnstile terms only if legacy hosted code is used or deployed.
- Local copyright, trademark, privacy, and consumer protection laws.

## AI Output Responsibility

AI-generated sticker images and text may still require human review. Do not represent the tool as guaranteeing LINE review approval, legal clearance, copyright safety, trademark clearance, or suitability for commercial use.

Before publishing sticker packs, users should review generated content for:

- Copyrighted characters, brands, logos, and recognizable IP.
- Real persons, political figures, private information, or likeness issues.
- Offensive, adult, violent, hateful, medical, gambling, or otherwise restricted content.
- Text errors, hallucinated symbols, and unintended visual artifacts.

## Deployment Caution

This fork is moving toward a local-only executable workflow. If any legacy hosted code is temporarily used, fork maintainers should replace all upstream-specific deployment values before operating a public instance:

- Worker URL and `DEFAULT_API_URL`.
- Cloudflare Worker name and KV namespace.
- Turnstile site key and secret.
- Gemini, Vertex AI, or gemini-web endpoint configuration.
- Icons, Open Graph images, product name, and public website URLs when rebranding.

Do not commit secrets, `.dev.vars`, API keys, private credentials, generated sticker packs, or user-uploaded images.
