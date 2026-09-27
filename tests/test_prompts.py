from __future__ import annotations

from sticker_forge.prompts import PROMPT_PRESETS, render_line_static_prompt


def test_prompt_presets_are_well_formed() -> None:
    for locale in ("zh-Hant", "en"):
        assert PROMPT_PRESETS[locale], f"no presets for {locale}"
        for key, preset in PROMPT_PRESETS[locale].items():
            assert preset["label"], key
            for field in ("character", "theme", "tone", "style", "language"):
                assert preset[field], f"{key}.{field}"
            assert len(preset["texts"]) == 8, key
            assert len(preset["actions"]) == 8, key
    # both locales expose the same preset keys
    assert set(PROMPT_PRESETS["zh-Hant"]) == set(PROMPT_PRESETS["en"])


def test_render_line_static_prompt_fills_text_version() -> None:
    prompt = render_line_static_prompt(
        character="原創柴犬",
        texts=[f"文字{i}" for i in range(1, 9)],
        actions=[f"動作{i}" for i in range(1, 9)],
        chroma_key="magenta",
    )

    assert "原創柴犬" in prompt
    assert "文字8" in prompt
    assert "#FF00FF" in prompt
    assert "{character}" not in prompt
    assert "## 無字版" not in prompt


def test_render_line_static_prompt_fills_no_text_version() -> None:
    prompt = render_line_static_prompt(
        with_text=False,
        actions=[f"動作{i}" for i in range(1, 9)],
    )

    assert "## 無字版" in prompt
    assert "不要在圖片中加入任何文字" in prompt
    assert "{action_1}" not in prompt
