from __future__ import annotations

import pytest
from PIL import Image

from sticker_forge.decorate import OUTLINE_STYLES, apply_outline_and_shadow


def _art(size: int = 60) -> Image.Image:
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    for y in range(24, 36):
        for x in range(24, 36):
            image.putpixel((x, y), (40, 42, 50, 255))
    return image


def test_none_style_returns_image_untouched() -> None:
    art = _art()

    assert apply_outline_and_shadow(art, "none") is art


def test_simple_style_paints_white_ring_outside_the_art() -> None:
    art = _art()

    result = apply_outline_and_shadow(art, "simple")

    # Artwork itself is untouched.
    assert result.getpixel((30, 30)) == (40, 42, 50, 255)
    # A pixel just outside the art becomes opaque white.
    assert result.getpixel((30, 22)) == (255, 255, 255, 255)
    # Far outside stays transparent.
    assert result.getpixel((2, 2))[3] == 0


def test_outline_width_is_configurable() -> None:
    art = _art()

    narrow = apply_outline_and_shadow(art, "simple", outline_px=2)
    wide = apply_outline_and_shadow(art, "simple", outline_px=9)

    def opaque(image: Image.Image) -> int:
        return sum(1 for pixel in image.get_flattened_data() if pixel[3] == 255)

    assert opaque(wide) > opaque(narrow)
    # 6px above the art is outside a 2px outline but inside a 9px one.
    assert narrow.getpixel((30, 18))[3] == 0
    assert wide.getpixel((30, 18)) == (255, 255, 255, 255)


def test_fancy_style_adds_feathered_edge_and_shadow() -> None:
    art = _art()

    simple = apply_outline_and_shadow(art, "simple")
    fancy = apply_outline_and_shadow(art, "fancy")

    def partial(image: Image.Image) -> int:
        return sum(1 for pixel in image.get_flattened_data() if 0 < pixel[3] < 255)

    # The feather and the drop shadow are both partially transparent, so fancy
    # must introduce partial-alpha pixels that the hard outline does not have.
    assert partial(simple) == 0
    assert partial(fancy) > 0
    # Artwork still intact.
    assert fancy.getpixel((30, 30)) == (40, 42, 50, 255)


def test_fancy_shadow_falls_below_and_right() -> None:
    art = _art()

    fancy = apply_outline_and_shadow(art, "fancy")

    def shadow_pixels(box: tuple[int, int, int, int]) -> int:
        left, top, right, bottom = box
        count = 0
        for y in range(top, bottom):
            for x in range(left, right):
                red, green, blue, alpha = fancy.getpixel((x, y))
                if 0 < alpha < 255 and red == green == blue == 0:
                    count += 1
        return count

    # Shadow is offset down-right, so there is more of it below than above.
    assert shadow_pixels((20, 44, 40, 52)) > shadow_pixels((20, 8, 40, 16))


def test_fully_transparent_input_is_left_alone() -> None:
    blank = Image.new("RGBA", (20, 20), (0, 0, 0, 0))

    result = apply_outline_and_shadow(blank, "fancy")

    assert result.getbbox() is None


def test_invalid_style_and_width_are_rejected() -> None:
    art = _art()

    with pytest.raises(ValueError):
        apply_outline_and_shadow(art, "sparkly")
    with pytest.raises(ValueError):
        apply_outline_and_shadow(art, "simple", outline_px=0)


def test_outline_styles_are_exposed_for_cli_and_gui() -> None:
    assert OUTLINE_STYLES == ("none", "simple", "fancy")
