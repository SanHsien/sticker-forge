from __future__ import annotations

import re

from PIL import Image

from .spec import (
    ChromaKey,
    ChromaTuneProfile,
    chroma_channels,
    RGBColor,
    chroma_despill_strength,
    resolve_chroma_key,
    resolve_chroma_tune,
)



def parse_hex_color(value: str) -> RGBColor:
    color = value.strip().removeprefix("#")
    # int(x, 16) alone also accepts signs and spaces ("-1", " f"), so match first.
    if not re.fullmatch(r"[0-9A-Fa-f]{6}", color):
        raise ValueError("hex color must use RRGGBB format")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


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
    extremes = _key_extremes(chroma_key)

    for red, green, blue, alpha in source_pixels:
        alpha_out = alpha
        if key_name:
            pixel = (red, green, blue)
            score = _key_score(extremes, pixel)
            # strict: only pixels passing the pure-key test may be keyed, so
            # uncertain foreground edges survive. continuous: key on score
            # alone, which cleans stubborn backgrounds harder.
            keyable = True if continuous else _is_pure_key(extremes, pixel, profile)
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
        elif key_name and _key_score(extremes, (red, green, blue)) > 0:
            # Despill only pixels that actually lean toward the key colour
            # (key-colour spill on foreground edges). Opaque foreground that
            # does not lean key-ward keeps its original colour — otherwise a blue
            # or skin-tone pixel next to a magenta/green backdrop would be forced
            # toward the key channel (e.g. blue -> black under a magenta key).
            pixels.append(
                (
                    *_despill(
                        red,
                        green,
                        blue,
                        key=chroma_key,
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


def _key_extremes(key: ChromaKey):
    """Build ``pixel -> (weakest key channel, strongest other channel)``.

    Built once per key (not per pixel): any colour with chroma occupies either
    one channel (green, red, blue) or two (magenta, cyan, yellow).
    """
    key_idx, other_idx = chroma_channels(key.rgb)
    if len(key_idx) == 1:
        (a,), (b, c) = key_idx, other_idx
        return lambda p: (p[a], max(p[b], p[c]))
    (a, b), (c,) = key_idx, other_idx
    return lambda p: (min(p[a], p[b]), p[c])


def _key_score(extremes, pixel) -> float:
    high, low = extremes(pixel)
    return (high - low) / 255


def _is_pure_key(extremes, pixel, profile) -> bool:
    high, low = extremes(pixel)
    return (
        high >= profile.min_key
        and low <= profile.max_other
        and high >= low * profile.dominance
    )


def _despill(
    red: int,
    green: int,
    blue: int,
    *,
    key: ChromaKey | None,
    strength: float = 1.0,
) -> RGBColor:
    """Pull the key colour out of a spilled pixel, `strength` of the way.

    At strength 1.0 this is a full despill: each key-occupied channel is
    replaced by the average of the other channels (magenta -> grey, green
    channel -> red/blue average). Conservative custom profiles use a lower
    strength so a cautious matte does not still rewrite edge colour hard.
    """
    if key is None:
        return red, green, blue
    pixel = [red, green, blue]
    key_idx, other_idx = chroma_channels(key.rgb)
    target = sum(pixel[i] for i in other_idx) / len(other_idx)
    for i in key_idx:
        pixel[i] = _clamp_byte(pixel[i] + (target - pixel[i]) * strength)
    return pixel[0], pixel[1], pixel[2]


def _clamp_byte(value: float) -> int:
    return max(0, min(255, round(value)))
