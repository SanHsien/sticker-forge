from __future__ import annotations

from PIL import Image

from sticker_forge.preview import build_pack_preview


def test_build_pack_preview_reports_selection_and_alpha() -> None:
    transparent = Image.new("RGBA", (370, 320), (255, 0, 0, 0))
    opaque = Image.new("RGBA", (300, 300), (255, 0, 0, 255))
    stickers = [transparent] + [opaque.copy() for _ in range(8)]

    preview = build_pack_preview(stickers, selected=[1, 2, 3, 4, 5, 6, 7, 9])

    assert preview.selected_count == 8
    assert preview.errors == ()
    assert preview.stickers[0].filename == "01.png"
    assert preview.stickers[0].has_alpha is True
    assert preview.stickers[0].is_line_size is True
    assert preview.stickers[1].is_line_size is False
    assert preview.stickers[7].included is False
    assert preview.stickers[8].included is True


def test_build_pack_preview_reports_invalid_selection() -> None:
    stickers = [Image.new("RGBA", (370, 320), (255, 0, 0, 255)) for _ in range(3)]

    preview = build_pack_preview(stickers, selected=[1, 1, 4])

    assert "expected 8 selected stickers, got 3" in preview.errors
    assert "selected stickers must not repeat" in preview.errors
    assert "selected stickers out of range: 4" in preview.errors
