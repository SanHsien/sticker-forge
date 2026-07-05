from __future__ import annotations

from pathlib import Path
import sys

from .spec import resolve_chroma_key


SUPPORTED_LOCALES = ("zh-Hant", "en")

DEFAULT_FIELDS = {
    "zh-Hant": {
        "character": "原創可愛角色",
        "theme": "日常聊天貼圖",
        "tone": "可愛、清楚、友善",
        "style": "粗黑線、扁平上色、適合聊天視窗縮圖閱讀",
        "language": "繁體中文",
    },
    "en": {
        "character": "an original cute character",
        "theme": "everyday chat stickers",
        "tone": "cute, clear, friendly",
        "style": "bold black outlines, flat colors, readable at chat thumbnail size",
        "language": "English",
    },
}

DEFAULT_TEXTS = {
    "zh-Hant": ["早安", "謝謝", "收到", "加油", "辛苦了", "太棒了", "等一下", "晚安"],
    "en": ["Good morning", "Thanks", "Got it", "You can do it", "Nice work", "Great", "Wait a sec", "Good night"],
}

DEFAULT_ACTIONS = {
    "zh-Hant": [
        "開心揮手",
        "雙手比心",
        "點頭確認",
        "握拳打氣",
        "擦汗微笑",
        "跳起來歡呼",
        "舉手示意暫停",
        "抱著枕頭打呵欠",
    ],
    "en": [
        "happily waving",
        "making a heart with both hands",
        "nodding in confirmation",
        "cheering with a clenched fist",
        "smiling while wiping sweat",
        "jumping in celebration",
        "raising one hand to pause",
        "yawning while hugging a pillow",
    ],
}


def normalize_locale(locale: str | None) -> str:
    if locale in SUPPORTED_LOCALES:
        return str(locale)
    return "zh-Hant"


def template_path(locale: str | None = None) -> Path:
    locale = normalize_locale(locale)
    filename = "line-static-3x3.en.md" if locale == "en" else "line-static-3x3.md"
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        return Path(bundle_root) / "prompts" / filename
    return Path(__file__).resolve().parents[2] / "prompts" / filename


def load_template(locale: str | None = None) -> str:
    return template_path(locale).read_text(encoding="utf-8")


def render_line_static_prompt(
    *,
    with_text: bool = True,
    locale: str | None = "zh-Hant",
    character: str | None = None,
    theme: str | None = None,
    tone: str | None = None,
    style: str | None = None,
    language: str | None = None,
    texts: list[str] | None = None,
    actions: list[str] | None = None,
    chroma_key: str = "green",
) -> str:
    locale = normalize_locale(locale)
    defaults = DEFAULT_FIELDS[locale]
    values = {
        "character": character or defaults["character"],
        "theme": theme or defaults["theme"],
        "tone": tone or defaults["tone"],
        "style": style or defaults["style"],
        "language": language or defaults["language"],
    }
    key = resolve_chroma_key(chroma_key)
    values.update(
        {
            "chroma_key_label": key.label,
            "chroma_key_hex": key.hex,
            "chroma_key_avoid": key.avoid,
            "chroma_key_substitutions": key.substitutions,
        }
    )

    resolved_texts = (texts or DEFAULT_TEXTS[locale])[:8]
    resolved_actions = (actions or DEFAULT_ACTIONS[locale])[:8]
    if len(resolved_texts) != 8:
        raise ValueError("texts must contain exactly 8 entries")
    if len(resolved_actions) != 8:
        raise ValueError("actions must contain exactly 8 entries")

    for index, text in enumerate(resolved_texts, start=1):
        values[f"text_{index}"] = text
    for index, action in enumerate(resolved_actions, start=1):
        values[f"action_{index}"] = action

    template = _selected_section(load_template(locale), with_text=with_text, locale=locale)
    return template.format(**values).strip() + "\n"


def _selected_section(template: str, *, with_text: bool, locale: str) -> str:
    if locale == "en":
        marker = "## Text version" if with_text else "## No-text version"
        next_marker = "## No-text version" if with_text else "## "
    else:
        marker = "## 有字版" if with_text else "## 無字版"
        next_marker = "## 無字版" if with_text else "## "
    start = template.index(marker)
    if with_text:
        end = template.index(next_marker, start + len(marker))
        return template[start:end]
    return template[start:]
