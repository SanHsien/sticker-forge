"""Pillow merges runs of identical frames; an export must not ship the result."""

from __future__ import annotations

from io import BytesIO
from zipfile import ZipFile

import pytest
from PIL import Image, ImageDraw

from sticker_forge.exporter import (
    export_animated_zip,
    export_effect_zip,
    export_popup_zip,
)


def _frame(step: int) -> Image.Image:
    image = Image.new("RGBA", (300, 270), (0, 0, 0, 0))
    ImageDraw.Draw(image).ellipse((50 + step * 6, 50, 200, 200), fill=(255, 0, 0, 255))
    return image


def _held(steps: list[int]) -> list[Image.Image]:
    return [_frame(step) for step in steps]


def _statics() -> list[Image.Image]:
    return [Image.new("RGBA", (100, 100), (index * 20, 40, 180, 255)) for index in range(8)]


def test_distinct_frames_keep_their_count(tmp_path) -> None:
    output = export_animated_zip([_held([0, 1, 2, 3, 4])] * 8, tmp_path / "ok.zip")

    with ZipFile(output) as archive:
        assert Image.open(BytesIO(archive.read("01.png"))).n_frames == 5


def test_animated_export_rejects_frames_that_merge_below_the_minimum(tmp_path) -> None:
    # Five frames in, but the four held frames collapse to one on save: 3 frames
    # out, which LINE rejects (5-20 frames).
    held = _held([0, 0, 0, 0, 1])

    with pytest.raises(ValueError, match="sticker 1"):
        export_animated_zip([held] * 8, tmp_path / "held.zip")


@pytest.mark.parametrize("exporter", [export_popup_zip, export_effect_zip])
def test_screen_animation_export_rejects_frames_that_merge_below_the_minimum(tmp_path, exporter) -> None:
    held = _held([0, 0, 0, 0, 1])

    with pytest.raises(ValueError, match="animation 1"):
        exporter(_statics(), [held] * 8, tmp_path / "held.zip")
