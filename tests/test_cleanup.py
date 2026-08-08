from __future__ import annotations

from PIL import Image

from sticker_forge.cleanup import parse_hex_color, remove_chroma_background


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
