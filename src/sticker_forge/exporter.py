from __future__ import annotations

import re
from dataclasses import replace
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
# Message stickers accept fewer sizes and want no margin (LINE adds one).
LINE_MESSAGE_PACK_SIZES = (8, 16, 24)


def export_line_zip(
    stickers: Sequence[ImageSource],
    output_path: str | Path,
    *,
    title: str = "sticker-forge pack",
    author: str = "sticker-forge",
    main_index: int = 0,
    tab_index: int = 0,
    spec: LINEStickerSpec = LINE_STATIC_SPEC,
    pack_sizes: tuple[int, ...] = LINE_PACK_SIZES,
    readme: str | None = None,
) -> Path:
    """Export a LINE static sticker pack (8/16/24/32/40) plus main/tab previews."""
    count = len(stickers)
    if count not in pack_sizes:
        allowed = " / ".join(str(size) for size in pack_sizes)
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

    if readme is None:
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


def export_message_zip(
    images: Sequence[ImageSource],
    output_path: str | Path,
    *,
    title: str = "sticker-forge message pack",
    author: str = "sticker-forge",
    main_index: int = 0,
    tab_index: int = 0,
) -> Path:
    """Export a LINE message sticker pack (8/16/24, no baked-in margin)."""
    count = len(images)
    spec = replace(LINE_STATIC_SPEC, sticker_padding=0)
    readme = (
        f"{title}\n"
        f"Author: {author}\n\n"
        "This ZIP was generated locally by sticker-forge (LINE message stickers).\n"
        f"It contains {count} message-sticker images (370x320 max), main.png (240x240),\n"
        "and tab.png (96x74). Message stickers let the sender type a short message onto\n"
        "the sticker; the text position and font are set in LINE's editor, not here.\n"
        "Manual LINE Creators Market submission:\n"
        "1. Sign in and create a new Message Sticker item.\n"
        "2. Choose 8, 16, or 24 stickers on the Manage Stickers page.\n"
        "3. Upload the images; LINE adds margins automatically, so none is baked in.\n"
        "4. Set the text position, font, and default message per sticker in LINE's editor.\n"
        "Review current LINE Creators Market message-sticker rules before submission.\n"
    )
    return export_line_zip(
        images,
        output_path,
        title=title,
        author=author,
        main_index=main_index,
        tab_index=tab_index,
        spec=spec,
        pack_sizes=LINE_MESSAGE_PACK_SIZES,
        readme=readme,
    )


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


# LINE custom emoji (Regular Emoji) spec, verified from
# https://creator.line.me/en/guideline/emoji/ and .../emoji/detail/ :
# 8-40 images at 180x180 PNG (transparent), filenames 001.png..0NN.png, plus a
# 96x74 chat thumbnail icon (uploaded separately in the LINE UI), ZIP < 20 MB.
LINE_EMOJI_SIZE = (180, 180)
LINE_EMOJI_THUMB_SIZE = (96, 74)
LINE_EMOJI_MIN = 8
LINE_EMOJI_MAX = 40


def export_emoji_zip(
    images: Sequence[ImageSource],
    output_path: str | Path,
    *,
    thumb_index: int = 0,
    title: str = "sticker-forge emoji",
    author: str = "sticker-forge",
) -> Path:
    """Export a LINE custom emoji set (8-40 x 180x180) plus a chat thumbnail."""
    count = len(images)
    if not LINE_EMOJI_MIN <= count <= LINE_EMOJI_MAX:
        raise ValueError(f"LINE emoji sets need {LINE_EMOJI_MIN}-{LINE_EMOJI_MAX} images, got {count}")

    loaded = [_load_image(image) for image in images]
    if not 0 <= thumb_index < count:
        raise ValueError("thumb_index must point at an emoji in the set")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    resized = [fit_to_canvas(image, LINE_EMOJI_SIZE) for image in loaded]
    thumbnail = fit_to_canvas(loaded[thumb_index], LINE_EMOJI_THUMB_SIZE)

    readme = (
        f"{title}\n"
        f"Author: {author}\n\n"
        "This ZIP was generated locally by sticker-forge (LINE custom emoji).\n"
        f"It contains {count} emoji images (001.png-{count:03d}.png, 180x180) and\n"
        "chat-thumbnail.png (96x74).\n"
        "Manual LINE Creators Market submission:\n"
        "1. Sign in at https://creator.line.me/ and create a new Emoji item.\n"
        "2. Upload the numbered 001.png-... emoji images (as a ZIP of just those, or one by one).\n"
        "3. Upload chat-thumbnail.png in the Chat Thumbnail Icon field.\n"
        "4. Fill in the required text fields and apply for sale.\n"
        "Review current LINE Creators Market emoji rules before submission.\n"
    )

    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for index, image in enumerate(resized, start=1):
            archive.writestr(f"{index:03d}.png", _png_bytes(image))
        archive.writestr("chat-thumbnail.png", _png_bytes(thumbnail))
        archive.writestr("README.txt", readme)

    return output


# LINE animated sticker spec, verified from
# https://creator.line.me/en/guideline/animationsticker/ :
# 8/16/24 stickers, up to 320x270 APNG (5-20 frames, one side >= 270), an animated
# 240x240 APNG main image, a static 96x74 PNG tab, loops totalling <= 4 seconds.
LINE_ANIM_MAX_SIZE = (320, 270)
LINE_ANIM_MAIN_SIZE = (240, 240)
LINE_ANIM_TAB_SIZE = (96, 74)
LINE_ANIM_PACK_SIZES = (8, 16, 24)
LINE_ANIM_MIN_FRAMES = 5
LINE_ANIM_MAX_FRAMES = 20


def _fit_frames_within(frames: list[Image.Image], box: tuple[int, int]) -> list[Image.Image]:
    """Resize frames to a shared size filling box (keep aspect, up or down, no padding).

    LINE animated stickers must have one side at least 270px, so this scales up
    small cells as well as down, unlike ``thumbnail`` which only shrinks.
    """
    width, height = frames[0].size
    box_w, box_h = box
    scale = min(box_w / width, box_h / height)
    size = (max(1, round(width * scale)), max(1, round(height * scale)))
    return [frame.convert("RGBA").resize(size, Image.Resampling.LANCZOS) for frame in frames]


def _apng_bytes(frames: list[Image.Image], durations: list[int]) -> bytes:
    # LINE wants 1-4 loops totalling <= 4 s; pick a loop count that fits.
    one_loop = max(1, sum(durations))
    loops = max(1, min(4, 4000 // one_loop))
    buffer = BytesIO()
    frames[0].save(
        buffer,
        format="PNG",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=loops,
        disposal=2,
    )
    return buffer.getvalue()


def export_animated_zip(
    sticker_frames: Sequence[Sequence[Image.Image]],
    output_path: str | Path,
    *,
    main_index: int = 0,
    tab_index: int = 0,
    title: str = "sticker-forge animated",
    author: str = "sticker-forge",
    durations: Sequence[int] | None = None,
) -> Path:
    """Export a LINE animated sticker pack (8/16/24 APNG stickers + APNG main + PNG tab)."""
    count = len(sticker_frames)
    if count not in LINE_ANIM_PACK_SIZES:
        allowed = " / ".join(str(size) for size in LINE_ANIM_PACK_SIZES)
        raise ValueError(f"LINE animated packs must have {allowed} stickers, got {count}")
    for index, frames in enumerate(sticker_frames, start=1):
        if not LINE_ANIM_MIN_FRAMES <= len(frames) <= LINE_ANIM_MAX_FRAMES:
            raise ValueError(
                f"sticker {index} has {len(frames)} frames, expected "
                f"{LINE_ANIM_MIN_FRAMES}-{LINE_ANIM_MAX_FRAMES}"
            )
    if not 0 <= main_index < count or not 0 <= tab_index < count:
        raise ValueError("main_index and tab_index must point at a sticker in the pack")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    def _durations_for(frames: Sequence[Image.Image]) -> list[int]:
        if durations and len(durations) == len(frames):
            return [max(20, int(d)) for d in durations]
        return [100] * len(frames)

    readme = (
        f"{title}\n"
        f"Author: {author}\n\n"
        "This ZIP was generated locally by sticker-forge (LINE animated stickers).\n"
        f"It contains {count} animated stickers (01.png-{count:02d}.png, APNG, up to 320x270),\n"
        "an animated main.png (240x240), and a static tab.png (96x74).\n"
        "Each APNG has 5-20 frames; LINE rejects APNGs whose frames are all identical.\n"
        "Manual LINE Creators Market submission:\n"
        "1. Sign in and create a new Animated Sticker item.\n"
        "2. Choose 8, 16, or 24 stickers on the Manage Stickers page.\n"
        "3. Upload the APNG images, main.png, and tab.png.\n"
        "Review current LINE Creators Market animated-sticker rules before submission.\n"
    )

    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for index, frames in enumerate(sticker_frames, start=1):
            fitted = _fit_frames_within(list(frames), LINE_ANIM_MAX_SIZE)
            archive.writestr(f"{index:02d}.png", _apng_bytes(fitted, _durations_for(frames)))
        main_frames = [fit_to_canvas(frame, LINE_ANIM_MAIN_SIZE) for frame in sticker_frames[main_index]]
        archive.writestr("main.png", _apng_bytes(main_frames, _durations_for(sticker_frames[main_index])))
        tab_image = fit_to_canvas(sticker_frames[tab_index][0], LINE_ANIM_TAB_SIZE)
        archive.writestr("tab.png", _png_bytes(tab_image))
        archive.writestr("README.txt", readme)

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


def validate_emoji_zip(zip_path: str | Path) -> list[str]:
    """Return validation errors for a LINE custom emoji ZIP."""
    errors: list[str] = []

    with ZipFile(zip_path) as archive:
        names = set(archive.namelist())
        emoji_names = sorted(name for name in names if re.fullmatch(r"\d{3}\.png", name))
        count = len(emoji_names)
        if not LINE_EMOJI_MIN <= count <= LINE_EMOJI_MAX:
            errors.append(f"emoji count is {count}, expected {LINE_EMOJI_MIN}-{LINE_EMOJI_MAX}")

        numbered = {f"{index:03d}.png" for index in range(1, count + 1)}
        missing = sorted(numbered - names)
        if missing:
            errors.append(f"missing emoji files: {', '.join(missing)}")

        for name in sorted(numbered & names):
            with archive.open(name) as file:
                image = Image.open(file)
                if image.size != LINE_EMOJI_SIZE:
                    errors.append(f"{name} size is {image.size[0]}x{image.size[1]}, expected 180x180")
                if image.format != "PNG":
                    errors.append(f"{name} is not PNG")
                if _is_fully_opaque(image):
                    errors.append(f"{name} has no transparent background; LINE requires transparent emoji")

    return errors
