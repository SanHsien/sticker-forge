"""pywebview bridge: the desktop GUI is the HTML app driven by the Python core.

The window renders ``app/index.html`` and the JavaScript calls into ``Api``
for every non-UI operation (prompt text, splitting, cleanup, export). This
keeps a single source of truth — the Python core — instead of a parallel
JavaScript reimplementation.
"""

from __future__ import annotations

import base64
from dataclasses import replace
from io import BytesIO
from pathlib import Path

from PIL import Image

from .app_launcher import app_path
from .cleanup import remove_chroma_background
from .decorate import apply_outline_and_shadow
from .exporter import (
    LINE_ANIM_MAX_SIZE,
    LINE_SCREEN_ANIM_SIZE,
    PLATFORM_SPECS,
    _apng_bytes,
    _fit_frames_within,
    _fit_screen_frames,
    export_animated_zip,
    export_big_zip,
    export_effect_zip,
    export_emoji_zip,
    export_line_zip,
    export_message_zip,
    export_platform_zip,
    export_popup_zip,
    export_stickers_zip,
)
from .prompts import (
    DEFAULT_ACTIONS,
    DEFAULT_FIELDS,
    DEFAULT_TEXTS,
    PROMPT_PRESETS,
    SUGGESTIONS,
    normalize_locale,
    render_line_static_prompt,
)
from .spec import CHROMA_KEYS, CHROMA_TUNE_PROFILES, LINE_STATIC_SPEC, resolve_chroma_key
from .splitter import load_animated_frames
from .splitter import split_grid_to_stickers


def _decode(data_url: str) -> Image.Image:
    _, _, encoded = data_url.partition(",")
    raw = base64.b64decode(encoded or data_url)
    return Image.open(BytesIO(raw)).convert("RGBA")


def _encode(image: Image.Image) -> str:
    buffer = BytesIO()
    image.convert("RGBA").save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def _decode_animated(data_url: str) -> tuple[list[Image.Image], list[int]]:
    _, _, encoded = data_url.partition(",")
    raw = base64.b64decode(encoded or data_url)
    return load_animated_frames(BytesIO(raw))


def _encode_apng(frames: list[Image.Image], durations: list[int]) -> str:
    return "data:image/png;base64," + base64.b64encode(_apng_bytes(frames, durations)).decode("ascii")


def _encode_screen_apng(frames: list[Image.Image], durations: list[int]) -> str:
    return "data:image/png;base64," + base64.b64encode(
        _apng_bytes(frames, durations, max_loops=3, max_total_ms=3000)
    ).decode("ascii")


_TUNE_FIELDS = {
    "hard": "hard",
    "soft": "soft",
    "minKey": "min_key",
    "maxOther": "max_other",
    "dominance": "dominance",
    "mode": "mode",
    "erode": "erode",
    "base": "base",
}


def _tune_option(options: dict):
    """Read the tune option, which is either a preset name or a custom profile.

    The GUI's advanced panel sends a camelCase object; translate it to the
    Python core's field names so `resolve_chroma_tune` can build a profile.
    """
    tune = options.get("tune", "balanced")
    if not isinstance(tune, dict):
        return tune
    return {
        _TUNE_FIELDS[key]: value
        for key, value in tune.items()
        if key in _TUNE_FIELDS and value is not None
    }


def _spec_for(options: dict) -> "LINE_STATIC_SPEC.__class__":
    padding = int(options.get("padding", LINE_STATIC_SPEC.sticker_padding))
    return replace(LINE_STATIC_SPEC, sticker_padding=padding)


class Api:
    """Methods exposed to the HTML app via ``window.pywebview.api``."""

    def __init__(self, locale: str = "zh-Hant") -> None:
        self.locale = normalize_locale(locale)
        self._window = None

    # --- data (single source of truth for the UI) ---------------------------
    def bootstrap(self, locale: str | None = None) -> dict:
        loc = normalize_locale(locale or self.locale)
        return {
            "locale": loc,
            "defaults": DEFAULT_FIELDS[loc],
            "texts": DEFAULT_TEXTS[loc],
            "actions": DEFAULT_ACTIONS[loc],
            "suggestions": SUGGESTIONS[loc],
            "presets": PROMPT_PRESETS[loc],
            "spec": {
                "stickerW": LINE_STATIC_SPEC.sticker_size[0],
                "stickerH": LINE_STATIC_SPEC.sticker_size[1],
                "screenAnimationW": LINE_SCREEN_ANIM_SIZE[0],
                "screenAnimationH": LINE_SCREEN_ANIM_SIZE[1],
                "mainSize": LINE_STATIC_SPEC.main_size[0],
                "tabW": LINE_STATIC_SPEC.tab_size[0],
                "tabH": LINE_STATIC_SPEC.tab_size[1],
                "packSize": LINE_STATIC_SPEC.sticker_count,
                "padding": LINE_STATIC_SPEC.sticker_padding,
            },
            "chromaKeys": {
                name: {"label": key.label, "hex": key.hex} for name, key in CHROMA_KEYS.items()
            },
            # The advanced panel seeds its sliders from these, so the presets
            # stay defined only in `spec`.
            "tuneProfiles": {
                name: {
                    "hard": profile.hard,
                    "soft": profile.soft,
                    "minKey": profile.min_key,
                    "maxOther": profile.max_other,
                    "dominance": profile.dominance,
                    "mode": profile.mode,
                    "erode": profile.erode,
                }
                for name, profile in CHROMA_TUNE_PROFILES.items()
            },
        }

    # --- prompt -------------------------------------------------------------
    def render_prompt(self, payload: dict) -> str:
        return render_line_static_prompt(
            with_text=bool(payload.get("withText", True)),
            locale=payload.get("locale", self.locale),
            character=payload.get("character"),
            theme=payload.get("theme"),
            tone=payload.get("tone"),
            style=payload.get("style"),
            language=payload.get("language"),
            texts=payload.get("texts"),
            actions=payload.get("actions"),
            chroma_key=payload.get("chromaKey", "green"),
        )

    # --- image pipeline -----------------------------------------------------
    def split(self, image_data_url: str, options: dict) -> list[str]:
        options = options or {}
        image = _decode(image_data_url)
        key = resolve_chroma_key(options.get("keyName", "green"))
        spec = _spec_for(options)
        tiles = split_grid_to_stickers(image, spec=spec, background=(*key.rgb, 255))
        if options.get("cleanup", False):
            tiles = self._cleanup_tiles(tiles, options)
        return [_encode(tile) for tile in tiles]

    def cleanup(self, tile_data_urls: list[str], options: dict) -> list[str]:
        options = options or {}
        tiles = [_decode(url) for url in tile_data_urls]
        return [_encode(tile) for tile in self._cleanup_tiles(tiles, options)]

    def _cleanup_tiles(self, tiles: list[Image.Image], options: dict) -> list[Image.Image]:
        outline = options.get("outline", "none")
        return [
            apply_outline_and_shadow(
                remove_chroma_background(
                    tile,
                    key_name=options.get("keyName", "green"),
                    tune=_tune_option(options),
                ),
                outline,
            )
            for tile in tiles
        ]

    # --- export -------------------------------------------------------------
    def export_line(self, tile_data_urls: list[str], options: dict) -> dict:
        path = self._ask_save_path("line-stickers.zip")
        if not path:
            return {"cancelled": True}
        self._write_line_zip([_decode(url) for url in tile_data_urls], path, options or {})
        return {"saved": str(path)}

    def export_stickers(self, tile_data_urls: list[str], options: dict) -> dict:
        path = self._ask_save_path("transparent-stickers.zip")
        if not path:
            return {"cancelled": True}
        self._write_stickers_zip([_decode(url) for url in tile_data_urls], path, options or {})
        return {"saved": str(path)}

    def export_big(self, tile_data_urls: list[str], options: dict) -> dict:
        path = self._ask_save_path("line-big-stickers.zip")
        if not path:
            return {"cancelled": True}
        options = options or {}
        tiles = [_decode(url) for url in tile_data_urls]
        main_index = int(options.get("mainIndex", 0))
        tab_index = int(options.get("tabIndex", 0))
        if not 0 <= main_index < len(tiles):
            main_index = 0
        if not 0 <= tab_index < len(tiles):
            tab_index = 0
        try:
            export_big_zip(
                tiles,
                path,
                main_index=main_index,
                tab_index=tab_index,
                title=(options.get("title") or "").strip() or "sticker-forge big sticker pack",
                author=(options.get("author") or "").strip() or "sticker-forge",
            )
        except ValueError as exc:
            return {"error": str(exc)}
        return {"saved": str(path)}

    def export_platform(self, tile_data_urls: list[str], options: dict) -> dict:
        platform = (options or {}).get("platform", "telegram")
        if platform not in PLATFORM_SPECS:
            return {"error": f"unknown platform: {platform}"}
        path = self._ask_save_path(f"{platform}-stickers.zip")
        if not path:
            return {"cancelled": True}
        export_platform_zip(
            [_decode(url) for url in tile_data_urls],
            path,
            platform=platform,
            title=((options or {}).get("title") or "").strip() or "sticker-forge pack",
            author=((options or {}).get("author") or "").strip() or "sticker-forge",
        )
        return {"saved": str(path)}

    # --- animated stickers (one animated file per sticker) ------------------
    def prepare_animated(self, data_urls: list[str], options: dict) -> list[str]:
        """Load each animated file, clean per frame, resize, return APNG previews."""
        options = options or {}
        previews = []
        for url in data_urls:
            frames, durations = _decode_animated(url)
            if not options.get("keepBackground", False):
                frames = [
                    remove_chroma_background(
                        frame,
                        key_name=options.get("keyName", "green"),
                        tune=_tune_option(options),
                    )
                    for frame in frames
                ]
            fitted = _fit_frames_within(frames, LINE_ANIM_MAX_SIZE)
            previews.append(_encode_apng(fitted, [max(20, int(d)) for d in durations]))
        return previews

    def export_animated(self, apng_data_urls: list[str], options: dict) -> dict:
        options = options or {}
        path = self._ask_save_path("line-animated.zip")
        if not path:
            return {"cancelled": True}
        sticker_frames = []
        durations = []
        for url in apng_data_urls:
            frames, frame_durations = _decode_animated(url)
            sticker_frames.append(frames)
            durations.append(frame_durations)
        main_index = int(options.get("mainIndex", 0))
        tab_index = int(options.get("tabIndex", 0))
        if not 0 <= main_index < len(sticker_frames):
            main_index = 0
        if not 0 <= tab_index < len(sticker_frames):
            tab_index = 0
        try:
            export_animated_zip(
                sticker_frames,
                path,
                main_index=main_index,
                tab_index=tab_index,
                title=(options.get("title") or "").strip() or "sticker-forge animated",
                author=(options.get("author") or "").strip() or "sticker-forge",
                durations=durations,
            )
        except ValueError as exc:
            return {"error": str(exc)}
        return {"saved": str(path)}

    # --- pop-up / effect stickers (static stickers + screen APNGs) ----------
    def prepare_screen_animations(self, data_urls: list[str], options: dict) -> list[str]:
        """Load screen animation files, clean per frame, fit to 480x480 APNG previews."""
        options = options or {}
        previews = []
        for url in data_urls:
            frames, durations = _decode_animated(url)
            if not options.get("keepBackground", False):
                frames = [
                    remove_chroma_background(
                        frame,
                        key_name=options.get("keyName", "green"),
                        tune=_tune_option(options),
                    )
                    for frame in frames
                ]
            previews.append(_encode_screen_apng(_fit_screen_frames(frames), [max(20, int(d)) for d in durations]))
        return previews

    def export_popup(self, tile_data_urls: list[str], apng_data_urls: list[str], options: dict) -> dict:
        options = options or {}
        path = self._ask_save_path("line-popup-stickers.zip")
        if not path:
            return {"cancelled": True}
        return self._write_screen_zip("popup", tile_data_urls, apng_data_urls, path, options)

    def export_effect(self, tile_data_urls: list[str], apng_data_urls: list[str], options: dict) -> dict:
        options = options or {}
        path = self._ask_save_path("line-effect-stickers.zip")
        if not path:
            return {"cancelled": True}
        return self._write_screen_zip("effect", tile_data_urls, apng_data_urls, path, options)

    def _write_screen_zip(
        self,
        kind: str,
        tile_data_urls: list[str],
        apng_data_urls: list[str],
        path: str | Path,
        options: dict,
    ) -> dict:
        tiles = [_decode(url) for url in tile_data_urls]
        sticker_frames = []
        durations = []
        for url in apng_data_urls:
            frames, frame_durations = _decode_animated(url)
            sticker_frames.append(frames)
            durations.append(frame_durations)
        main_index = int(options.get("mainIndex", 0))
        tab_index = int(options.get("tabIndex", 0))
        if not 0 <= main_index < len(tiles):
            main_index = 0
        if not 0 <= tab_index < len(tiles):
            tab_index = 0
        title = (options.get("title") or "").strip()
        author = (options.get("author") or "").strip() or "sticker-forge"
        try:
            if kind == "popup":
                export_popup_zip(
                    tiles,
                    sticker_frames,
                    path,
                    main_index=main_index,
                    tab_index=tab_index,
                    title=title or "sticker-forge pop-up",
                    author=author,
                    durations=durations,
                )
            elif kind == "effect":
                export_effect_zip(
                    tiles,
                    sticker_frames,
                    path,
                    main_index=main_index,
                    tab_index=tab_index,
                    title=title or "sticker-forge effect",
                    author=author,
                    durations=durations,
                )
            else:
                return {"error": f"unknown screen sticker type: {kind}"}
        except ValueError as exc:
            return {"error": str(exc)}
        return {"saved": str(path)}

    def export_message(self, tile_data_urls: list[str], options: dict) -> dict:
        options = options or {}
        path = self._ask_save_path("line-message-stickers.zip")
        if not path:
            return {"cancelled": True}
        tiles = [_decode(url) for url in tile_data_urls]
        main_index = int(options.get("mainIndex", 0))
        tab_index = int(options.get("tabIndex", 0))
        if not 0 <= main_index < len(tiles):
            main_index = 0
        if not 0 <= tab_index < len(tiles):
            tab_index = 0
        try:
            export_message_zip(
                tiles,
                path,
                main_index=main_index,
                tab_index=tab_index,
                title=(options.get("title") or "").strip() or "sticker-forge message pack",
                author=(options.get("author") or "").strip() or "sticker-forge",
            )
        except ValueError as exc:
            return {"error": str(exc)}
        return {"saved": str(path)}

    def export_emoji(self, tile_data_urls: list[str], options: dict) -> dict:
        options = options or {}
        path = self._ask_save_path("line-emoji.zip")
        if not path:
            return {"cancelled": True}
        tiles = [_decode(url) for url in tile_data_urls]
        thumb = int(options.get("thumbIndex", 0))
        if not 0 <= thumb < len(tiles):
            thumb = 0
        try:
            export_emoji_zip(
                tiles,
                path,
                thumb_index=thumb,
                title=(options.get("title") or "").strip() or "sticker-forge emoji",
                author=(options.get("author") or "").strip() or "sticker-forge",
            )
        except ValueError as exc:
            return {"error": str(exc)}
        return {"saved": str(path)}

    def save_png(self, data_url: str, default_name: str = "sticker.png") -> dict:
        path = self._ask_save_path(default_name, ("PNG (*.png)",))
        if not path:
            return {"cancelled": True}
        _decode(data_url).save(path)
        return {"saved": str(path)}

    # Split from the dialog-less write helpers so tests can drive them directly.
    def _write_line_zip(self, tiles: list[Image.Image], path: str | Path, options: dict) -> Path:
        count = len(tiles)
        main_index = int(options.get("mainIndex", 0))
        tab_index = int(options.get("tabIndex", 0))
        if not 0 <= main_index < count:
            main_index = 0
        if not 0 <= tab_index < count:
            tab_index = 0
        title = (options.get("title") or "").strip() or "sticker-forge pack"
        author = (options.get("author") or "").strip() or "sticker-forge"
        return export_line_zip(
            tiles,
            path,
            title=title,
            author=author,
            spec=_spec_for(options),
            main_index=main_index,
            tab_index=tab_index,
        )

    def _write_stickers_zip(self, tiles: list[Image.Image], path: str | Path, options: dict) -> Path:
        return export_stickers_zip(tiles, path, spec=_spec_for(options))

    def _ask_save_path(self, default_name: str, file_types: tuple[str, ...] = ("ZIP (*.zip)",)):
        if self._window is None:
            return None
        import webview

        result = self._window.create_file_dialog(
            webview.SAVE_DIALOG, save_filename=default_name, file_types=file_types
        )
        if not result:
            return None
        return result if isinstance(result, str) else result[0]


def run(locale: str = "zh-Hant") -> int:
    import webview

    api = Api(locale)
    window = webview.create_window(
        "sticker-forge",
        url=str(app_path()),
        js_api=api,
        width=1180,
        height=820,
        min_size=(960, 640),
    )
    api._window = window
    # private_mode keeps the WebView2 profile ephemeral (a temp folder cleared on
    # exit), so the app writes no persistent user data — consistent with the
    # local-first "no hidden data" stance. The trade-off is that the UI language
    # preference is not remembered across launches.
    webview.start(private_mode=True)
    return 0
