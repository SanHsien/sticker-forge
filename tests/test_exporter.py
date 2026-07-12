from __future__ import annotations

import json
from io import BytesIO
from zipfile import ZipFile

from PIL import Image, ImageDraw

from sticker_forge.exporter import (
    export_animated_zip,
    export_big_zip,
    export_emoji_zip,
    export_line_zip,
    export_message_zip,
    export_platform_zip,
    export_stickers_zip,
    fit_to_canvas,
    validate_big_zip,
    validate_emoji_zip,
    validate_line_zip,
    validate_signal_zip,
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


def test_export_platform_zip_signal_has_manifest_and_cover(tmp_path) -> None:
    output = export_platform_zip(
        _stickers()[:3],
        tmp_path / "signal.zip",
        platform="signal",
        title="Signal Pack",
        author="Tester",
        emoji="😀,😄,😉",
    )
    with ZipFile(output) as archive:
        names = set(archive.namelist())
        assert {"01.png", "03.png", "cover.png", "signal_manifest.json", "README.txt"} <= names
        manifest = json.loads(archive.read("signal_manifest.json").decode("utf-8"))
        assert manifest["title"] == "Signal Pack"
        assert manifest["author"] == "Tester"
        assert manifest["cover"] == "cover.png"
        assert manifest["stickers"][0] == {"file": "01.png", "emoji": "😀"}
        sticker = Image.open(BytesIO(archive.read("01.png")))
        assert sticker.size == (512, 512)
        cover = Image.open(BytesIO(archive.read("cover.png")))
        assert cover.size == (512, 512)
    assert validate_signal_zip(output) == []


def test_export_platform_zip_signal_rejects_wrong_emoji_count(tmp_path) -> None:
    try:
        export_platform_zip(_stickers()[:3], tmp_path / "signal.zip", platform="signal", emoji="😀,😄")
    except ValueError as exc:
        assert "Signal emoji list" in str(exc)
    else:
        raise AssertionError("Signal export should reject emoji lists that do not match sticker count")


def test_export_platform_zip_rejects_unknown_platform(tmp_path) -> None:
    try:
        export_platform_zip(_stickers()[:1], tmp_path / "x.zip", platform="myspace")
    except ValueError as exc:
        assert "unknown platform" in str(exc)
    else:
        raise AssertionError("export_platform_zip should reject unknown platforms")


def _animated_sticker_path(tmp_path, name, frames: int = 6):
    images = []
    for k in range(frames):
        image = Image.new("RGBA", (200, 200), (0, 255, 0, 255))
        draw = ImageDraw.Draw(image)
        draw.ellipse([20 + k * 8, 40, 50 + k * 8, 70], fill=(200, 30, 30, 255))
        images.append(image)
    path = tmp_path / name
    images[0].save(path, format="PNG", save_all=True, append_images=images[1:], duration=120, loop=0, disposal=2)
    return path


def test_export_animated_zip(tmp_path) -> None:
    from sticker_forge.splitter import load_animated_frames

    sticker_frames = []
    durations = []
    for i in range(8):
        frames, frame_durations = load_animated_frames(_animated_sticker_path(tmp_path, f"s{i}.png"))
        sticker_frames.append(frames)
        durations.append(frame_durations)
    output = export_animated_zip(sticker_frames, tmp_path / "a.zip", durations=durations)
    with ZipFile(output) as archive:
        names = set(archive.namelist())
        assert {"main.png", "tab.png", "01.png", "08.png", "README.txt"} <= names
        sticker = Image.open(BytesIO(archive.read("01.png")))
        assert sticker.is_animated and sticker.n_frames == 6
        w, h = sticker.size
        assert w <= 320 and h <= 270 and (w >= 270 or h >= 270)
        main = Image.open(BytesIO(archive.read("main.png")))
        assert main.is_animated and main.size == (240, 240)
        tab = Image.open(BytesIO(archive.read("tab.png")))
        assert tab.size == (96, 74) and getattr(tab, "n_frames", 1) == 1


def test_export_animated_zip_rejects_frame_count(tmp_path) -> None:
    single_frame = [[Image.new("RGBA", (200, 200), (1, 2, 3, 255))] for _ in range(8)]
    try:
        export_animated_zip(single_frame, tmp_path / "a.zip")
    except ValueError as exc:
        assert "frames" in str(exc)
    else:
        raise AssertionError("animated export should require 5-20 frames")


def test_export_message_zip_structure(tmp_path) -> None:
    output = export_message_zip(_stickers(), tmp_path / "m.zip")  # 8
    with ZipFile(output) as archive:
        names = set(archive.namelist())
        assert {"main.png", "tab.png", "01.png", "08.png", "README.txt"} <= names
        assert "09.png" not in names
        assert "message" in archive.read("README.txt").decode("utf-8").lower()
    assert validate_line_zip(output) == []


def test_export_big_zip_structure_and_validate(tmp_path) -> None:
    output = export_big_zip(_stickers(), tmp_path / "big.zip", title="Big Pack", author="Tester")
    with ZipFile(output) as archive:
        names = set(archive.namelist())
        assert {"main.png", "tab.png", "01.png", "08.png", "README.txt"} <= names
        sticker = Image.open(BytesIO(archive.read("01.png")))
        assert sticker.size == (396, 660)
        assert "Big Stickers" in archive.read("README.txt").decode("utf-8")
    assert validate_big_zip(output) == []


def test_export_message_zip_rejects_pack_size(tmp_path) -> None:
    try:
        export_message_zip(_stickers() * 4, tmp_path / "m.zip")  # 32 not allowed for message
    except ValueError as exc:
        assert "8 / 16 / 24" in str(exc)
    else:
        raise AssertionError("message packs cap at 24")


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


def test_validate_signal_zip_reports_bad_structure(tmp_path) -> None:
    output = tmp_path / "bad-signal.zip"
    with ZipFile(output, "w") as archive:
        archive.writestr("signal_manifest.json", '{"title":"","author":"","cover":"missing.png","stickers":[]}')
        archive.writestr("README.txt", "bad")

    errors = validate_signal_zip(output)

    assert any("missing files: cover.png" in error for error in errors)
