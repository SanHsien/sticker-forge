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

`sticker-forge` is a local toolkit for preparing LINE sticker packs: prompt templates, image cleanup, slicing, and export.

Current output target:

- LINE Creators Market static sticker packs.

Future output targets may be added, but current product behavior and validation should assume LINE sticker requirements unless the roadmap explicitly changes.

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
