from __future__ import annotations

from PIL import Image

from .spec import (
    ChromaTuneProfile,
    RGBColor,
    chroma_despill_strength,
    resolve_chroma_key,
    resolve_chroma_tune,
)



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
    tune: str | ChromaTuneProfile | dict | None = "balanced",
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

    despill_strength = chroma_despill_strength(profile)
    continuous = profile.mode == "continuous"

    for red, green, blue, alpha in source_pixels:
        alpha_out = alpha
        if key_name:
            score = _key_score(red, green, blue, chroma_key.name)
            # strict: only pixels passing the pure-key test may be keyed, so
            # uncertain foreground edges survive. continuous: key on score
            # alone, which cleans stubborn backgrounds harder.
            keyable = True if continuous else _is_pure_key(
                red, green, blue, chroma_key.name, profile
            )
            key_alpha = 255
            if keyable and score > profile.hard:
                key_alpha = 0
            elif keyable and score > profile.soft:
                key_alpha = round(
                    255
                    * (profile.hard - score)
                    / max(0.01, profile.hard - profile.soft)
                )
            # Composite against the source alpha so already-transparent input
            # (e.g. APNG frames) never becomes more opaque than it started.
            alpha_out = round(max(0, min(255, key_alpha)) * alpha / 255)
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
        elif key_name and _key_score(red, green, blue, chroma_key.name) > 0:
            # Despill only pixels that actually lean toward the key colour
            # (green/magenta spill on foreground edges). Opaque foreground that
            # does not lean key-ward keeps its original colour — otherwise a blue
            # or skin-tone pixel next to a magenta/green backdrop would be forced
            # toward the key channel (e.g. blue -> black under a magenta key).
            pixels.append(
                (
                    *_despill(
                        red,
                        green,
                        blue,
                        active_key=key_name,
                        strength=despill_strength,
                    ),
                    alpha_out,
                )
            )
        else:
            pixels.append((red, green, blue, alpha_out))

    output.putdata(pixels)
    if key_name and profile.erode:
        output = _erode_fringe(output, profile.erode)
    return output


def _erode_fringe(image: Image.Image, passes: int) -> Image.Image:
    """Drop partial-alpha pixels that touch a fully transparent neighbour.

    Only reachable from profiles that opt in (``aggressive``); the softer
    profiles keep decontaminated partial-alpha pixels, because deleting them is
    the main source of stair-stepped silhouettes.
    """
    width, height = image.size
    working = image.copy()
    for _ in range(passes):
        alpha = working.getchannel("A")
        # Snapshot alpha so one pass cannot cascade-erode into the character.
        snapshot = alpha.load()
        result = alpha.copy()
        target = result.load()
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                value = snapshot[x, y]
                if value in (0, 255):
                    continue
                touches_empty = any(
                    snapshot[x + dx, y + dy] == 0
                    for dy in (-1, 0, 1)
                    for dx in (-1, 0, 1)
                    if not (dx == 0 and dy == 0)
                )
                if touches_empty:
                    target[x, y] = 0
        working.putalpha(result)
    return working


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
    strength: float = 1.0,
) -> RGBColor:
    """Pull the key colour out of a spilled pixel, `strength` of the way.

    At strength 1.0 this is a full despill (magenta -> grey, green channel
    replaced by the red/blue average). Conservative custom profiles use a lower
    strength so a cautious matte does not still rewrite edge colour hard.
    """
    if active_key is None:
        return red, green, blue
    if active_key == "magenta":
        return (
            _clamp_byte(red + (green - red) * strength),
            green,
            _clamp_byte(blue + (green - blue) * strength),
        )
    target = (red + blue) / 2
    return red, _clamp_byte(green + (target - green) * strength), blue


def _clamp_byte(value: float) -> int:
    return max(0, min(255, round(value)))
