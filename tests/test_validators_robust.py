"""Validators must report broken input as errors instead of raising."""

from __future__ import annotations

import struct
import zlib
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

import pytest
from PIL import Image

from sticker_forge.cli import main
from sticker_forge.exporter import (
    validate_big_zip,
    validate_effect_zip,
    validate_emoji_zip,
    validate_line_zip,
    validate_popup_zip,
    validate_signal_zip,
)

VALIDATORS = [
    validate_line_zip,
    validate_big_zip,
    validate_emoji_zip,
    validate_popup_zip,
    validate_effect_zip,
    validate_signal_zip,
]


def _png() -> bytes:
    buffer = BytesIO()
    Image.new("RGBA", (512, 512), (0, 0, 0, 0)).save(buffer, format="PNG")
    return buffer.getvalue()


def _decompression_bomb_png() -> bytes:
    img = Image.new("RGB", (1, 1), (0, 0, 0))
    buf = BytesIO()
    img.save(buf, format="PNG")
    data = bytearray(buf.getvalue())
    pos = data.find(b"IHDR")
    struct.pack_into(">II", data, pos + 4, 20000, 20000)
    new_crc = zlib.crc32(data[pos : pos + 4 + 13])
    struct.pack_into(">I", data, pos + 4 + 13, new_crc)
    return bytes(data)


def _corrupt_deflate_zip(entries: dict[str, bytes], corrupt_name: str) -> bytes:
    buf = BytesIO()
    with ZipFile(buf, "w", compression=ZIP_DEFLATED) as archive:
        for name, content in entries.items():
            archive.writestr(name, content)
    data = bytearray(buf.getvalue())
    idx = data.find(corrupt_name.encode("utf-8"))
    header_start = idx - 26
    payload_start = header_start + 30 + len(corrupt_name)
    for i in range(payload_start, payload_start + 10):
        data[i] = 0xFF
    return bytes(data)


def _corrupt_crc_zip(entries: dict[str, bytes], corrupt_name: str) -> bytes:
    buf = BytesIO()
    with ZipFile(buf, "w", compression=ZIP_STORED) as archive:
        for name, content in entries.items():
            archive.writestr(name, content)
    data = bytearray(buf.getvalue())
    idx = data.find(corrupt_name.encode("utf-8"))
    header_start = idx - 26
    payload_start = header_start + 30 + len(corrupt_name)
    data[payload_start + 2] ^= 0x01
    return bytes(data)


@pytest.mark.parametrize("validator", VALIDATORS)
def test_validators_report_a_file_that_is_not_a_zip(tmp_path, validator) -> None:
    broken = tmp_path / "broken.zip"
    broken.write_text("this is not a zip archive")

    errors = validator(broken)

    assert errors
    assert any("ZIP" in error for error in errors)


def test_validate_line_zip_reports_unreadable_images(tmp_path) -> None:
    broken = tmp_path / "garbage.zip"
    with ZipFile(broken, "w") as archive:
        archive.writestr("README.txt", "x")
        archive.writestr("main.png", b"garbage")
        archive.writestr("tab.png", b"garbage")
        for index in range(1, 9):
            archive.writestr(f"{index:02d}.png", b"garbage")

    errors = validate_line_zip(broken)

    assert "main.png is not a readable image" in errors
    assert "08.png is not a readable image" in errors


def test_validate_emoji_zip_reports_unreadable_images(tmp_path) -> None:
    broken = tmp_path / "garbage-emoji.zip"
    with ZipFile(broken, "w") as archive:
        for index in range(1, 9):
            archive.writestr(f"{index:03d}.png", b"garbage")

    assert "001.png is not a readable image" in validate_emoji_zip(broken)


@pytest.mark.parametrize("validator", [validate_popup_zip, validate_effect_zip])
def test_validate_screen_animation_zip_reports_unreadable_images(tmp_path, validator) -> None:
    prefix = "popup" if validator is validate_popup_zip else "effect"
    broken = tmp_path / "garbage-screen.zip"
    with ZipFile(broken, "w") as archive:
        archive.writestr("README.txt", "x")
        for name in ["main.png", "tab.png", f"{prefix}-main.png"]:
            archive.writestr(name, b"garbage")
        for index in range(1, 9):
            archive.writestr(f"{index:02d}.png", b"garbage")
            archive.writestr(f"{prefix}-{index:02d}.png", b"garbage")

    errors = validator(broken)

    assert "main.png is not a readable image" in errors
    assert f"{prefix}-01.png is not a readable image" in errors


@pytest.mark.parametrize("manifest", ["[]", '"text"', "null", "42"])
def test_validate_signal_zip_rejects_a_manifest_that_is_not_an_object(tmp_path, manifest) -> None:
    broken = tmp_path / "list-manifest.zip"
    with ZipFile(broken, "w") as archive:
        archive.writestr("README.txt", "x")
        archive.writestr("cover.png", _png())
        archive.writestr("signal_manifest.json", manifest)

    errors = validate_signal_zip(broken)

    assert any("signal_manifest.json must be a JSON object" in error for error in errors)


def test_validate_signal_zip_reports_unreadable_cover_and_sticker(tmp_path) -> None:
    broken = tmp_path / "garbage-signal.zip"
    manifest = '{"title":"t","author":"a","cover":"cover.png","stickers":[{"file":"01.png","emoji":"x"}]}'
    with ZipFile(broken, "w") as archive:
        archive.writestr("README.txt", "x")
        archive.writestr("cover.png", b"garbage")
        archive.writestr("01.png", b"garbage")
        archive.writestr("signal_manifest.json", manifest)

    errors = validate_signal_zip(broken)

    assert "cover.png is not a readable image" in errors
    assert "01.png is not a readable image" in errors


def test_cli_validate_exits_1_for_a_file_that_is_not_a_zip(tmp_path, capsys) -> None:
    broken = tmp_path / "broken.zip"
    broken.write_text("nope")

    assert main(["validate", str(broken)]) == 1
    assert "ZIP" in capsys.readouterr().out


def test_validate_line_zip_reports_deflate_corruption_as_unreadable_image(tmp_path) -> None:
    entries = {
        "README.txt": b"x",
        "main.png": b"deflated dummy content " * 100,
        "tab.png": b"garbage",
        **{f"{i:02d}.png": b"garbage" for i in range(1, 9)},
    }
    broken = tmp_path / "deflate-corrupt.zip"
    broken.write_bytes(_corrupt_deflate_zip(entries, "main.png"))

    errors = validate_line_zip(broken)

    assert "main.png is not a readable image" in errors
    assert "tab.png is not a readable image" in errors


def test_validate_line_zip_reports_crc_error_without_early_exit(tmp_path) -> None:
    entries = {
        "README.txt": b"x",
        "main.png": b"crc dummy content " * 20,
        "tab.png": b"garbage",
        **{f"{i:02d}.png": b"garbage" for i in range(1, 9)},
    }
    broken = tmp_path / "crc-corrupt.zip"
    broken.write_bytes(_corrupt_crc_zip(entries, "main.png"))

    errors = validate_line_zip(broken)

    assert "main.png is not a readable image" in errors
    assert "tab.png is not a readable image" in errors
    assert "08.png is not a readable image" in errors


def test_validate_line_zip_reports_decompression_bomb_as_unreadable_image(tmp_path) -> None:
    broken = tmp_path / "bomb.zip"
    bomb_data = _decompression_bomb_png()
    with ZipFile(broken, "w") as archive:
        archive.writestr("README.txt", "x")
        archive.writestr("main.png", bomb_data)
        archive.writestr("tab.png", b"garbage")
        for index in range(1, 9):
            archive.writestr(f"{index:02d}.png", b"garbage")

    errors = validate_line_zip(broken)

    assert "main.png is not a readable image" in errors
    assert "tab.png is not a readable image" in errors


def test_validate_signal_zip_reports_deflate_corrupted_manifest(tmp_path) -> None:
    entries = {
        "README.txt": b"x",
        "cover.png": _png(),
        "signal_manifest.json": b'{"title":"test"}' * 20,
    }
    broken = tmp_path / "signal-deflate-corrupt.zip"
    broken.write_bytes(_corrupt_deflate_zip(entries, "signal_manifest.json"))

    errors = validate_signal_zip(broken)

    assert any("signal_manifest.json is invalid" in error for error in errors)


def test_cli_validate_handles_deflate_crc_and_bomb_without_traceback(tmp_path, capsys) -> None:
    entries = {
        "README.txt": b"x",
        "main.png": b"deflated dummy content " * 100,
        "tab.png": b"garbage",
        **{f"{i:02d}.png": b"garbage" for i in range(1, 9)},
    }
    p_deflate = tmp_path / "deflate.zip"
    p_deflate.write_bytes(_corrupt_deflate_zip(entries, "main.png"))
    assert main(["validate", str(p_deflate)]) == 1
    out, err = capsys.readouterr()
    assert "Traceback" not in err
    assert "main.png is not a readable image" in out

    p_crc = tmp_path / "crc.zip"
    p_crc.write_bytes(_corrupt_crc_zip(entries, "main.png"))
    assert main(["validate", str(p_crc)]) == 1
    out, err = capsys.readouterr()
    assert "Traceback" not in err
    assert "main.png is not a readable image" in out
    assert "08.png is not a readable image" in out

    p_bomb = tmp_path / "bomb.zip"
    with ZipFile(p_bomb, "w") as archive:
        archive.writestr("README.txt", "x")
        archive.writestr("main.png", _decompression_bomb_png())
        archive.writestr("tab.png", b"garbage")
        for index in range(1, 9):
            archive.writestr(f"{index:02d}.png", b"garbage")
    assert main(["validate", str(p_bomb)]) == 1
    out, err = capsys.readouterr()
    assert "Traceback" not in err
    assert "main.png is not a readable image" in out

@pytest.mark.parametrize("validator", [validate_line_zip, validate_big_zip, validate_emoji_zip])
def test_all_standard_validators_handle_decompression_bomb(tmp_path, validator) -> None:
    broken = tmp_path / "bomb-std.zip"
    bomb_data = _decompression_bomb_png()
    with ZipFile(broken, "w") as archive:
        archive.writestr("README.txt", "x")
        archive.writestr("main.png", bomb_data)
        archive.writestr("tab.png", b"garbage")
        for index in range(1, 9):
            archive.writestr(f"{index:02d}.png", b"garbage")
            archive.writestr(f"{index:03d}.png", b"garbage")

    errors = validator(broken)

    if validator is validate_emoji_zip:
        assert "001.png is not a readable image" in errors
    else:
        assert "main.png is not a readable image" in errors


@pytest.mark.parametrize("validator", [validate_popup_zip, validate_effect_zip])
def test_screen_animation_validators_handle_deflate_corrupted_animation(tmp_path, validator) -> None:
    prefix = "popup" if validator is validate_popup_zip else "effect"
    entries = {
        "README.txt": b"x",
        "main.png": b"garbage",
        "tab.png": b"garbage",
        f"{prefix}-main.png": b"corrupt anim content " * 100,
        **{f"{i:02d}.png": b"garbage" for i in range(1, 9)},
        **{f"{prefix}-{i:02d}.png": b"garbage" for i in range(1, 9)},
    }
    broken = tmp_path / f"{prefix}-deflate.zip"
    broken.write_bytes(_corrupt_deflate_zip(entries, f"{prefix}-main.png"))

    errors = validator(broken)

    assert f"{prefix}-main.png is not a readable image" in errors
    assert "main.png is not a readable image" in errors
