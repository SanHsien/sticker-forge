"""Create non-infringing sample sticker assets for local testing."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


GREEN = (0, 255, 0)
PALETTE = [
    (245, 107, 107),
    (54, 162, 235),
    (255, 206, 86),
    (75, 192, 192),
    (153, 102, 255),
    (255, 159, 64),
    (80, 180, 120),
    (220, 120, 180),
    (120, 140, 220),
]


def font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def draw_face(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], color: tuple[int, int, int], label: str) -> None:
    left, top, right, bottom = box
    draw.ellipse((left, top, right, bottom), fill=color, outline=(30, 30, 30), width=5)
    width = right - left
    height = bottom - top
    eye_y = top + height * 38 // 100
    draw.ellipse((left + width * 30 // 100, eye_y, left + width * 38 // 100, eye_y + 18), fill=(30, 30, 30))
    draw.ellipse((left + width * 62 // 100, eye_y, left + width * 70 // 100, eye_y + 18), fill=(30, 30, 30))
    draw.arc(
        (left + width * 32 // 100, top + height * 46 // 100, right - width * 32 // 100, bottom - height * 20 // 100),
        start=20,
        end=160,
        fill=(30, 30, 30),
        width=5,
    )
    text_font = font(30)
    text_box = draw.textbbox((0, 0), label, font=text_font)
    text_w = text_box[2] - text_box[0]
    draw.text((left + (width - text_w) / 2, bottom + 12), label, fill=(30, 30, 30), font=text_font)


def create_static_grid(output_dir: Path) -> Path:
    size = 1024
    cell = size // 3
    image = Image.new("RGB", (size, size), GREEN)
    draw = ImageDraw.Draw(image)
    for index in range(9):
        row = index // 3
        col = index % 3
        x0 = col * cell
        y0 = row * cell
        margin = 58
        draw.rounded_rectangle(
            (x0 + 24, y0 + 24, x0 + cell - 24, y0 + cell - 24),
            radius=24,
            outline=(255, 255, 255),
            width=3,
        )
        draw_face(
            draw,
            (x0 + margin, y0 + margin, x0 + cell - margin, y0 + cell - margin - 36),
            PALETTE[index],
            f"S{index + 1}",
        )
    path = output_dir / "static-grid.png"
    image.save(path)
    return path


def create_animated_files(output_dir: Path) -> list[Path]:
    animated_dir = output_dir / "animated"
    animated_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for index in range(8):
        frames: list[Image.Image] = []
        for frame_index in range(6):
            image = Image.new("RGB", (320, 270), GREEN)
            draw = ImageDraw.Draw(image)
            offset = (frame_index % 3 - 1) * 12
            draw_face(
                draw,
                (54 + offset, 28, 266 + offset, 216),
                PALETTE[index],
                f"A{index + 1}",
            )
            frames.append(image)
        path = animated_dir / f"animated-{index + 1:02d}.gif"
        frames[0].save(path, save_all=True, append_images=frames[1:], duration=160, loop=0)
        paths.append(path)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Create sample sticker assets for sticker-forge.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "generated",
        help="Output directory. Defaults to examples/generated.",
    )
    args = parser.parse_args()
    output_dir = args.output.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    static_grid = create_static_grid(output_dir)
    animated_files = create_animated_files(output_dir)

    print(f"static grid: {static_grid}")
    print(f"animated files: {len(animated_files)} files in {output_dir / 'animated'}")


if __name__ == "__main__":
    main()
