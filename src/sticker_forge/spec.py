from __future__ import annotations

import re
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
    "blue": ChromaKey(
        name="blue",
        label="PURE NEON BLUE",
        hex="#0000FF",
        rgb=(0, 0, 255),
        forbidden_label="blue-screen color",
        avoid="blue, royal blue, cobalt, navy, blue-tinted colors",
        substitutions="red, orange, yellow, green, pink, or neutral colors",
    ),
    "cyan": ChromaKey(
        name="cyan",
        label="PURE NEON CYAN",
        hex="#00FFFF",
        rgb=(0, 255, 255),
        forbidden_label="cyan-screen color",
        avoid="cyan, aqua, turquoise, teal, cyan-tinted colors",
        substitutions="red, orange, yellow, purple, pink, or neutral colors",
    ),
    "yellow": ChromaKey(
        name="yellow",
        label="PURE NEON YELLOW",
        hex="#FFFF00",
        rgb=(255, 255, 0),
        forbidden_label="yellow-screen color",
        avoid="yellow, golden yellow, lemon, mustard, yellow-tinted colors",
        substitutions="red, blue, purple, green, pink, or neutral colors",
    ),
}

# Black, white and grey have no chroma, so a chroma key can never separate them
# from the foreground; anything with a smaller channel spread is rejected.
MIN_CHROMA_SPREAD = 60

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
    """Resolve a named key, or a custom ``#RRGGBB`` colour into a key.

    A custom colour that cannot work as a key raises ``ValueError`` with the
    reason, instead of silently keying nothing out.
    """
    if not name:
        return CHROMA_KEYS["green"]
    named = CHROMA_KEYS.get(name.lower())
    if named:
        return named
    if name.startswith("#"):
        return make_custom_chroma_key(name)
    return CHROMA_KEYS["green"]


def parse_chroma_hex(value: str) -> RGBColor:
    color = value.strip().removeprefix("#")
    # int(x, 16) alone also accepts signs and spaces ("-1", " f"), so match first.
    if not re.fullmatch(r"[0-9A-Fa-f]{6}", color):
        raise ValueError("chroma key must be a #RRGGBB colour, e.g. #FF8000")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def chroma_channels(rgb: RGBColor) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Split channels into those the key colour occupies and the rest.

    The midpoint between the strongest and weakest channel is the divider, so
    green gives ((1,), (0, 2)), magenta ((0, 2), (1,)) and cyan ((1, 2), (0,)).
    Any colour with chroma has channels on both sides of the midpoint.
    """
    mid = (max(rgb) + min(rgb)) / 2
    key = tuple(i for i in range(3) if rgb[i] > mid)
    return key, tuple(i for i in range(3) if i not in key)


def chroma_key_rejection(rgb: RGBColor) -> str:
    """Return why ``rgb`` cannot serve as a key colour, or ``""`` if it can."""
    hex_code = "#%02X%02X%02X" % tuple(rgb)
    if max(rgb) - min(rgb) < MIN_CHROMA_SPREAD:
        return (
            f"{hex_code} has no chroma (black, white and grey never do), so a "
            "chroma key cannot separate it; use a saturated colour such as "
            "#00FF00, #FF00FF or #0000FF"
        )
    key, other = chroma_channels(rgb)
    high = min(rgb[i] for i in key)
    low = max(rgb[i] for i in other)
    # The colour must key out cleanly under every built-in preset, the
    # strictest (safe) included; otherwise its own backdrop would survive or
    # be despilled to grey.
    for profile in CHROMA_TUNE_PROFILES.values():
        if not (
            high >= profile.min_key
            and low <= profile.max_other
            and high >= low * profile.dominance
            and (high - low) / 255 > profile.hard
        ):
            return (
                f"{hex_code} is not saturated enough, or sits on the boundary "
                "between two hues (the other channels are too bright), so the "
                "key would miss part of the background; use a purer colour "
                "such as #FF8000 or #00B7A8"
            )
    return ""


def make_custom_chroma_key(value: str) -> ChromaKey:
    rgb = parse_chroma_hex(value)
    reason = chroma_key_rejection(rgb)
    if reason:
        raise ValueError(reason)
    hex_code = "#%02X%02X%02X" % rgb
    return ChromaKey(
        name=hex_code,
        label=f"PURE {hex_code}",
        hex=hex_code,
        rgb=rgb,
        forbidden_label=f"{hex_code} screen color",
        avoid=(
            f"{hex_code}, colors close to it, and the whole hue family it shares "
            "channels with, including tinted shadows and highlights"
        ),
        substitutions="colors far from the background hue, or neutral colors",
    )


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
