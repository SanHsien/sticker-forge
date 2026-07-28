from __future__ import annotations

import io
from zipfile import ZipFile

from PIL import Image, ImageDraw

from sticker_forge import cli
from sticker_forge.cli import main


def test_windows_cli_replaces_unencodable_output(monkeypatch) -> None:
    stdout = io.TextIOWrapper(io.BytesIO(), encoding="cp1252")
    stderr = io.TextIOWrapper(io.BytesIO(), encoding="cp1252")
    monkeypatch.setattr(cli.sys, "platform", "win32")
    monkeypatch.setattr(cli.sys, "stdout", stdout)
    monkeypatch.setattr(cli.sys, "stderr", stderr)

    cli._configure_windows_output()

    assert stdout.encoding.lower() == "cp1252"
    assert stderr.encoding.lower() == "cp1252"
    assert stdout.errors == "replace"
    assert stderr.errors == "replace"


def _animated_gif(path, frames: int = 6) -> None:
    images = []
    for k in range(frames):
        image = Image.new("RGBA", (200, 200), (0, 255, 0, 255))
        draw = ImageDraw.Draw(image)
        draw.ellipse([20 + k * 8, 40, 50 + k * 8, 70], fill=(200, 30, 30, 255))
        images.append(image)
    images[0].save(path, format="PNG", save_all=True, append_images=images[1:], duration=120, loop=0, disposal=2)


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


def test_cli_prompt_preset_fills_fields(capsys) -> None:
    assert main(["prompt", "--preset", "office-cat"]) == 0
    output = capsys.readouterr().out
    assert "上班族貓" in output  # preset character
    assert "收到" in output  # preset text


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


def test_cli_export_multi_grid_16(tmp_path) -> None:
    grid = Image.new("RGBA", (300, 300), (0, 255, 0, 255))
    g1, g2 = tmp_path / "a.png", tmp_path / "b.png"
    grid.save(g1)
    grid.save(g2)
    output_path = tmp_path / "pack.zip"
    selection = ",".join(str(i) for i in range(1, 17))  # 16 cells from 2 grids

    assert main(["export", str(g1), str(g2), "-o", str(output_path), "--select", selection, "--main", "2", "--tab", "3"]) == 0

    with ZipFile(output_path) as archive:
        assert "16.png" in archive.namelist()
    assert main(["validate", str(output_path)]) == 0


def test_cli_emoji_creates_and_validates_zip(tmp_path) -> None:
    grid = Image.new("RGBA", (300, 300), (0, 255, 0, 255))
    grid_path = tmp_path / "grid.png"
    grid.save(grid_path)
    output_path = tmp_path / "emoji.zip"

    assert main(["emoji", str(grid_path), "-o", str(output_path), "--select", "1,2,3,4,5,6,7,8", "--thumb", "2"]) == 0

    with ZipFile(output_path) as archive:
        assert "008.png" in archive.namelist()
        assert "chat-thumbnail.png" in archive.namelist()
    assert main(["validate", str(output_path), "--emoji"]) == 0


def test_cli_message_creates_and_validates_zip(tmp_path) -> None:
    grid = Image.new("RGBA", (300, 300), (0, 255, 0, 255))
    grid_path = tmp_path / "grid.png"
    grid.save(grid_path)
    output_path = tmp_path / "message.zip"

    assert main(["message", str(grid_path), "-o", str(output_path), "--select", "1,2,3,4,5,6,7,8"]) == 0

    with ZipFile(output_path) as archive:
        names = archive.namelist()
        assert "main.png" in names and "08.png" in names
    assert main(["validate", str(output_path)]) == 0


def test_cli_big_creates_and_validates_zip(tmp_path) -> None:
    grid = Image.new("RGBA", (300, 300), (0, 255, 0, 255))
    grid_path = tmp_path / "grid.png"
    grid.save(grid_path)
    output_path = tmp_path / "big.zip"

    assert main(["big", str(grid_path), "-o", str(output_path), "--select", "1,2,3,4,5,6,7,8"]) == 0

    with ZipFile(output_path) as archive:
        names = archive.namelist()
        assert "main.png" in names and "08.png" in names
    assert main(["validate", str(output_path), "--big"]) == 0


def test_cli_animated_creates_zip(tmp_path) -> None:
    paths = []
    for i in range(8):
        p = tmp_path / f"s{i}.png"
        _animated_gif(p)
        paths.append(str(p))
    output_path = tmp_path / "anim.zip"

    assert main(["animated", *paths, "-o", str(output_path), "--main", "2"]) == 0

    with ZipFile(output_path) as archive:
        from io import BytesIO

        sticker = Image.open(BytesIO(archive.read("01.png")))
        assert sticker.is_animated and "main.png" in archive.namelist()


def test_cli_popup_creates_and_validates_zip(tmp_path) -> None:
    grid = Image.new("RGBA", (300, 300), (0, 255, 0, 255))
    grid_path = tmp_path / "grid.png"
    grid.save(grid_path)
    args = ["popup", str(grid_path), "-o", str(tmp_path / "popup.zip")]
    for i in range(8):
        p = tmp_path / f"popup-{i}.png"
        _animated_gif(p)
        args.extend(["-a", str(p)])

    assert main(args) == 0

    with ZipFile(tmp_path / "popup.zip") as archive:
        assert "popup-main.png" in archive.namelist()
        assert "popup-08.png" in archive.namelist()
    assert main(["validate", str(tmp_path / "popup.zip"), "--popup"]) == 0


def test_cli_effect_creates_and_validates_zip(tmp_path) -> None:
    grid = Image.new("RGBA", (300, 300), (0, 255, 0, 255))
    grid_path = tmp_path / "grid.png"
    grid.save(grid_path)
    args = ["effect", str(grid_path), "-o", str(tmp_path / "effect.zip")]
    for i in range(8):
        p = tmp_path / f"effect-{i}.png"
        _animated_gif(p)
        args.extend(["-a", str(p)])

    assert main(args) == 0

    with ZipFile(tmp_path / "effect.zip") as archive:
        assert "effect-main.png" in archive.namelist()
        assert "effect-08.png" in archive.namelist()
    assert main(["validate", str(tmp_path / "effect.zip"), "--effect"]) == 0


def test_cli_platform_creates_zip(tmp_path) -> None:
    grid = Image.new("RGBA", (300, 300), (0, 255, 0, 255))
    grid_path = tmp_path / "grid.png"
    grid.save(grid_path)
    output_path = tmp_path / "tg.zip"

    assert main(["platform", str(grid_path), "-o", str(output_path), "--target", "telegram"]) == 0

    with ZipFile(output_path) as archive:
        assert "01.png" in archive.namelist()


def test_cli_signal_platform_creates_and_validates_zip(tmp_path) -> None:
    grid = Image.new("RGBA", (300, 300), (0, 255, 0, 255))
    grid_path = tmp_path / "grid.png"
    grid.save(grid_path)
    output_path = tmp_path / "signal.zip"

    assert (
        main(
            [
                "platform",
                str(grid_path),
                "-o",
                str(output_path),
                "--target",
                "signal",
                "--title",
                "Signal Pack",
                "--author",
                "Tester",
                "--emoji",
                "😀",
            ]
        )
        == 0
    )

    with ZipFile(output_path) as archive:
        names = archive.namelist()
        assert "signal_manifest.json" in names and "cover.png" in names
    assert main(["validate", str(output_path), "--signal"]) == 0


def test_cli_preview_reports_grid_readiness(tmp_path, capsys) -> None:
    grid = Image.new("RGBA", (300, 300), (255, 255, 255, 0))
    grid_path = tmp_path / "grid.png"
    grid.save(grid_path)

    assert main(["preview", str(grid_path), "--select", "1,2,3,4,5,6,7,9"]) == 0

    output = capsys.readouterr().out
    assert "01.png" in output
    assert "09.png" in output
    assert "370x320" in output
