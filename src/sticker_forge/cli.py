from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from .app_launcher import app_path, open_local_app
from .cleanup import parse_hex_color, remove_chroma_background
from .exporter import export_line_zip, export_stickers_zip, validate_line_zip
from .prompts import render_line_static_prompt
from .spec import resolve_chroma_key
from .splitter import split_grid_file, split_grid_to_stickers


def _parse_selection(value: str) -> list[int]:
    try:
        selected = [int(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("selection must be comma-separated numbers") from exc

    if len(selected) != 8:
        raise argparse.ArgumentTypeError("selection must contain exactly 8 cells")
    if any(index < 1 or index > 9 for index in selected):
        raise argparse.ArgumentTypeError("selection values must be between 1 and 9")
    if len(set(selected)) != len(selected):
        raise argparse.ArgumentTypeError("selection values must not repeat")

    return selected


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sticker-forge",
        description="Local LINE static sticker pack toolkit.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prompt = subparsers.add_parser("prompt", help="print the 3x3 LINE static sticker prompt")
    prompt.add_argument("--no-text", action="store_true")
    prompt.add_argument("--character", default="原創可愛角色")
    prompt.add_argument("--theme", default="日常聊天貼圖")
    prompt.add_argument("--tone", default="可愛、清楚、友善")
    prompt.add_argument("--style", default="粗黑線、扁平上色、適合聊天視窗縮圖閱讀")
    prompt.add_argument("--language", default="繁體中文")
    prompt.add_argument("--text", action="append", dest="texts", help="repeat exactly 8 times")
    prompt.add_argument("--action", action="append", dest="actions", help="repeat exactly 8 times")
    prompt.add_argument("--chroma-key", choices=["green", "magenta"], default="green")
    prompt.add_argument("-o", "--output", type=Path, help="write UTF-8 prompt text to a file")

    split = subparsers.add_parser("split", help="split a 3x3 grid into PNG cells")
    split.add_argument("input", type=Path)
    split.add_argument("-o", "--output-dir", type=Path, required=True)
    split.add_argument("--prefix", default="sticker")
    split.add_argument("--inset-ratio", type=float, default=0)

    cleanup = subparsers.add_parser("cleanup", help="remove a solid background with chroma-key")
    cleanup.add_argument("input", type=Path)
    cleanup.add_argument("-o", "--output", type=Path, required=True)
    cleanup.add_argument("--key-color", type=parse_hex_color)
    cleanup.add_argument("--chroma-key", choices=["green", "magenta"])
    cleanup.add_argument("--tolerance", type=int, default=32)
    cleanup.add_argument("--tune", choices=["safe", "balanced", "aggressive"], default="balanced")

    export = subparsers.add_parser("export", help="export a LINE-style sticker ZIP from a 3x3 grid")
    export.add_argument("input", type=Path)
    export.add_argument("-o", "--output", type=Path, required=True)
    export.add_argument(
        "--select",
        type=_parse_selection,
        default=_parse_selection("1,2,3,4,5,6,7,8"),
        help="8 cells to export, 1-based row-major list. Default: 1,2,3,4,5,6,7,8",
    )
    export.add_argument("--title", default="sticker-forge pack")
    export.add_argument("--author", default="sticker-forge")
    export.add_argument("--chroma-key", action="store_true", help="remove background before export")
    export.add_argument("--key-name", choices=["green", "magenta"], default="green")
    export.add_argument("--key-color", type=parse_hex_color)
    export.add_argument("--tune", choices=["safe", "balanced", "aggressive"], default="balanced")

    stickers = subparsers.add_parser("stickers", help="export all 9 stickers as a PNG-only ZIP")
    stickers.add_argument("input", type=Path)
    stickers.add_argument("-o", "--output", type=Path, required=True)
    stickers.add_argument("--chroma-key", action="store_true", help="remove background before export")
    stickers.add_argument("--key-name", choices=["green", "magenta"], default="green")
    stickers.add_argument("--key-color", type=parse_hex_color)
    stickers.add_argument("--tune", choices=["safe", "balanced", "aggressive"], default="balanced")

    validate = subparsers.add_parser("validate", help="validate a LINE-style sticker ZIP")
    validate.add_argument("zip", type=Path)

    app = subparsers.add_parser("app", help="open the local HTML sticker workspace")
    app.add_argument("--print-path", action="store_true", help="print the HTML path without opening it")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "prompt":
        prompt_text = render_line_static_prompt(
            with_text=not args.no_text,
            character=args.character,
            theme=args.theme,
            tone=args.tone,
            style=args.style,
            language=args.language,
            texts=args.texts,
            actions=args.actions,
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
        with Image.open(args.input) as image:
            key = resolve_chroma_key(args.key_name)
            cells = split_grid_to_stickers(image, background=(*key.rgb, 255))
        selected = [cells[index - 1] for index in args.select]
        if args.chroma_key:
            selected = [
                remove_chroma_background(
                    sticker,
                    key_color=args.key_color,
                    key_name=args.key_name,
                    tune=args.tune,
                )
                for sticker in selected
            ]
        output = export_line_zip(selected, args.output, title=args.title, author=args.author)
        print(output)
        return 0

    if args.command == "stickers":
        with Image.open(args.input) as image:
            key = resolve_chroma_key(args.key_name)
            stickers = split_grid_to_stickers(image, background=(*key.rgb, 255))
        if args.chroma_key:
            stickers = [
                remove_chroma_background(
                    sticker,
                    key_color=args.key_color,
                    key_name=args.key_name,
                    tune=args.tune,
                )
                for sticker in stickers
            ]
        output = export_stickers_zip(stickers, args.output)
        print(output)
        return 0

    if args.command == "validate":
        errors = validate_line_zip(args.zip)
        if errors:
            for error in errors:
                print(error)
            return 1
        print("OK")
        return 0

    if args.command == "app":
        path = app_path() if args.print_path else open_local_app()
        print(path)
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2
