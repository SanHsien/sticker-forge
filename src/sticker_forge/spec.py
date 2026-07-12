from __future__ import annotations

from dataclasses import dataclass


RGBColor = tuple[int, int, int]
RGBAColor = tuple[int, int, int, int]


@dataclass(frozen=True)
class ChromaKey:
    name: str
    label: str
    hex: str
    rgb: RGBColor
    forbidden_label: str
    avoid: str
    substitutions: str


@dataclass(frozen=True)
class ChromaTuneProfile:
    hard: float
    soft: float
    min_key: int
    max_other: int
    dominance: float


@dataclass(frozen=True)
class LINEStickerSpec:
    sticker_size: tuple[int, int] = (370, 320)
    main_size: tuple[int, int] = (240, 240)
    tab_size: tuple[int, int] = (96, 74)
    sticker_count: int = 8
    grid_rows: int = 3
    grid_columns: int = 3
    split_inset_ratio: float = 0.03
    sticker_padding: int = 10
    main_padding: int = 12
    tab_padding: int = 4


LINE_STATIC_SPEC = LINEStickerSpec()
LINE_BIG_SPEC = LINEStickerSpec(sticker_size=(396, 660), sticker_padding=0)

CHROMA_KEYS = {
    "green": ChromaKey(
        name="green",
        label="PURE NEON GREEN",
        hex="#00FF00",
        rgb=(0, 255, 0),
        forbidden_label="green-screen color",
        avoid="green, neon green, chroma green, green-tinted colors",
        substitutions="red, orange, blue, purple, yellow, pink, or neutral colors",
    ),
    "magenta": ChromaKey(
        name="magenta",
        label="PURE NEON MAGENTA",
        hex="#FF00FF",
        rgb=(255, 0, 255),
        forbidden_label="magenta-screen color",
        avoid="magenta, hot pink, fuchsia, neon pink, purple-pink, magenta-tinted colors",
        substitutions="green, blue, orange, yellow, red, teal, or neutral colors",
    ),
}

CHROMA_TUNE_PROFILES = {
    "safe": ChromaTuneProfile(hard=0.32, soft=0.12, min_key=60, max_other=100, dominance=1.9),
    "balanced": ChromaTuneProfile(hard=0.25, soft=0.05, min_key=50, max_other=110, dominance=1.7),
    "aggressive": ChromaTuneProfile(
        hard=0.20,
        soft=0.04,
        min_key=40,
        max_other=125,
        dominance=1.45,
    ),
}


def resolve_chroma_key(name: str | None) -> ChromaKey:
    if not name:
        return CHROMA_KEYS["green"]
    return CHROMA_KEYS.get(name.lower(), CHROMA_KEYS["green"])


def resolve_chroma_tune(name: str | None) -> ChromaTuneProfile:
    if not name:
        return CHROMA_TUNE_PROFILES["balanced"]
    return CHROMA_TUNE_PROFILES.get(name.lower(), CHROMA_TUNE_PROFILES["balanced"])
