from __future__ import annotations

from pathlib import Path
import sys

from .spec import resolve_chroma_key


DEFAULT_TEXTS = [
    "早安",
    "謝謝",
    "收到",
    "加油",
    "辛苦了",
    "太棒了",
    "等一下",
    "晚安",
]

DEFAULT_ACTIONS = [
    "開心揮手",
    "雙手比心",
    "點頭確認",
    "握拳打氣",
    "擦汗微笑",
    "跳起來歡呼",
    "舉手示意暫停",
    "抱著枕頭打呵欠",
]


def template_path() -> Path:
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        return Path(bundle_root) / "prompts" / "line-static-3x3.md"
    return Path(__file__).resolve().parents[2] / "prompts" / "line-static-3x3.md"


def load_template() -> str:
    return template_path().read_text(encoding="utf-8")


def render_line_static_prompt(
    *,
    with_text: bool = True,
    character: str = "原創可愛角色",
    theme: str = "日常聊天貼圖",
    tone: str = "可愛、清楚、友善",
    style: str = "粗黑線、扁平上色、適合聊天視窗縮圖閱讀",
    language: str = "繁體中文",
    texts: list[str] | None = None,
    actions: list[str] | None = None,
    chroma_key: str = "green",
) -> str:
    values = {
        "character": character,
        "theme": theme,
        "tone": tone,
        "style": style,
        "language": language,
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

    resolved_texts = (texts or DEFAULT_TEXTS)[:8]
    resolved_actions = (actions or DEFAULT_ACTIONS)[:8]
    if len(resolved_texts) != 8:
        raise ValueError("texts must contain exactly 8 entries")
    if len(resolved_actions) != 8:
        raise ValueError("actions must contain exactly 8 entries")

    for index, text in enumerate(resolved_texts, start=1):
        values[f"text_{index}"] = text
    for index, action in enumerate(resolved_actions, start=1):
        values[f"action_{index}"] = action

    template = _selected_section(load_template(), with_text=with_text)
    return template.format(**values).strip() + "\n"


def _selected_section(template: str, *, with_text: bool) -> str:
    marker = "## 有字版" if with_text else "## 無字版"
    next_marker = "## 無字版" if with_text else "## "
    start = template.index(marker)
    if with_text:
        end = template.index(next_marker, start + len(marker))
        return template[start:end]
    return template[start:]
