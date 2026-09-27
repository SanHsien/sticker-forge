"""Create non-infringing LINE ZIPs for manual Creators Market upload trials."""

from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from PIL import Image

from create_sample_assets import create_animated_files, create_static_grid
from sticker_forge.cleanup import remove_chroma_background
from sticker_forge.exporter import (
    export_animated_zip,
    export_big_zip,
    export_effect_zip,
    export_emoji_zip,
    export_line_zip,
    export_message_zip,
    export_popup_zip,
    validate_big_zip,
    validate_effect_zip,
    validate_emoji_zip,
    validate_line_zip,
    validate_popup_zip,
)
from sticker_forge.splitter import load_animated_frames, split_grid_to_stickers


def _load_clean_static_stickers(grid_path: Path) -> list[Image.Image]:
    with Image.open(grid_path) as image:
        stickers = split_grid_to_stickers(image, background=(0, 255, 0, 255))
    return [remove_chroma_background(sticker, key_name="green") for sticker in stickers[:8]]


def _load_clean_animation(path: Path) -> tuple[list[Image.Image], list[int]]:
    frames, durations = load_animated_frames(path)
    return [remove_chroma_background(frame, key_name="green") for frame in frames], durations


def _validate_animated_zip(zip_path: Path) -> list[str]:
    errors: list[str] = []
    with ZipFile(zip_path) as archive:
        names = set(archive.namelist())
        required = {"main.png", "tab.png", "README.txt"} | {f"{index:02d}.png" for index in range(1, 9)}
        missing = sorted(required - names)
        if missing:
            errors.append(f"missing files: {', '.join(missing)}")
        for name in sorted(required & names):
            if name == "README.txt":
                continue
            image = Image.open(BytesIO(archive.read(name)))
            if name == "tab.png":
                if image.size != (96, 74):
                    errors.append(f"{name} size is {image.size}, expected 96x74")
                continue
            if not getattr(image, "is_animated", False):
                errors.append(f"{name} is not animated APNG")
                continue
            if not 5 <= getattr(image, "n_frames", 1) <= 20:
                errors.append(f"{name} frame count is {image.n_frames}, expected 5-20")
    return errors


def _write_result(name: str, path: Path, errors: list[str]) -> None:
    if errors:
        print(f"FAIL {name}: {path}")
        for error in errors:
            print(f"  - {error}")
        raise SystemExit(1)
    print(f"OK   {name}: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create LINE trial ZIPs from generated non-infringing samples.")
    parser.add_argument(
        "--assets-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "generated",
        help="Directory for generated sample assets. Defaults to examples/generated.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "generated" / "line-trial-packs",
        help="Directory for trial ZIP outputs. Defaults to examples/generated/line-trial-packs.",
    )
    args = parser.parse_args()

    assets_dir = args.assets_dir.resolve()
    output_dir = args.output_dir.resolve()
    assets_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    grid_path = assets_dir / "static-grid.png"
    if not grid_path.exists():
        grid_path = create_static_grid(assets_dir)

    animated_dir = assets_dir / "animated"
    animated_paths = sorted(animated_dir.glob("animated-*.gif"))
    if len(animated_paths) < 8:
        animated_paths = create_animated_files(assets_dir)
    animated_paths = animated_paths[:8]

    stickers = _load_clean_static_stickers(grid_path)
    animations = []
    durations = []
    for path in animated_paths:
        frames, frame_durations = _load_clean_animation(path)
        animations.append(frames)
        durations.append(frame_durations)

    title = "sticker-forge upload trial"
    author = "sticker-forge"

    outputs = {
        "static": export_line_zip(stickers, output_dir / "line-static.zip", title=title, author=author),
        "big": export_big_zip(stickers, output_dir / "line-big-stickers.zip", title=title, author=author),
        "emoji": export_emoji_zip(stickers, output_dir / "line-emoji.zip", title=title, author=author),
        "message": export_message_zip(stickers, output_dir / "line-message.zip", title=title, author=author),
        "animated": export_animated_zip(
            animations,
            output_dir / "line-animated.zip",
            title=title,
            author=author,
            durations=durations,
        ),
        "popup": export_popup_zip(
            stickers,
            animations,
            output_dir / "line-popup.zip",
            title=title,
            author=author,
            durations=durations,
        ),
        "effect": export_effect_zip(
            stickers,
            animations,
            output_dir / "line-effect.zip",
            title=title,
            author=author,
            durations=durations,
        ),
    }

    validators = {
        "static": validate_line_zip,
        "big": validate_big_zip,
        "emoji": validate_emoji_zip,
        "message": validate_line_zip,
        "animated": _validate_animated_zip,
        "popup": validate_popup_zip,
        "effect": validate_effect_zip,
    }

    for name, path in outputs.items():
        _write_result(name, path, validators[name](path))

    print(f"\nManual upload trial ZIPs: {output_dir}")
    print("Use these only for LINE Creators Market upload-form smoke tests; this script does not submit anything.")


if __name__ == "__main__":
    main()
