from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path

from PIL import Image

from .cleanup import parse_hex_color, remove_chroma_background
from .exporter import (
    LINE_EMOJI_MAX,
    LINE_EMOJI_MIN,
    LINE_MESSAGE_PACK_SIZES,
    LINE_PACK_SIZES,
    PLATFORM_SPECS,
    export_animated_zip,
    export_emoji_zip,
    export_line_zip,
    export_message_zip,
    export_platform_zip,
    export_stickers_zip,
    validate_emoji_zip,
    validate_line_zip,
)
from .prompts import PROMPT_PRESETS, normalize_locale, render_line_static_prompt
from .preview import build_pack_preview
from .spec import LINE_STATIC_SPEC
from .spec import resolve_chroma_key
from .splitter import split_animated_grid, split_grid_file, split_grid_to_stickers

MESSAGES = {
    "zh-Hant": {
        "description": "本機 LINE 靜態貼圖包工具。",
        "lang_help": "介面語言。預設：zh-Hant",
        "prompt_help": "輸出 3x3 LINE 靜態貼圖 prompt",
        "preset_help": "套用主題預設包（填入角色／主題／語氣／文字等，可再用其他參數覆寫）",
        "split_help": "將 3x3 grid 切成 PNG cells",
        "cleanup_help": "用 chroma-key 移除單色背景",
        "export_help": "從 3x3 grid 匯出 LINE 靜態貼圖 ZIP",
        "stickers_help": "匯出 9 張 PNG-only 貼圖 ZIP",
        "platform_help": "匯出其他平台尺寸的貼圖 ZIP（Telegram/WhatsApp/Discord/Signal）",
        "emoji_help": "匯出 LINE 原創貼圖 emoji ZIP（8-40 張 × 180x180 ＋ 聊天縮圖）",
        "thumb_help": "聊天縮圖用選取中的第幾張（1-based）。預設：1",
        "emoji_validate_help": "以 LINE emoji 規格檢查 ZIP（而非貼圖）",
        "message_help": "匯出 LINE 訊息貼圖 ZIP（8/16/24 張，文字由發送者輸入）",
        "animated_help": "匯出 LINE 動態貼圖 ZIP（8 張，需匯入動態 3x3 grid：GIF/APNG，每格 5-20 影格）",
        "target_help": "目標平台",
        "preview_help": "預覽 3x3 grid 匯出狀態",
        "validate_help": "檢查 LINE 靜態貼圖 ZIP",
        "text_help": "重複輸入剛好 8 次",
        "action_help": "重複輸入剛好 8 次",
        "output_prompt_help": "將 UTF-8 prompt 寫入檔案",
        "select_help": "要匯出的格（8/16/24/32/40 張），1-based row-major 清單。多張 grid 時編號連續累加。預設：1,2,3,4,5,6,7,8",
        "main_help": "主圖用選取中的第幾張（1-based）。預設：1",
        "tab_help": "聊天室標籤用選取中的第幾張（1-based）。預設：1",
        "keep_background_help": "保留實心底色不去背（預設會去背，因為 LINE 要求透明背景）",
        "padding_help": "貼圖透明 padding，單位 px。預設：10",
        "ok": "OK",
        "preview_header": "idx file included size alpha line_size",
        "unknown_command": "未知指令",
    },
    "en": {
        "description": "Local LINE static sticker pack toolkit.",
        "lang_help": "Interface language. Default: zh-Hant",
        "prompt_help": "print the 3x3 LINE static sticker prompt",
        "preset_help": "apply a themed starter preset (fills character/theme/tone/texts; other flags still override)",
        "split_help": "split a 3x3 grid into PNG cells",
        "cleanup_help": "remove a solid background with chroma-key",
        "export_help": "export a LINE static sticker ZIP from a 3x3 grid",
        "stickers_help": "export all 9 stickers as a PNG-only ZIP",
        "platform_help": "export a sticker ZIP sized for another platform (Telegram/WhatsApp/Discord/Signal)",
        "target_help": "target platform",
        "emoji_help": "export a LINE custom emoji ZIP (8-40 x 180x180 + chat thumbnail)",
        "thumb_help": "which selected emoji is the chat thumbnail (1-based). Default: 1",
        "emoji_validate_help": "validate the ZIP as a LINE emoji set instead of stickers",
        "message_help": "export a LINE message sticker ZIP (8/16/24, the sender types the text)",
        "animated_help": "export a LINE animated sticker ZIP (8, needs an animated 3x3 grid GIF/APNG, 5-20 frames/cell)",
        "preview_help": "preview export readiness for a 3x3 grid",
        "validate_help": "validate a LINE static sticker ZIP",
        "text_help": "repeat exactly 8 times",
        "action_help": "repeat exactly 8 times",
        "output_prompt_help": "write UTF-8 prompt text to a file",
        "select_help": "cells to export (8/16/24/32/40), 1-based row-major list; numbering continues across multiple grids. Default: 1,2,3,4,5,6,7,8",
        "main_help": "which selected sticker is the main image (1-based). Default: 1",
        "tab_help": "which selected sticker is the tab image (1-based). Default: 1",
        "keep_background_help": "keep the solid background instead of removing it (cleanup is on by default; LINE requires transparent backgrounds)",
        "padding_help": "transparent sticker padding in px. Default: 10",
        "ok": "OK",
        "preview_header": "idx file included size alpha line_size",
        "unknown_command": "unknown command",
    },
}


def _parse_selection(value: str) -> list[int]:
    try:
        selected = [int(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("selection must be comma-separated numbers") from exc

    if len(selected) not in LINE_PACK_SIZES:
        allowed = " / ".join(str(size) for size in LINE_PACK_SIZES)
        raise argparse.ArgumentTypeError(f"selection must contain {allowed} cells")
    if any(index < 1 for index in selected):
        raise argparse.ArgumentTypeError("selection values must be 1 or greater")
    if len(set(selected)) != len(selected):
        raise argparse.ArgumentTypeError("selection values must not repeat")

    return selected


def _parse_message_selection(value: str) -> list[int]:
    try:
        selected = [int(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("selection must be comma-separated numbers") from exc

    if len(selected) not in LINE_MESSAGE_PACK_SIZES:
        allowed = " / ".join(str(size) for size in LINE_MESSAGE_PACK_SIZES)
        raise argparse.ArgumentTypeError(f"message selection must contain {allowed} cells")
    if any(index < 1 for index in selected):
        raise argparse.ArgumentTypeError("selection values must be 1 or greater")
    if len(set(selected)) != len(selected):
        raise argparse.ArgumentTypeError("selection values must not repeat")

    return selected


def _parse_animated_selection(value: str) -> list[int]:
    try:
        selected = [int(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("selection must be comma-separated numbers") from exc

    if len(selected) != 8:
        raise argparse.ArgumentTypeError("animated selection must contain exactly 8 cells (one 3x3 grid)")
    if any(index < 1 for index in selected):
        raise argparse.ArgumentTypeError("selection values must be 1 or greater")
    if len(set(selected)) != len(selected):
        raise argparse.ArgumentTypeError("selection values must not repeat")

    return selected


def _parse_emoji_selection(value: str) -> list[int]:
    try:
        selected = [int(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("selection must be comma-separated numbers") from exc

    if not LINE_EMOJI_MIN <= len(selected) <= LINE_EMOJI_MAX:
        raise argparse.ArgumentTypeError(f"emoji selection must contain {LINE_EMOJI_MIN}-{LINE_EMOJI_MAX} cells")
    if any(index < 1 for index in selected):
        raise argparse.ArgumentTypeError("selection values must be 1 or greater")
    if len(set(selected)) != len(selected):
        raise argparse.ArgumentTypeError("selection values must not repeat")

    return selected


def _locale_from_argv(argv: list[str] | None) -> str:
    values = sys.argv[1:] if argv is None else argv
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--lang", choices=["zh-Hant", "en"], default="zh-Hant")
    args, _ = parser.parse_known_args(values)
    return normalize_locale(args.lang)


def _language_parent(locale: str) -> argparse.ArgumentParser:
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("--lang", choices=["zh-Hant", "en"], default=locale, help=MESSAGES[locale]["lang_help"])
    return parent


def build_parser(locale: str = "zh-Hant") -> argparse.ArgumentParser:
    locale = normalize_locale(locale)
    text = MESSAGES[locale]
    language_parent = _language_parent(locale)
    parser = argparse.ArgumentParser(
        prog="sticker-forge",
        description=text["description"],
        parents=[language_parent],
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prompt = subparsers.add_parser("prompt", parents=[language_parent], help=text["prompt_help"])
    prompt.add_argument("--no-text", action="store_true")
    prompt.add_argument("--preset", choices=sorted(PROMPT_PRESETS["zh-Hant"]), help=text["preset_help"])
    prompt.add_argument("--character")
    prompt.add_argument("--theme")
    prompt.add_argument("--tone")
    prompt.add_argument("--style")
    prompt.add_argument("--language")
    prompt.add_argument("--text", action="append", dest="texts", help=text["text_help"])
    prompt.add_argument("--action", action="append", dest="actions", help=text["action_help"])
    prompt.add_argument("--chroma-key", choices=["green", "magenta"], default="green")
    prompt.add_argument("-o", "--output", type=Path, help=text["output_prompt_help"])

    split = subparsers.add_parser("split", parents=[language_parent], help=text["split_help"])
    split.add_argument("input", type=Path)
    split.add_argument("-o", "--output-dir", type=Path, required=True)
    split.add_argument("--prefix", default="sticker")
    split.add_argument("--inset-ratio", type=float, default=0)

    cleanup = subparsers.add_parser("cleanup", parents=[language_parent], help=text["cleanup_help"])
    cleanup.add_argument("input", type=Path)
    cleanup.add_argument("-o", "--output", type=Path, required=True)
    cleanup.add_argument("--key-color", type=parse_hex_color)
    cleanup.add_argument("--chroma-key", choices=["green", "magenta"])
    cleanup.add_argument("--tolerance", type=int, default=32)
    cleanup.add_argument("--tune", choices=["safe", "balanced", "aggressive"], default="balanced")

    export = subparsers.add_parser("export", parents=[language_parent], help=text["export_help"])
    export.add_argument("input", type=Path, nargs="+")
    export.add_argument("-o", "--output", type=Path, required=True)
    export.add_argument(
        "--select",
        type=_parse_selection,
        default=_parse_selection("1,2,3,4,5,6,7,8"),
        help=text["select_help"],
    )
    export.add_argument("--main", type=int, default=1, help=text["main_help"])
    export.add_argument("--tab", type=int, default=1, help=text["tab_help"])
    export.add_argument("--title", default="sticker-forge pack")
    export.add_argument("--author", default="sticker-forge")
    export.add_argument("--keep-background", action="store_true", help=text["keep_background_help"])
    export.add_argument("--key-name", choices=["green", "magenta"], default="green")
    export.add_argument("--tune", choices=["safe", "balanced", "aggressive"], default="balanced")
    export.add_argument("--padding", type=int, default=LINE_STATIC_SPEC.sticker_padding, help=text["padding_help"])

    stickers = subparsers.add_parser("stickers", parents=[language_parent], help=text["stickers_help"])
    stickers.add_argument("input", type=Path)
    stickers.add_argument("-o", "--output", type=Path, required=True)
    stickers.add_argument("--keep-background", action="store_true", help=text["keep_background_help"])
    stickers.add_argument("--key-name", choices=["green", "magenta"], default="green")
    stickers.add_argument("--tune", choices=["safe", "balanced", "aggressive"], default="balanced")
    stickers.add_argument("--padding", type=int, default=LINE_STATIC_SPEC.sticker_padding, help=text["padding_help"])

    platform = subparsers.add_parser("platform", parents=[language_parent], help=text["platform_help"])
    platform.add_argument("input", type=Path)
    platform.add_argument("-o", "--output", type=Path, required=True)
    platform.add_argument("--target", choices=sorted(PLATFORM_SPECS), required=True, help=text["target_help"])
    platform.add_argument("--keep-background", action="store_true", help=text["keep_background_help"])
    platform.add_argument("--key-name", choices=["green", "magenta"], default="green")
    platform.add_argument("--tune", choices=["safe", "balanced", "aggressive"], default="balanced")

    emoji = subparsers.add_parser("emoji", parents=[language_parent], help=text["emoji_help"])
    emoji.add_argument("input", type=Path, nargs="+")
    emoji.add_argument("-o", "--output", type=Path, required=True)
    emoji.add_argument(
        "--select",
        type=_parse_emoji_selection,
        default=_parse_emoji_selection("1,2,3,4,5,6,7,8"),
        help=text["select_help"],
    )
    emoji.add_argument("--thumb", type=int, default=1, help=text["thumb_help"])
    emoji.add_argument("--keep-background", action="store_true", help=text["keep_background_help"])
    emoji.add_argument("--key-name", choices=["green", "magenta"], default="green")
    emoji.add_argument("--tune", choices=["safe", "balanced", "aggressive"], default="balanced")
    emoji.add_argument("--title", default="sticker-forge emoji")
    emoji.add_argument("--author", default="sticker-forge")

    message = subparsers.add_parser("message", parents=[language_parent], help=text["message_help"])
    message.add_argument("input", type=Path, nargs="+")
    message.add_argument("-o", "--output", type=Path, required=True)
    message.add_argument(
        "--select",
        type=_parse_message_selection,
        default=_parse_message_selection("1,2,3,4,5,6,7,8"),
        help=text["select_help"],
    )
    message.add_argument("--main", type=int, default=1, help=text["main_help"])
    message.add_argument("--tab", type=int, default=1, help=text["tab_help"])
    message.add_argument("--keep-background", action="store_true", help=text["keep_background_help"])
    message.add_argument("--key-name", choices=["green", "magenta"], default="green")
    message.add_argument("--tune", choices=["safe", "balanced", "aggressive"], default="balanced")
    message.add_argument("--title", default="sticker-forge message pack")
    message.add_argument("--author", default="sticker-forge")

    animated = subparsers.add_parser("animated", parents=[language_parent], help=text["animated_help"])
    animated.add_argument("input", type=Path)
    animated.add_argument("-o", "--output", type=Path, required=True)
    animated.add_argument(
        "--select",
        type=_parse_animated_selection,
        default=_parse_animated_selection("1,2,3,4,5,6,7,8"),
        help=text["select_help"],
    )
    animated.add_argument("--main", type=int, default=1, help=text["main_help"])
    animated.add_argument("--tab", type=int, default=1, help=text["tab_help"])
    animated.add_argument("--keep-background", action="store_true", help=text["keep_background_help"])
    animated.add_argument("--key-name", choices=["green", "magenta"], default="green")
    animated.add_argument("--tune", choices=["safe", "balanced", "aggressive"], default="balanced")
    animated.add_argument("--title", default="sticker-forge animated")
    animated.add_argument("--author", default="sticker-forge")

    preview = subparsers.add_parser("preview", parents=[language_parent], help=text["preview_help"])
    preview.add_argument("input", type=Path)
    preview.add_argument(
        "--select",
        type=_parse_selection,
        default=_parse_selection("1,2,3,4,5,6,7,8"),
        help=text["select_help"],
    )
    preview.add_argument("--keep-background", action="store_true", help=text["keep_background_help"])
    preview.add_argument("--key-name", choices=["green", "magenta"], default="green")
    preview.add_argument("--tune", choices=["safe", "balanced", "aggressive"], default="balanced")
    preview.add_argument("--padding", type=int, default=LINE_STATIC_SPEC.sticker_padding, help=text["padding_help"])

    validate = subparsers.add_parser("validate", parents=[language_parent], help=text["validate_help"])
    validate.add_argument("zip", type=Path)
    validate.add_argument("--emoji", action="store_true", help=text["emoji_validate_help"])

    return parser


def main(argv: list[str] | None = None) -> int:
    locale = _locale_from_argv(argv)
    parser = build_parser(locale)
    args = parser.parse_args(argv)
    locale = normalize_locale(args.lang)
    text = MESSAGES[locale]

    if args.command == "prompt":
        preset = PROMPT_PRESETS[locale].get(args.preset, {}) if args.preset else {}
        prompt_text = render_line_static_prompt(
            with_text=not args.no_text,
            locale=locale,
            character=args.character or preset.get("character"),
            theme=args.theme or preset.get("theme"),
            tone=args.tone or preset.get("tone"),
            style=args.style or preset.get("style"),
            language=args.language or preset.get("language"),
            texts=args.texts or preset.get("texts"),
            actions=args.actions or preset.get("actions"),
            chroma_key=args.chroma_key,
        )
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(prompt_text, encoding="utf-8")
            print(args.output)
        else:
            print(prompt_text, end="")
        return 0

    if args.command == "split":
        paths = split_grid_file(
            args.input,
            args.output_dir,
            prefix=args.prefix,
            inset_ratio=args.inset_ratio,
        )
        for path in paths:
            print(path)
        return 0

    if args.command == "cleanup":
        with Image.open(args.input) as image:
            output_image = remove_chroma_background(
                image,
                key_color=args.key_color,
                key_name=args.chroma_key,
                tolerance=args.tolerance,
                tune=args.tune,
            )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        output_image.save(args.output)
        print(args.output)
        return 0

    if args.command == "export":
        spec = replace(LINE_STATIC_SPEC, sticker_padding=args.padding)
        key = resolve_chroma_key(args.key_name)
        pool: list[Image.Image] = []
        for grid_path in args.input:
            with Image.open(grid_path) as image:
                pool.extend(split_grid_to_stickers(image, spec=spec, background=(*key.rgb, 255)))
        if any(index > len(pool) for index in args.select):
            parser.error(
                f"--select values must be between 1 and {len(pool)} "
                f"({len(args.input)} grid(s) = {len(pool)} cells)"
            )
        selected = [pool[index - 1] for index in args.select]
        if not args.keep_background:
            selected = [
                remove_chroma_background(sticker, key_name=args.key_name, tune=args.tune)
                for sticker in selected
            ]
        if not 1 <= args.main <= len(selected) or not 1 <= args.tab <= len(selected):
            parser.error(f"--main/--tab must be between 1 and {len(selected)}")
        output = export_line_zip(
            selected,
            args.output,
            title=args.title,
            author=args.author,
            main_index=args.main - 1,
            tab_index=args.tab - 1,
            spec=spec,
        )
        print(output)
        return 0

    if args.command == "stickers":
        spec = replace(LINE_STATIC_SPEC, sticker_padding=args.padding)
        with Image.open(args.input) as image:
            key = resolve_chroma_key(args.key_name)
            stickers = split_grid_to_stickers(image, spec=spec, background=(*key.rgb, 255))
        if not args.keep_background:
            stickers = [
                remove_chroma_background(
                    sticker,
                    key_name=args.key_name,
                    tune=args.tune,
                )
                for sticker in stickers
            ]
        output = export_stickers_zip(stickers, args.output, spec=spec)
        print(output)
        return 0

    if args.command == "platform":
        with Image.open(args.input) as image:
            key = resolve_chroma_key(args.key_name)
            stickers = split_grid_to_stickers(image, background=(*key.rgb, 255))
        if not args.keep_background:
            stickers = [
                remove_chroma_background(sticker, key_name=args.key_name, tune=args.tune)
                for sticker in stickers
            ]
        output = export_platform_zip(stickers, args.output, platform=args.target)
        print(output)
        return 0

    if args.command == "emoji":
        key = resolve_chroma_key(args.key_name)
        pool: list[Image.Image] = []
        for grid_path in args.input:
            with Image.open(grid_path) as image:
                pool.extend(split_grid_to_stickers(image, background=(*key.rgb, 255)))
        if any(index > len(pool) for index in args.select):
            parser.error(
                f"--select values must be between 1 and {len(pool)} "
                f"({len(args.input)} grid(s) = {len(pool)} cells)"
            )
        selected = [pool[index - 1] for index in args.select]
        if not args.keep_background:
            selected = [
                remove_chroma_background(sticker, key_name=args.key_name, tune=args.tune)
                for sticker in selected
            ]
        if not 1 <= args.thumb <= len(selected):
            parser.error(f"--thumb must be between 1 and {len(selected)}")
        output = export_emoji_zip(
            selected, args.output, thumb_index=args.thumb - 1, title=args.title, author=args.author
        )
        print(output)
        return 0

    if args.command == "message":
        key = resolve_chroma_key(args.key_name)
        pool: list[Image.Image] = []
        for grid_path in args.input:
            with Image.open(grid_path) as image:
                pool.extend(split_grid_to_stickers(image, background=(*key.rgb, 255)))
        if any(index > len(pool) for index in args.select):
            parser.error(
                f"--select values must be between 1 and {len(pool)} "
                f"({len(args.input)} grid(s) = {len(pool)} cells)"
            )
        selected = [pool[index - 1] for index in args.select]
        if not args.keep_background:
            selected = [
                remove_chroma_background(sticker, key_name=args.key_name, tune=args.tune)
                for sticker in selected
            ]
        if not 1 <= args.main <= len(selected) or not 1 <= args.tab <= len(selected):
            parser.error(f"--main/--tab must be between 1 and {len(selected)}")
        output = export_message_zip(
            selected,
            args.output,
            title=args.title,
            author=args.author,
            main_index=args.main - 1,
            tab_index=args.tab - 1,
        )
        print(output)
        return 0

    if args.command == "animated":
        sticker_frames, durations = split_animated_grid(args.input)
        if any(index > len(sticker_frames) for index in args.select):
            parser.error(f"--select values must be between 1 and {len(sticker_frames)}")
        selected = [sticker_frames[index - 1] for index in args.select]
        if not args.keep_background:
            selected = [
                [remove_chroma_background(frame, key_name=args.key_name, tune=args.tune) for frame in frames]
                for frames in selected
            ]
        if not 1 <= args.main <= len(selected) or not 1 <= args.tab <= len(selected):
            parser.error(f"--main/--tab must be between 1 and {len(selected)}")
        output = export_animated_zip(
            selected,
            args.output,
            main_index=args.main - 1,
            tab_index=args.tab - 1,
            title=args.title,
            author=args.author,
            durations=durations,
        )
        print(output)
        return 0

    if args.command == "preview":
        spec = replace(LINE_STATIC_SPEC, sticker_padding=args.padding)
        with Image.open(args.input) as image:
            key = resolve_chroma_key(args.key_name)
            stickers = split_grid_to_stickers(image, spec=spec, background=(*key.rgb, 255))
        if not args.keep_background:
            stickers = [
                remove_chroma_background(
                    sticker,
                    key_name=args.key_name,
                    tune=args.tune,
                )
                for sticker in stickers
            ]
        preview_data = build_pack_preview(stickers, selected=args.select, spec=spec)
        print(text["preview_header"])
        for item in preview_data.stickers:
            print(
                f"{item.index:02d} {item.filename} "
                f"{'yes' if item.included else 'no'} "
                f"{item.width}x{item.height} "
                f"{'yes' if item.has_alpha else 'no'} "
                f"{'yes' if item.is_line_size else 'no'}"
            )
        if preview_data.errors:
            for error in preview_data.errors:
                print(error)
            return 1
        return 0

    if args.command == "validate":
        errors = validate_emoji_zip(args.zip) if args.emoji else validate_line_zip(args.zip)
        if errors:
            for error in errors:
                print(error)
            return 1
        print(text["ok"])
        return 0

    parser.error(f"{text['unknown_command']}: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
