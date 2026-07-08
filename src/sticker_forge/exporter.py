from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path
from typing import Sequence
from zipfile import ZIP_DEFLATED, ZipFile

from PIL import Image

from .spec import LINE_STATIC_SPEC, LINEStickerSpec

ImageSource = Image.Image | str | Path


def _load_image(source: ImageSource) -> Image.Image:
    if isinstance(source, Image.Image):
        return source.convert("RGBA")

    with Image.open(source) as image:
        return image.convert("RGBA")


def fit_to_canvas(
    image: Image.Image,
    size: tuple[int, int],
    *,
    padding: int = 0,
    background: tuple[int, int, int, int] = (255, 255, 255, 0),
) -> Image.Image:
    """Resize an image into a transparent canvas without changing aspect ratio."""
    if padding < 0:
        raise ValueError("padding must be non-negative")

    target_width, target_height = size
    inner_width = target_width - padding * 2
    inner_height = target_height - padding * 2
    if inner_width <= 0 or inner_height <= 0:
        raise ValueError("padding is too large for target size")

    source = image.convert("RGBA")
    fitted = source.copy()
    fitted.thumbnail((inner_width, inner_height), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", size, background)
    left = (target_width - fitted.width) // 2
    top = (target_height - fitted.height) // 2
    canvas.alpha_composite(fitted, (left, top))
    return canvas


def _png_bytes(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


# Static-sticker pack sizes allowed by LINE Creators Market.
LINE_PACK_SIZES = (8, 16, 24, 32, 40)


def export_line_zip(
    stickers: Sequence[ImageSource],
    output_path: str | Path,
    *,
    title: str = "sticker-forge pack",
    author: str = "sticker-forge",
    main_index: int = 0,
    tab_index: int = 0,
    spec: LINEStickerSpec = LINE_STATIC_SPEC,
) -> Path:
    """Export a LINE static sticker pack (8/16/24/32/40) plus main/tab previews."""
    count = len(stickers)
    if count not in LINE_PACK_SIZES:
        allowed = " / ".join(str(size) for size in LINE_PACK_SIZES)
        raise ValueError(f"LINE packs must have {allowed} stickers, got {count}")

    loaded = [_load_image(sticker) for sticker in stickers]
    if not 0 <= main_index < count or not 0 <= tab_index < count:
        raise ValueError("main_index and tab_index must point at a sticker in the pack")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    resized_stickers = [
        fit_to_canvas(sticker, spec.sticker_size, padding=spec.sticker_padding) for sticker in loaded
    ]
    main_image = fit_to_canvas(loaded[main_index], spec.main_size, padding=spec.main_padding)
    tab_image = fit_to_canvas(loaded[tab_index], spec.tab_size, padding=spec.tab_padding)

    readme = (
        f"{title}\n"
        f"Author: {author}\n\n"
        "This ZIP was generated locally by sticker-forge.\n"
        f"It contains {count} static sticker images, main.png, and tab.png.\n"
        "Manual LINE Creators Market submission:\n"
        "1. Sign in at https://creator.line.me/zh-hant/.\n"
        "2. Create a new Sticker item.\n"
        "3. Fill sticker description, image edit, and sales information tabs.\n"
        f"4. Upload this ZIP, or upload main.png, tab.png, and 01.png-{count:02d}.png manually.\n"
        "5. Click the sales application button manually after all fields are complete.\n"
        "Review current LINE Creators Market rules before submission.\n"
    )

    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("main.png", _png_bytes(main_image))
        archive.writestr("tab.png", _png_bytes(tab_image))
        for index, sticker in enumerate(resized_stickers, start=1):
            archive.writestr(f"{index:02d}.png", _png_bytes(sticker))
        archive.writestr("README.txt", readme)

    return output


def export_stickers_zip(
    stickers: Sequence[ImageSource],
    output_path: str | Path,
    *,
    spec: LINEStickerSpec = LINE_STATIC_SPEC,
) -> Path:
    """Export numbered sticker PNGs without main/tab/README files."""
    if not stickers:
        raise ValueError("expected at least one sticker")

    loaded = [_load_image(sticker) for sticker in stickers]
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for index, sticker in enumerate(loaded, start=1):
            resized = fit_to_canvas(
                sticker,
                spec.sticker_size,
                padding=spec.sticker_padding,
            )
            archive.writestr(f"{index:02d}.png", _png_bytes(resized))

    return output


# Static-sticker specs for other chat platforms (all transparent PNG/WebP).
# References: sticker-convert, StampNyaa, each platform's creator docs.
PLATFORM_SPECS = {
    "telegram": {"size": (512, 512), "format": "PNG", "ext": "png", "tray": None},
    "whatsapp": {"size": (512, 512), "format": "WEBP", "ext": "webp", "tray": (96, 96)},
    "discord": {"size": (320, 320), "format": "PNG", "ext": "png", "tray": None},
    "signal": {"size": (512, 512), "format": "PNG", "ext": "png", "tray": None},
}


def _encode_image(image: Image.Image, image_format: str) -> bytes:
    buffer = BytesIO()
    if image_format == "WEBP":
        image.save(buffer, format="WEBP", lossless=True)
    else:
        image.save(buffer, format=image_format, optimize=True)
    return buffer.getvalue()


def export_platform_zip(
    stickers: Sequence[ImageSource],
    output_path: str | Path,
    *,
    platform: str,
) -> Path:
    """Export stickers resized to another chat platform's sticker spec."""
    if platform not in PLATFORM_SPECS:
        raise ValueError(f"unknown platform: {platform}")
    if not stickers:
        raise ValueError("expected at least one sticker")

    profile = PLATFORM_SPECS[platform]
    loaded = [_load_image(sticker) for sticker in stickers]
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for index, sticker in enumerate(loaded, start=1):
            fitted = fit_to_canvas(sticker, profile["size"])
            archive.writestr(f"{index:02d}.{profile['ext']}", _encode_image(fitted, profile["format"]))
        if profile["tray"]:
            tray = fit_to_canvas(loaded[0], profile["tray"])
            archive.writestr("tray.png", _png_bytes(tray))
        archive.writestr(
            "README.txt",
            f"{platform} sticker pack generated locally by sticker-forge.\n"
            f"Sticker size: {profile['size'][0]}x{profile['size'][1]} {profile['format']}.\n"
            "Review the platform's current sticker rules before publishing.\n",
        )

    return output


def _is_fully_opaque(image: Image.Image) -> bool:
    """True if the image has no transparent pixels (a solid background)."""
    if image.mode == "P":
        image = image.convert("RGBA")
    if "A" not in image.getbands():
        return True
    return image.getchannel("A").getextrema()[0] == 255


def validate_line_zip(
    zip_path: str | Path,
    *,
    spec: LINEStickerSpec = LINE_STATIC_SPEC,
) -> list[str]:
    """Return validation errors for a LINE static sticker ZIP (any valid pack size)."""
    errors: list[str] = []

    with ZipFile(zip_path) as archive:
        names = set(archive.namelist())
        sticker_names = sorted(name for name in names if re.fullmatch(r"\d{2}\.png", name))
        count = len(sticker_names)
        if count not in LINE_PACK_SIZES:
            allowed = ", ".join(str(size) for size in LINE_PACK_SIZES)
            errors.append(f"sticker count is {count}, expected one of {allowed}")
            count = max(count, spec.sticker_count)

        numbered = {f"{index:02d}.png" for index in range(1, count + 1)}
        required = {"main.png", "tab.png", "README.txt"} | numbered
        missing = sorted(required - names)
        if missing:
            errors.append(f"missing files: {', '.join(missing)}")

        extra_pngs = sorted(
            name for name in names - required if name.lower().endswith(".png")
        )
        if extra_pngs:
            errors.append(f"unexpected PNG files: {', '.join(extra_pngs)}")

        expected_sizes = {
            "main.png": spec.main_size,
            "tab.png": spec.tab_size,
            **{name: spec.sticker_size for name in numbered},
        }
        for name, size in expected_sizes.items():
            if name not in names:
                continue
            with archive.open(name) as file:
                image = Image.open(file)
                if image.size != size:
                    errors.append(f"{name} size is {image.size[0]}x{image.size[1]}, expected {size[0]}x{size[1]}")
                if image.format != "PNG":
                    errors.append(f"{name} is not PNG")
                if _is_fully_opaque(image):
                    errors.append(f"{name} has no transparent background; LINE requires transparent stickers")

    return errors
