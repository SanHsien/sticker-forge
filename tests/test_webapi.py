from __future__ import annotations

import base64
from io import BytesIO
from zipfile import ZipFile

from PIL import Image

from sticker_forge.exporter import validate_line_zip
from sticker_forge.prompts import SUGGESTIONS
from sticker_forge.webapi import Api, _decode, _encode


def _grid_data_url(color=(0, 255, 0, 255), size=(300, 300)) -> str:
    buffer = BytesIO()
    Image.new("RGBA", size, color).save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def test_bootstrap_exposes_localised_data() -> None:
    api = Api()
    zh = api.bootstrap("zh-Hant")
    en = api.bootstrap("en")
    assert zh["suggestions"]["character"] == SUGGESTIONS["zh-Hant"]["character"]
    assert en["suggestions"]["character"] == SUGGESTIONS["en"]["character"]
    assert zh["spec"]["stickerW"] == 370 and zh["spec"]["stickerH"] == 320
    assert set(zh["chromaKeys"]) == {"green", "magenta"}


def test_render_prompt_matches_core() -> None:
    api = Api()
    text = api.render_prompt({"locale": "zh-Hant", "withText": True})
    assert "LINE 靜態貼圖" in text
    assert "{character}" not in text


def test_split_returns_nine_tiles_and_cleanup_makes_transparent() -> None:
    api = Api()
    tiles = api.split(_grid_data_url(), {"keyName": "green", "padding": 10, "cleanup": False})
    assert len(tiles) == 9
    # Without cleanup the green fill stays opaque.
    assert _decode(tiles[0]).getpixel((0, 0))[3] == 255

    cleaned = api.split(_grid_data_url(), {"keyName": "green", "cleanup": True})
    assert _decode(cleaned[0]).getpixel((0, 0))[3] == 0


def test_cleanup_endpoint_removes_key_colour() -> None:
    api = Api()
    tile = _encode(Image.new("RGBA", (370, 320), (0, 255, 0, 255)))
    out = api.cleanup([tile], {"keyName": "green", "tune": "balanced"})
    assert _decode(out[0]).getpixel((0, 0))[3] == 0


def test_write_line_zip_is_valid(tmp_path) -> None:
    api = Api()
    tiles = api.split(_grid_data_url(), {"keyName": "green", "cleanup": True})
    selected = [_decode(url) for url in tiles[:8]]
    output = api._write_line_zip(selected, tmp_path / "pack.zip", {"padding": 10})
    assert ZipFile(output).namelist()
    assert validate_line_zip(output) == []
