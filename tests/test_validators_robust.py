"""Validators must report broken input as errors instead of raising."""

from __future__ import annotations

from io import BytesIO
from zipfile import ZipFile

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
