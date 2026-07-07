from __future__ import annotations

from PIL import Image

from .spec import RGBColor, resolve_chroma_key, resolve_chroma_tune



def parse_hex_color(value: str) -> RGBColor:
    color = value.strip().removeprefix("#")
    if len(color) != 6:
        raise ValueError("hex color must use RRGGBB format")

    try:
        return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
    except ValueError as exc:
        raise ValueError("hex color must use RRGGBB format") from exc


def remove_chroma_background(
    image: Image.Image,
    *,
    key_color: RGBColor | None = None,
    key_name: str | None = None,
    tolerance: int = 32,
    tune: str = "balanced",
) -> Image.Image:
    """Make pixels near the key color transparent."""
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")

    source = image.convert("RGBA")
    chroma_key = resolve_chroma_key(key_name)
    profile = resolve_chroma_tune(tune)

    if key_color is None and key_name:
        key_color = chroma_key.rgb
    if key_color is None:
        key_color = source.getpixel((0, 0))[:3]

    tolerance_squared = tolerance * tolerance
    output = Image.new("RGBA", source.size)
    pixels = []

    # Pillow 14 removes Image.getdata() in favor of get_flattened_data();
    # prefer the new API when available, fall back on older Pillow.
    if hasattr(source, "get_flattened_data"):
        source_pixels = source.get_flattened_data()
    else:
        source_pixels = source.getdata()

    for red, green, blue, alpha in source_pixels:
        alpha_out = alpha
        if key_name:
            score = _key_score(red, green, blue, chroma_key.name)
            pure_key = _is_pure_key(red, green, blue, chroma_key.name, profile)
            if pure_key and score > profile.hard:
                alpha_out = 0
            elif pure_key and score > profile.soft:
                alpha_out = round(
                    255
                    * (profile.hard - score)
                    / max(0.01, profile.hard - profile.soft)
                )
        else:
            distance_squared = (
                (red - key_color[0]) ** 2
                + (green - key_color[1]) ** 2
                + (blue - key_color[2]) ** 2
            )
            if distance_squared <= tolerance_squared:
                alpha_out = 0

        if alpha_out == 0:
            pixels.append((red, green, blue, 0))
        else:
            pixels.append((*_despill(red, green, blue, active_key=key_name), alpha_out))

    output.putdata(pixels)
    return output


def _key_score(red: int, green: int, blue: int, key_name: str) -> float:
    if key_name == "magenta":
        return (min(red, blue) - green) / 255
    return (green - max(red, blue)) / 255


def _is_pure_key(red: int, green: int, blue: int, key_name: str, profile) -> bool:
    if key_name == "magenta":
        magenta = min(red, blue)
        return (
            magenta >= profile.min_key
            and green <= profile.max_other
            and red >= green * profile.dominance
            and blue >= green * profile.dominance
        )
    return (
        green >= profile.min_key
        and red <= profile.max_other
        and blue <= profile.max_other
        and green >= red * profile.dominance
        and green >= blue * profile.dominance
    )


def _despill(
    red: int,
    green: int,
    blue: int,
    *,
    active_key: str | None,
) -> RGBColor:
    if active_key is None:
        return red, green, blue
    if active_key == "magenta":
        return green, green, green
    return red, (red + blue) // 2, blue
