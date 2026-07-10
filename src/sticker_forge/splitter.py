from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageSequence

from .spec import LINE_STATIC_SPEC, LINEStickerSpec, RGBAColor


def split_grid(
    image: Image.Image,
    rows: int = 3,
    columns: int = 3,
    *,
    inset_ratio: float = 0,
) -> list[Image.Image]:
    """Split a regular image grid into row-major cells.

    Cell size is floored, so sizes that do not divide evenly (e.g. the common
    1024x1024 AI export) are handled by dropping the leftover pixels on the
    right and bottom edges. This matches the web app's ``Math.floor`` behavior.
    """
    if rows <= 0 or columns <= 0:
        raise ValueError("rows and columns must be positive")
    if inset_ratio < 0 or inset_ratio >= 0.5:
        raise ValueError("inset_ratio must be between 0 and 0.5")

    width, height = image.size
    cell_width = width // columns
    cell_height = height // rows
    if cell_width <= 0 or cell_height <= 0:
        raise ValueError(
            f"image size {width}x{height} is too small to split into {columns}x{rows} cells"
        )
    cells: list[Image.Image] = []

    for row in range(rows):
        for column in range(columns):
            inset_x = round(cell_width * inset_ratio)
            inset_y = round(cell_height * inset_ratio)
            left = column * cell_width + inset_x
            upper = row * cell_height + inset_y
            box = (left, upper, left + cell_width, upper + cell_height)
            if inset_x or inset_y:
                box = (
                    left,
                    upper,
                    column * cell_width + cell_width - inset_x,
                    row * cell_height + cell_height - inset_y,
                )
            cells.append(image.crop(box).convert("RGBA"))

    return cells


def split_grid_to_stickers(
    image: Image.Image,
    *,
    spec: LINEStickerSpec = LINE_STATIC_SPEC,
    background: RGBAColor = (0, 255, 0, 255),
) -> list[Image.Image]:
    """Split a grid and contain-fit each cell into LINE sticker dimensions."""
    from .exporter import fit_to_canvas

    cells = split_grid(
        image,
        rows=spec.grid_rows,
        columns=spec.grid_columns,
        inset_ratio=spec.split_inset_ratio,
    )
    return [
        fit_to_canvas(cell, spec.sticker_size, background=background)
        for cell in cells
    ]


def load_animated_frames(source: str | Path) -> tuple[list[Image.Image], list[int]]:
    """Load one animated image (GIF/APNG) into its RGBA frames + per-frame durations.

    Each animated file is one animated sticker. Returns (frames, durations in ms).
    """
    frames: list[Image.Image] = []
    durations: list[int] = []
    with Image.open(source) as image:
        for frame in ImageSequence.Iterator(image):
            durations.append(int(frame.info.get("duration", 100) or 100))
            frames.append(frame.convert("RGBA").copy())
    if not frames:
        raise ValueError("no frames found in the animated source")
    return frames, durations


def split_grid_file(
    input_path: str | Path,
    output_dir: str | Path,
    *,
    rows: int = 3,
    columns: int = 3,
    prefix: str = "sticker",
    inset_ratio: float = 0,
) -> list[Path]:
    """Split an input grid image and save numbered PNG cells."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    with Image.open(input_path) as image:
        cells = split_grid(image, rows=rows, columns=columns, inset_ratio=inset_ratio)

    paths: list[Path] = []
    for index, cell in enumerate(cells, start=1):
        path = output / f"{prefix}-{index:02d}.png"
        cell.save(path)
        paths.append(path)

    return paths
