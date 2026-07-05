from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from PIL import Image

from .exporter import ImageSource
from .spec import LINE_STATIC_SPEC, LINEStickerSpec


@dataclass(frozen=True)
class StickerPreview:
    index: int
    filename: str
    included: bool
    width: int
    height: int
    mode: str
    has_alpha: bool
    is_line_size: bool


@dataclass(frozen=True)
class PackPreview:
    stickers: tuple[StickerPreview, ...]
    selected_count: int
    errors: tuple[str, ...]


def build_pack_preview(
    stickers: Sequence[ImageSource],
    *,
    selected: Sequence[int] | None = None,
    spec: LINEStickerSpec = LINE_STATIC_SPEC,
) -> PackPreview:
    selected_indexes = tuple(selected or range(1, min(len(stickers), spec.sticker_count) + 1))
    selected_set = set(selected_indexes)
    errors = _selection_errors(selected_indexes, len(stickers), spec)
    previews: list[StickerPreview] = []

    for index, source in enumerate(stickers, start=1):
        with _open_preview_image(source) as image:
            previews.append(
                StickerPreview(
                    index=index,
                    filename=f"{index:02d}.png",
                    included=index in selected_set,
                    width=image.width,
                    height=image.height,
                    mode=image.mode,
                    has_alpha=_has_alpha(image),
                    is_line_size=image.size == spec.sticker_size,
                )
            )

    return PackPreview(
        stickers=tuple(previews),
        selected_count=sum(1 for item in previews if item.included),
        errors=tuple(errors),
    )


def _open_preview_image(source: ImageSource) -> Image.Image:
    if isinstance(source, Image.Image):
        return source.copy()
    return Image.open(Path(source))


def _has_alpha(image: Image.Image) -> bool:
    if image.mode in {"RGBA", "LA"}:
        return image.getextrema()[-1][0] < 255
    if image.mode == "P" and "transparency" in image.info:
        return True
    return False


def _selection_errors(
    selected: Sequence[int],
    total: int,
    spec: LINEStickerSpec,
) -> list[str]:
    errors: list[str] = []
    if len(selected) != spec.sticker_count:
        errors.append(f"expected {spec.sticker_count} selected stickers, got {len(selected)}")
    if len(set(selected)) != len(selected):
        errors.append("selected stickers must not repeat")
    invalid = [index for index in selected if index < 1 or index > total]
    if invalid:
        errors.append(f"selected stickers out of range: {', '.join(str(index) for index in invalid)}")
    return errors
