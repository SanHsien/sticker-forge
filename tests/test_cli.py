from __future__ import annotations

from zipfile import ZipFile

from PIL import Image

from sticker_forge.cli import main


def test_cli_prompt_prints_template(capsys) -> None:
    assert main(["prompt"]) == 0

    output = capsys.readouterr().out
    assert "LINE 靜態貼圖" in output
    assert "有字版" in output
    assert "無字版" not in output
    assert "{character}" not in output


def test_cli_prompt_prints_english_template(capsys) -> None:
    assert main(["--lang", "en", "prompt"]) == 0

    output = capsys.readouterr().out
    assert "LINE static sticker" in output
    assert "Text version" in output
    assert "Good morning" in output


def test_cli_prompt_writes_utf8_file(tmp_path) -> None:
    output_path = tmp_path / "prompt.md"

    assert main(["prompt", "--character", "原創柴犬", "-o", str(output_path)]) == 0

    output = output_path.read_text(encoding="utf-8")
    assert "原創柴犬" in output
    assert "LINE 靜態貼圖" in output


def test_cli_english_help(capsys) -> None:
    try:
        main(["--lang", "en", "--help"])
    except SystemExit as exc:
        assert exc.code == 0

    output = capsys.readouterr().out
    assert "Local LINE static sticker pack toolkit." in output


def test_cli_export_creates_zip(tmp_path) -> None:
    grid = Image.new("RGBA", (300, 300), (255, 255, 255, 0))
    grid_path = tmp_path / "grid.png"
    grid.save(grid_path)
    output_path = tmp_path / "pack.zip"

    assert main(["export", str(grid_path), "-o", str(output_path), "--select", "1,2,3,4,5,6,7,9"]) == 0

    with ZipFile(output_path) as archive:
        assert "08.png" in archive.namelist()

    assert main(["validate", str(output_path)]) == 0


def _read_zip_image(archive_path, name):
    from io import BytesIO

    with ZipFile(archive_path) as archive:
        return Image.open(BytesIO(archive.read(name))).convert("RGBA")


def test_cli_export_removes_background_by_default(tmp_path) -> None:
    # A green-screen grid should export transparent stickers without any flag,
    # because LINE requires transparent backgrounds.
    grid = Image.new("RGBA", (300, 300), (0, 255, 0, 255))
    grid_path = tmp_path / "grid.png"
    grid.save(grid_path)
    output_path = tmp_path / "pack.zip"

    assert main(["export", str(grid_path), "-o", str(output_path)]) == 0

    sticker = _read_zip_image(output_path, "01.png")
    assert sticker.getpixel((0, 0))[3] == 0


def test_cli_export_keep_background_leaves_solid_fill(tmp_path) -> None:
    grid = Image.new("RGBA", (300, 300), (0, 255, 0, 255))
    grid_path = tmp_path / "grid.png"
    grid.save(grid_path)
    output_path = tmp_path / "pack.zip"

    assert main(["export", str(grid_path), "-o", str(output_path), "--keep-background"]) == 0

    # export adds a 10px transparent padding border, so check the center fill.
    sticker = _read_zip_image(output_path, "01.png")
    assert sticker.getpixel((185, 160)) == (0, 255, 0, 255)


def test_cli_stickers_creates_png_only_zip(tmp_path) -> None:
    grid = Image.new("RGBA", (300, 300), (255, 255, 255, 0))
    grid_path = tmp_path / "grid.png"
    grid.save(grid_path)
    output_path = tmp_path / "stickers.zip"

    assert main(["stickers", str(grid_path), "-o", str(output_path)]) == 0

    with ZipFile(output_path) as archive:
        assert archive.namelist()[-1] == "09.png"


def test_cli_preview_reports_grid_readiness(tmp_path, capsys) -> None:
    grid = Image.new("RGBA", (300, 300), (255, 255, 255, 0))
    grid_path = tmp_path / "grid.png"
    grid.save(grid_path)

    assert main(["preview", str(grid_path), "--select", "1,2,3,4,5,6,7,9"]) == 0

    output = capsys.readouterr().out
    assert "01.png" in output
    assert "09.png" in output
    assert "370x320" in output
