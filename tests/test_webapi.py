from __future__ import annotations

import base64
from io import BytesIO
from zipfile import ZipFile

from PIL import Image, ImageDraw

from sticker_forge.exporter import validate_effect_zip, validate_line_zip, validate_popup_zip
from sticker_forge.prompts import SUGGESTIONS
from sticker_forge.webapi import Api, _decode, _encode


def _grid_data_url(color=(0, 255, 0, 255), size=(300, 300)) -> str:
    buffer = BytesIO()
    Image.new("RGBA", size, color).save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def _animated_data_url(frames: int = 6) -> str:
    images = []
    for index in range(frames):
        image = Image.new("RGBA", (200, 200), (0, 255, 0, 255))
        draw = ImageDraw.Draw(image)
        draw.ellipse([20 + index * 8, 40, 50 + index * 8, 70], fill=(200, 30, 30, 255))
        images.append(image)
    buffer = BytesIO()
    images[0].save(buffer, format="PNG", save_all=True, append_images=images[1:], duration=120, loop=0, disposal=2)
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def test_bootstrap_exposes_localised_data() -> None:
    api = Api()
    zh = api.bootstrap("zh-Hant")
    en = api.bootstrap("en")
    assert zh["suggestions"]["character"] == SUGGESTIONS["zh-Hant"]["character"]
    assert en["suggestions"]["character"] == SUGGESTIONS["en"]["character"]
    assert zh["spec"]["stickerW"] == 370 and zh["spec"]["stickerH"] == 320
    assert set(zh["chromaKeys"]) == {"green", "magenta"}


def test_bootstrap_includes_presets() -> None:
    api = Api()
    presets = api.bootstrap("zh-Hant")["presets"]
    assert "office-cat" in presets
    assert len(presets["office-cat"]["texts"]) == 8


def test_write_line_zip_embeds_title_author(tmp_path) -> None:
    api = Api()
    tiles = [_decode(url) for url in api.split(_grid_data_url(), {"keyName": "green", "cleanup": True})][:8]
    output = api._write_line_zip(tiles, tmp_path / "p.zip", {"title": "My Pack", "author": "Me"})
    readme = ZipFile(output).read("README.txt").decode("utf-8")
    assert "My Pack" in readme and "Me" in readme


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


def test_export_message_bridge_cancels_without_window() -> None:
    api = Api()
    tile = _encode(Image.new("RGBA", (370, 320), (10, 20, 30, 255)))
    assert api.export_message([tile] * 8, {}) == {"cancelled": True}


def test_export_big_bridge_cancels_without_window() -> None:
    api = Api()
    tile = _encode(Image.new("RGBA", (370, 320), (10, 20, 30, 255)))
    assert api.export_big([tile] * 8, {}) == {"cancelled": True}


def test_prepare_screen_animations_returns_480_apng() -> None:
    api = Api()
    [preview] = api.prepare_screen_animations([_animated_data_url()], {"keyName": "green"})
    image = _decode(preview)
    assert image.size == (480, 480)
    assert image.getpixel((0, 0))[3] == 0


def test_write_popup_and_effect_zip_are_valid(tmp_path) -> None:
    api = Api()
    tiles = api.split(_grid_data_url(), {"keyName": "green", "cleanup": True})[:8]
    animations = api.prepare_screen_animations([_animated_data_url() for _ in range(8)], {"keyName": "green"})

    popup = api._write_screen_zip(
        "popup",
        tiles,
        animations,
        tmp_path / "popup.zip",
        {"title": "Popup Pack", "author": "Tester"},
    )
    effect = api._write_screen_zip(
        "effect",
        tiles,
        animations,
        tmp_path / "effect.zip",
        {"title": "Effect Pack", "author": "Tester"},
    )

    assert "saved" in popup and validate_popup_zip(tmp_path / "popup.zip") == []
    assert "saved" in effect and validate_effect_zip(tmp_path / "effect.zip") == []


def test_export_popup_effect_bridge_cancels_without_window() -> None:
    api = Api()
    tile = _encode(Image.new("RGBA", (370, 320), (10, 20, 30, 255)))
    animation = _animated_data_url()
    assert api.export_popup([tile] * 8, [animation] * 8, {}) == {"cancelled": True}
    assert api.export_effect([tile] * 8, [animation] * 8, {}) == {"cancelled": True}


def test_export_emoji_bridge_cancels_without_window() -> None:
    api = Api()
    tile = _encode(Image.new("RGBA", (370, 320), (10, 20, 30, 255)))
    # No window -> no save dialog -> cancelled (not a crash).
    assert api.export_emoji([tile] * 8, {}) == {"cancelled": True}


def test_export_platform_bridge_behaviour() -> None:
    api = Api()
    tile = _encode(Image.new("RGBA", (370, 320), (10, 20, 30, 255)))
    # No window bound -> save dialog unavailable -> cancelled (not a crash).
    assert api.export_platform([tile], {"platform": "telegram"}) == {"cancelled": True}
    # Unknown platform is reported, not raised.
    assert "error" in api.export_platform([tile], {"platform": "myspace"})


def test_write_line_zip_is_valid(tmp_path) -> None:
    api = Api()
    tiles = api.split(_grid_data_url(), {"keyName": "green", "cleanup": True})
    selected = [_decode(url) for url in tiles[:8]]
    output = api._write_line_zip(selected, tmp_path / "pack.zip", {"padding": 10, "mainIndex": 2, "tabIndex": 3})
    assert ZipFile(output).namelist()
    assert validate_line_zip(output) == []


def test_tune_option_passes_preset_names_through() -> None:
    from sticker_forge.webapi import _tune_option

    assert _tune_option({"tune": "continuous"}) == "continuous"
    assert _tune_option({}) == "balanced"


def test_tune_option_translates_custom_profile_from_the_gui() -> None:
    from sticker_forge.webapi import _tune_option
    from sticker_forge.spec import resolve_chroma_tune

    payload = {
        "tune": {
            "hard": 0.3,
            "soft": 0.1,
            "minKey": 85,
            "maxOther": 100,
            "dominance": 2.1,
            "mode": "strict",
            "erode": 1,
            "bogus": "ignored",
        }
    }

    translated = _tune_option(payload)
    assert translated == {
        "hard": 0.3,
        "soft": 0.1,
        "min_key": 85,
        "max_other": 100,
        "dominance": 2.1,
        "mode": "strict",
        "erode": 1,
    }
    # It must actually build a usable profile.
    profile = resolve_chroma_tune(translated)
    assert profile.min_key == 85
    assert profile.erode == 1


def test_bootstrap_exposes_tune_profiles_for_the_advanced_panel() -> None:
    from sticker_forge.spec import CHROMA_TUNE_PROFILES
    from sticker_forge.webapi import Api

    profiles = Api().bootstrap()["tuneProfiles"]

    assert set(profiles) == set(CHROMA_TUNE_PROFILES)
    balanced = profiles["balanced"]
    # camelCase, because the GUI reads these straight into its sliders.
    assert balanced["minKey"] == CHROMA_TUNE_PROFILES["balanced"].min_key
    assert balanced["maxOther"] == CHROMA_TUNE_PROFILES["balanced"].max_other
    assert profiles["continuous"]["mode"] == "continuous"
    assert profiles["aggressive"]["erode"] == 1


def test_custom_tune_from_the_gui_changes_cleanup_output() -> None:
    import base64
    from io import BytesIO

    from PIL import Image, ImageDraw

    from sticker_forge.webapi import Api

    size = 120
    image = Image.new("RGBA", (size, size))
    for y in range(size):
        for x in range(size):
            ratio = x / size * 0.6 + y / size * 0.4
            image.putpixel(
                (x, y),
                (int(120 * ratio), int(255 - 65 * ratio), int(120 * ratio), 255),
            )
    ImageDraw.Draw(image).ellipse((36, 30, 84, 78), fill=(225, 90, 70, 255))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    url = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()

    api = Api()

    def kept(tune) -> int:
        result = api.cleanup([url], {"keyName": "green", "tune": tune})
        decoded = Image.open(
            BytesIO(base64.b64decode(result[0].split(",", 1)[1]))
        ).convert("RGBA")
        return sum(1 for pixel in decoded.get_flattened_data() if pixel[3] > 0)

    preset = kept("balanced")
    conservative = kept(
        {"hard": 0.4, "soft": 0.3, "minKey": 90, "maxOther": 80, "dominance": 2.2}
    )

    # A conservative custom profile must keep visibly more than the preset,
    # otherwise the sliders are not reaching the core.
    assert conservative > preset
