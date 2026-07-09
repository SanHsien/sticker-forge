from __future__ import annotations

from io import BytesIO
from zipfile import ZipFile

from PIL import Image

from sticker_forge.exporter import (
    export_emoji_zip,
    export_line_zip,
    export_platform_zip,
    export_stickers_zip,
    fit_to_canvas,
    validate_emoji_zip,
    validate_line_zip,
)


def _stickers() -> list[Image.Image]:
    return [
        Image.new("RGBA", (100 + index, 80 + index), (index * 20, 40, 180, 255))
        for index in range(8)
    ]


def test_fit_to_canvas_preserves_target_size() -> None:
    image = Image.new("RGBA", (200, 100), (255, 0, 0, 255))

    result = fit_to_canvas(image, (370, 320), padding=10)

    assert result.size == (370, 320)
    assert result.mode == "RGBA"


def test_export_line_zip_writes_expected_structure(tmp_path) -> None:
    output = export_line_zip(_stickers(), tmp_path / "pack.zip", title="Demo", author="Tester")

    with ZipFile(output) as archive:
        names = set(archive.namelist())
        assert names == {
            "main.png",
            "tab.png",
            "01.png",
            "02.png",
            "03.png",
            "04.png",
            "05.png",
            "06.png",
            "07.png",
            "08.png",
            "README.txt",
        }

        with archive.open("01.png") as file:
            sticker = Image.open(BytesIO(file.read()))
            assert sticker.size == (370, 320)

        with archive.open("main.png") as file:
            main = Image.open(BytesIO(file.read()))
            assert main.size == (240, 240)

        with archive.open("tab.png") as file:
            tab = Image.open(BytesIO(file.read()))
            assert tab.size == (96, 74)

        readme = archive.read("README.txt").decode("utf-8")
        assert "Demo" in readme
        assert "Tester" in readme

    assert validate_line_zip(output) == []


def test_export_line_zip_rejects_invalid_pack_size(tmp_path) -> None:
    try:
        export_line_zip(_stickers()[:7], tmp_path / "pack.zip")
    except ValueError as exc:
        assert "8 / 16 / 24 / 32 / 40" in str(exc)
    else:
        raise AssertionError("export_line_zip should reject invalid pack sizes")


def test_export_line_zip_supports_larger_pack_and_main_tab(tmp_path) -> None:
    stickers = _stickers() + _stickers()  # 16
    output = export_line_zip(stickers, tmp_path / "pack.zip", main_index=2, tab_index=3)
    with ZipFile(output) as archive:
        names = set(archive.namelist())
        assert "16.png" in names and "09.png" in names
        assert "17.png" not in names
    assert validate_line_zip(output) == []


def test_export_stickers_zip_writes_png_only_pack(tmp_path) -> None:
    output = export_stickers_zip(_stickers() + [Image.new("RGBA", (90, 90))], tmp_path / "stickers.zip")

    with ZipFile(output) as archive:
        assert archive.namelist() == [
            "01.png",
            "02.png",
            "03.png",
            "04.png",
            "05.png",
            "06.png",
            "07.png",
            "08.png",
            "09.png",
        ]


def test_export_platform_zip_telegram_sizes_png(tmp_path) -> None:
    output = export_platform_zip(_stickers()[:3], tmp_path / "tg.zip", platform="telegram")
    with ZipFile(output) as archive:
        names = archive.namelist()
        assert "01.png" in names and "03.png" in names and "README.txt" in names
        image = Image.open(BytesIO(archive.read("01.png")))
        assert image.size == (512, 512)
        assert image.format == "PNG"


def test_export_platform_zip_whatsapp_has_webp_and_tray(tmp_path) -> None:
    output = export_platform_zip(_stickers()[:2], tmp_path / "wa.zip", platform="whatsapp")
    with ZipFile(output) as archive:
        names = archive.namelist()
        assert "01.webp" in names and "tray.png" in names
        sticker = Image.open(BytesIO(archive.read("01.webp")))
        assert sticker.size == (512, 512) and sticker.format == "WEBP"
        tray = Image.open(BytesIO(archive.read("tray.png")))
        assert tray.size == (96, 96)


def test_export_platform_zip_rejects_unknown_platform(tmp_path) -> None:
    try:
        export_platform_zip(_stickers()[:1], tmp_path / "x.zip", platform="myspace")
    except ValueError as exc:
        assert "unknown platform" in str(exc)
    else:
        raise AssertionError("export_platform_zip should reject unknown platforms")


def test_export_emoji_zip_structure_and_validate(tmp_path) -> None:
    output = export_emoji_zip(_stickers(), tmp_path / "e.zip", thumb_index=1)  # 8 emoji
    with ZipFile(output) as archive:
        names = set(archive.namelist())
        assert "001.png" in names and "008.png" in names
        assert "chat-thumbnail.png" in names and "README.txt" in names
        assert "009.png" not in names
        emoji = Image.open(BytesIO(archive.read("001.png")))
        assert emoji.size == (180, 180)
        thumb = Image.open(BytesIO(archive.read("chat-thumbnail.png")))
        assert thumb.size == (96, 74)
    assert validate_emoji_zip(output) == []


def test_export_emoji_zip_rejects_out_of_range(tmp_path) -> None:
    try:
        export_emoji_zip(_stickers()[:7], tmp_path / "e.zip")
    except ValueError as exc:
        assert "8-40" in str(exc)
    else:
        raise AssertionError("export_emoji_zip should reject fewer than 8 images")


def test_validate_line_zip_flags_opaque_stickers(tmp_path) -> None:
    # A structurally correct ZIP whose stickers have solid (opaque) backgrounds
    # should be flagged, because LINE requires transparent stickers.
    output = tmp_path / "opaque.zip"
    sizes = {"main.png": (240, 240), "tab.png": (96, 74)}
    sizes.update({f"{index:02d}.png": (370, 320) for index in range(1, 9)})
    with ZipFile(output, "w") as archive:
        for name, size in sizes.items():
            buffer = BytesIO()
            Image.new("RGBA", size, (0, 200, 0, 255)).save(buffer, format="PNG")
            archive.writestr(name, buffer.getvalue())
        archive.writestr("README.txt", "opaque test")

    errors = validate_line_zip(output)

    assert any("size is" not in error for error in errors)
    assert any("01.png has no transparent background" in error for error in errors)


def test_validate_line_zip_reports_bad_structure(tmp_path) -> None:
    output = tmp_path / "bad.zip"
    with ZipFile(output, "w") as archive:
        image = Image.new("RGBA", (1, 1), (255, 0, 0, 255))
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        archive.writestr("01.png", buffer.getvalue())

    errors = validate_line_zip(output)

    assert any("missing files" in error for error in errors)
    assert any("01.png size is 1x1" in error for error in errors)
