from __future__ import annotations

from PIL import Image

from sticker_forge.splitter import split_grid, split_grid_file, split_grid_to_stickers


def _grid_image() -> Image.Image:
    image = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
    colors = [
        (255, 0, 0, 255),
        (0, 255, 0, 255),
        (0, 0, 255, 255),
        (255, 255, 0, 255),
        (255, 0, 255, 255),
        (0, 255, 255, 255),
        (128, 0, 0, 255),
        (0, 128, 0, 255),
        (0, 0, 128, 255),
    ]

    for index, color in enumerate(colors):
        row = index // 3
        column = index % 3
        for x in range(column * 100, column * 100 + 100):
            for y in range(row * 100, row * 100 + 100):
                image.putpixel((x, y), color)

    return image


def test_split_grid_returns_row_major_cells() -> None:
    cells = split_grid(_grid_image())

    assert len(cells) == 9
    assert [cell.size for cell in cells] == [(100, 100)] * 9
    assert cells[0].getpixel((50, 50)) == (255, 0, 0, 255)
    assert cells[4].getpixel((50, 50)) == (255, 0, 255, 255)
    assert cells[8].getpixel((50, 50)) == (0, 0, 128, 255)


def test_split_grid_rejects_uneven_grid() -> None:
    image = Image.new("RGBA", (301, 300), (255, 255, 255, 255))

    try:
        split_grid(image)
    except ValueError as exc:
        assert "not evenly divisible" in str(exc)
    else:
        raise AssertionError("split_grid should reject uneven grid sizes")


def test_split_grid_supports_inset_ratio() -> None:
    cells = split_grid(_grid_image(), inset_ratio=0.1)

    assert [cell.size for cell in cells] == [(80, 80)] * 9
    assert cells[0].getpixel((40, 40)) == (255, 0, 0, 255)


def test_split_grid_to_stickers_outputs_line_size_with_key_background() -> None:
    stickers = split_grid_to_stickers(_grid_image(), background=(0, 255, 0, 255))

    assert len(stickers) == 9
    assert stickers[0].size == (370, 320)
    assert stickers[0].getpixel((0, 0)) == (0, 255, 0, 255)


def test_split_grid_file_writes_numbered_pngs(tmp_path) -> None:
    input_path = tmp_path / "grid.png"
    _grid_image().save(input_path)

    output_paths = split_grid_file(input_path, tmp_path / "cells", prefix="cell")

    assert len(output_paths) == 9
    assert output_paths[0].name == "cell-01.png"
    assert output_paths[-1].name == "cell-09.png"
    assert all(path.exists() for path in output_paths)
