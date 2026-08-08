from __future__ import annotations

import pytest
from PIL import Image

from sticker_forge.cleanup import parse_hex_color, remove_chroma_background
from sticker_forge.spec import (
    chroma_despill_strength,
    make_chroma_tune,
    resolve_chroma_tune,
)


def test_parse_hex_color_accepts_hash_prefix() -> None:
    assert parse_hex_color("#00ff80") == (0, 255, 128)


def test_remove_chroma_background_uses_corner_color_by_default() -> None:
    image = Image.new("RGBA", (3, 3), (0, 255, 0, 255))
    image.putpixel((1, 1), (255, 0, 0, 255))

    result = remove_chroma_background(image, tolerance=0)

    assert result.getpixel((0, 0)) == (0, 255, 0, 0)
    assert result.getpixel((1, 1)) == (255, 0, 0, 255)


def test_remove_chroma_background_uses_explicit_key_color() -> None:
    image = Image.new("RGBA", (2, 1), (255, 255, 255, 255))
    image.putpixel((1, 0), (0, 0, 255, 255))

    result = remove_chroma_background(image, key_color=(0, 0, 255), tolerance=0)

    assert result.getpixel((0, 0)) == (255, 255, 255, 255)
    assert result.getpixel((1, 0)) == (0, 0, 255, 0)


def test_remove_chroma_background_uses_named_magenta_key() -> None:
    image = Image.new("RGBA", (2, 1), (255, 0, 255, 255))
    image.putpixel((1, 0), (0, 0, 255, 255))

    result = remove_chroma_background(image, key_name="magenta")

    assert result.getpixel((0, 0)) == (255, 0, 255, 0)
    # Blue foreground next to a magenta key must stay blue, not be despilled to
    # black: it does not lean magenta, so despill must not touch it.
    assert result.getpixel((1, 0)) == (0, 0, 255, 255)


def test_remove_chroma_background_preserves_non_key_foreground() -> None:
    # Green key with opaque non-green foreground: red and blue patches must keep
    # their exact colour; only the green backdrop is removed.
    image = Image.new("RGBA", (3, 1), (0, 255, 0, 255))
    image.putpixel((1, 0), (200, 20, 20, 255))
    image.putpixel((2, 0), (20, 20, 200, 255))

    result = remove_chroma_background(image, key_name="green")

    assert result.getpixel((0, 0))[3] == 0
    assert result.getpixel((1, 0)) == (200, 20, 20, 255)
    assert result.getpixel((2, 0)) == (20, 20, 200, 255)


def test_continuous_mode_keys_impure_background_that_strict_keeps() -> None:
    # Muddy desaturated green fails the pure-key test, so strict mode keeps it
    # while continuous mode keys on score alone and removes it.
    image = Image.new("RGBA", (2, 1), (90, 140, 90, 255))
    image.putpixel((1, 0), (200, 30, 30, 255))

    strict = remove_chroma_background(image, key_name="green", tune="balanced")
    continuous = remove_chroma_background(image, key_name="green", tune="continuous")

    assert strict.getpixel((0, 0))[3] == 255
    assert continuous.getpixel((0, 0))[3] < 255
    # Neither mode may touch the red character.
    assert strict.getpixel((1, 0)) == (200, 30, 30, 255)
    assert continuous.getpixel((1, 0)) == (200, 30, 30, 255)


def test_source_alpha_is_composited_not_overwritten() -> None:
    # A half-transparent frame (e.g. an APNG cell) must never become more
    # opaque than it started.
    key = Image.new("RGBA", (1, 1), (0, 255, 0, 128))
    foreground = Image.new("RGBA", (1, 1), (200, 30, 30, 128))

    assert remove_chroma_background(key, key_name="green").getpixel((0, 0))[3] == 0
    assert (
        remove_chroma_background(foreground, key_name="green").getpixel((0, 0))[3] == 128
    )


def test_erode_removes_partial_alpha_fringe_touching_transparency() -> None:
    # (80, 120, 80) scores inside the aggressive soft..hard band, so it becomes
    # a partial-alpha fringe ring around the character.
    image = Image.new("RGBA", (9, 9), (0, 255, 0, 255))
    for y in range(3, 6):
        for x in range(3, 6):
            image.putpixel((x, y), (200, 30, 30, 255))
    ring = [(2, 3), (2, 4), (2, 5), (6, 3), (6, 4), (6, 5)]
    ring += [(3, 2), (4, 2), (5, 2), (3, 6), (4, 6), (5, 6)]
    for x, y in ring:
        image.putpixel((x, y), (80, 120, 80, 255))

    def fringe(img: Image.Image) -> int:
        return sum(1 for pixel in img.get_flattened_data() if 0 < pixel[3] < 255)

    kept = remove_chroma_background(
        image, key_name="green", tune=make_chroma_tune(erode=0, base="aggressive")
    )
    eroded = remove_chroma_background(image, key_name="green", tune="aggressive")

    assert fringe(kept) == len(ring)
    assert fringe(eroded) == 0
    # Erosion must not eat into the opaque character.
    assert eroded.getpixel((4, 4)) == (200, 30, 30, 255)


def test_conservative_custom_profile_softens_despill() -> None:
    assert chroma_despill_strength(resolve_chroma_tune("balanced")) == 1.0
    assert chroma_despill_strength(resolve_chroma_tune("continuous")) == 1.0
    # A custom profile tuned more conservatively than balanced despills gently.
    conservative = chroma_despill_strength(make_chroma_tune(min_key=85, dominance=2.1))
    assert 0 < conservative < 1.0
    # A looser-than-balanced custom profile still despills fully.
    assert chroma_despill_strength(make_chroma_tune(min_key=30, dominance=1.3)) == 1.0


def test_make_chroma_tune_rejects_invalid_values() -> None:
    with pytest.raises(ValueError):
        make_chroma_tune(hard=0.1, soft=0.4)
    with pytest.raises(ValueError):
        make_chroma_tune(erode=-1)
    with pytest.raises(ValueError):
        make_chroma_tune(mode="nonsense")
