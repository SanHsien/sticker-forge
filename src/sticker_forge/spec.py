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
    # "strict" keys only pixels that pass the pure-key test, so uncertain
    # foreground edges survive. "continuous" keys purely on the key score,
    # which cleans stubborn backgrounds harder at the cost of thin edges.
    mode: str = "strict"
    # Fringe erosion passes applied to partial-alpha pixels touching a fully
    # transparent neighbour. Only "aggressive" enables it by default.
    erode: int = 0

    @property
    def is_custom(self) -> bool:
        """Custom profiles come from user-set values, not the named presets."""
        return self not in CHROMA_TUNE_PROFILES.values()


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
        erode=1,
    ),
    "continuous": ChromaTuneProfile(
        hard=0.25,
        soft=0.05,
        min_key=50,
        max_other=110,
        dominance=1.7,
        mode="continuous",
    ),
}

CHROMA_TUNE_NAMES = tuple(CHROMA_TUNE_PROFILES)

# Normalisation bounds for scoring how conservative a custom profile is.
_MIN_KEY_FLOOR, _MIN_KEY_RANGE = 20, 70
_DOMINANCE_FLOOR, _DOMINANCE_RANGE = 1.2, 1.0
_BALANCED_NORM = (
    (50 - _MIN_KEY_FLOOR) / _MIN_KEY_RANGE + (1.7 - _DOMINANCE_FLOOR) / _DOMINANCE_RANGE
) / 2


def resolve_chroma_key(name: str | None) -> ChromaKey:
    if not name:
        return CHROMA_KEYS["green"]
    return CHROMA_KEYS.get(name.lower(), CHROMA_KEYS["green"])


def resolve_chroma_tune(
    tune: str | ChromaTuneProfile | dict | None,
) -> ChromaTuneProfile:
    """Resolve a preset name, a custom mapping, or a profile into a profile."""
    if isinstance(tune, ChromaTuneProfile):
        return tune
    if isinstance(tune, dict):
        return make_chroma_tune(**tune)
    if not tune:
        return CHROMA_TUNE_PROFILES["balanced"]
    return CHROMA_TUNE_PROFILES.get(tune.lower(), CHROMA_TUNE_PROFILES["balanced"])


def make_chroma_tune(
    *,
    hard: float | None = None,
    soft: float | None = None,
    min_key: int | None = None,
    max_other: int | None = None,
    dominance: float | None = None,
    mode: str | None = None,
    erode: int | None = None,
    base: str = "balanced",
) -> ChromaTuneProfile:
    """Build a custom profile, filling unset fields from a named preset."""
    default = CHROMA_TUNE_PROFILES.get(base, CHROMA_TUNE_PROFILES["balanced"])
    profile = ChromaTuneProfile(
        hard=default.hard if hard is None else float(hard),
        soft=default.soft if soft is None else float(soft),
        min_key=default.min_key if min_key is None else int(min_key),
        max_other=default.max_other if max_other is None else int(max_other),
        dominance=default.dominance if dominance is None else float(dominance),
        mode=default.mode if mode is None else str(mode),
        erode=default.erode if erode is None else int(erode),
    )
    if profile.soft > profile.hard:
        raise ValueError("soft threshold must not exceed hard threshold")
    if profile.erode < 0:
        raise ValueError("erode must be non-negative")
    if profile.mode not in ("strict", "continuous"):
        raise ValueError("mode must be 'strict' or 'continuous'")
    return profile


def chroma_despill_strength(profile: ChromaTuneProfile) -> float:
    """How strongly to pull spill out of key-leaning pixels (0..1).

    Named presets always despill fully. A *custom* profile that is tuned more
    conservatively than "balanced" (higher min_key / dominance, i.e. the user
    wants less keyed out) also gets a gentler despill, so a cautious matte does
    not still aggressively rewrite edge colour.
    """
    if not profile.is_custom:
        return 1.0
    min_norm = _clamp01((profile.min_key - _MIN_KEY_FLOOR) / _MIN_KEY_RANGE)
    dominance_norm = _clamp01((profile.dominance - _DOMINANCE_FLOOR) / _DOMINANCE_RANGE)
    conservative = _clamp01(
        ((min_norm + dominance_norm) / 2 - _BALANCED_NORM) / (1 - _BALANCED_NORM)
    )
    return 1 - 0.35 * conservative


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))
