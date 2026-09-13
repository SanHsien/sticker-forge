"""White sticker outline and drop shadow, applied after background removal.

Ported from upstream `line-sticker-studio`'s `applyOutlineAndShadow`. The white
keyline is the classic chat-sticker look and it also keeps dark characters
readable against LINE's dark chat themes. Doing it here is far more reliable
than asking an image model for "a white outline" in the prompt.

Styles:

- ``none``   -- leave the image alone.
- ``simple`` -- hard white keyline.
- ``fancy``  -- white keyline with a feathered edge plus a soft drop shadow.
"""

from __future__ import annotations

from PIL import Image, ImageChops, ImageFilter

OUTLINE_STYLES = ("none", "simple", "fancy")

# Upstream constants, kept so output matches the reference implementation.
_OUTLINE_PX = 7
_FEATHER_PX = 2
_SOLID_ALPHA = 64
_FEATHER_ALPHAS = (180, 100)
_SHADOW_OFFSET = (2, 3)
_SHADOW_BLUR = 2
_SHADOW_MAX_ALPHA = 70
_SHADOW_MIN_ALPHA = 4


def apply_outline_and_shadow(
    image: Image.Image,
    style: str = "none",
    *,
    outline_px: int = _OUTLINE_PX,
) -> Image.Image:
    """Draw a white outline (and for ``fancy``, a drop shadow) around the art."""
    if style not in OUTLINE_STYLES:
        raise ValueError(f"outline style must be one of {OUTLINE_STYLES}")
    if style == "none":
        return image
    if outline_px < 1:
        raise ValueError("outline_px must be at least 1")

    source = image.convert("RGBA")
    width, height = source.size
    # Treat near-transparent pixels as background so anti-aliased edges do not
    # push the outline outwards.
    solid = source.getchannel("A").point(
        lambda value: 255 if value >= _SOLID_ALPHA else 0
    )
    if not solid.getbbox():
        return source

    feather = _FEATHER_PX if style == "fancy" else 0
    # Build the outline alpha from the widest ring inwards so the innermost
    # (fully opaque) ring wins where the rings overlap.
    outline_alpha = Image.new("L", (width, height), 0)
    rings: list[tuple[int, int]] = []
    if feather:
        rings.append((outline_px + feather, _FEATHER_ALPHAS[1]))
        rings.append((outline_px + 1, _FEATHER_ALPHAS[0]))
    rings.append((outline_px, 255))
    for radius, alpha in rings:
        outline_alpha.paste(alpha, (0, 0), _dilate(solid, radius))

    # The outline only ever paints outside the artwork.
    outline_alpha.paste(0, (0, 0), solid)

    white = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    white.putalpha(outline_alpha)
    # Where the outline paints, it replaces the pixel outright (upstream
    # overwrites those pixels), so composite by the outline's own coverage.
    result = Image.composite(white, source, outline_alpha.point(lambda v: 255 if v else 0))

    if style != "fancy":
        return result
    return _apply_drop_shadow(result)


def _apply_drop_shadow(image: Image.Image) -> Image.Image:
    """Add a soft dark shadow under the artwork, in still-transparent areas."""
    width, height = image.size
    current_alpha = image.getchannel("A")
    blurred = current_alpha.filter(ImageFilter.BoxBlur(_SHADOW_BLUR))
    # Sampling at (x - dx, y - dy) is the same as offsetting the source by
    # (dx, dy), which pushes the shadow down-right.
    offset_x, offset_y = _SHADOW_OFFSET
    shifted = ImageChops.offset(blurred, offset_x, offset_y)
    # Clear the wrapped-around edges that offset brings in from the far side.
    shifted.paste(0, (0, 0, width, offset_y))
    shifted.paste(0, (0, 0, offset_x, height))

    scale = _SHADOW_MAX_ALPHA / 255
    shadow_alpha = shifted.point(
        lambda value: (
            round(value * scale) if round(value * scale) > _SHADOW_MIN_ALPHA else 0
        )
    )
    # Only paint where the image is still fully transparent.
    empty = current_alpha.point(lambda value: 255 if value == 0 else 0)
    shadow_alpha = ImageChops.multiply(
        shadow_alpha, empty.point(lambda value: 255 if value else 0)
    )
    shadow_alpha.paste(0, (0, 0), ImageChops.invert(empty))

    shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    shadow.putalpha(shadow_alpha)
    return Image.alpha_composite(shadow, image)


def _dilate(mask: Image.Image, radius: int) -> Image.Image:
    """Grow a 0/255 mask by `radius` pixels using a square structuring element.

    Matches upstream's separable box dilation.
    """
    return mask.filter(ImageFilter.MaxFilter(radius * 2 + 1))
