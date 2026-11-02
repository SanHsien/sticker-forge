from __future__ import annotations

from pathlib import Path

from sticker_forge.gui import main


def test_gui_smoke_mode_does_not_open_window() -> None:
    assert main(["--smoke"]) == 0


def test_app_uses_bridge_locale_for_initial_ui_language() -> None:
    app_js = (Path(__file__).parents[1] / "app" / "app.js").read_text(encoding="utf-8")

    assert "const initial = await bridge.bootstrap();" in app_js
    assert 'state.locale = UI[initial.locale] ? initial.locale : "zh-Hant";' in app_js
    assert 'localStorage.getItem("stickerForgeLocale")' not in app_js


def test_advanced_tune_panel_is_wired_and_off_by_default() -> None:
    app_js = (Path(__file__).parents[1] / "app" / "app.js").read_text(encoding="utf-8")
    index_html = (
        Path(__file__).parents[1] / "app" / "index.html"
    ).read_text(encoding="utf-8")

    # Collapsed by default so casual users never meet the knobs.
    assert '<details class="advanced-tune">' in index_html
    assert 'id="adv-enabled" type="checkbox">' in index_html
    for field in ("adv-hard", "adv-soft", "adv-minkey", "adv-maxother", "adv-dominance", "adv-erode"):
        assert f'id="{field}"' in index_html

    # Custom values only apply when explicitly enabled.
    assert "function tuneValue()" in app_js
    assert 'return advEnabled() ? advProfile() : $("cleanup-tune").value;' in app_js
    # Presets come from the Python core, not a duplicated JS table.
    assert "state.tuneProfiles = initial.tuneProfiles || {};" in app_js
    # soft above hard would invert the alpha ramp.
    assert "if (profile.soft > profile.hard)" in app_js


def test_incomplete_custom_chroma_clears_stale_prompt() -> None:
    app_js = (Path(__file__).parents[1] / "app" / "app.js").read_text(encoding="utf-8")

    render = app_js[app_js.index("async function renderPrompt("):]
    render = render[: render.index("\n}\n")]
    guard = render[render.index('if ($("chroma-key").value === "custom" && !/^#[0-9a-f]{6}$/i.test(chromaKeyValue())) {'):]
    guard = guard[: guard.index("    return;\n  }")]

    # Still typing: the panel is emptied without nagging about the half-typed value.
    assert '} else {\n      $("prompt-output").value = "";' in guard
    assert "if (!text) return;" in app_js


def test_rejected_custom_chroma_never_leaves_a_copyable_prompt() -> None:
    app_js = (Path(__file__).parents[1] / "app" / "app.js").read_text(encoding="utf-8")
    show = app_js[app_js.index("function showPromptError("):]
    show = show[: show.index("\n}\n")]
    render = app_js[app_js.index("async function renderPrompt("):]
    render = render[: render.index("\n}\n")]

    # Every rejection path (backend error, full-length bad value) goes through the
    # helper, and the helper empties the prompt before showing the reason.
    assert '$("prompt-output").value = "";' in show
    assert "showPromptError(String(err));" in render
    assert "showPromptError(ui().customKeyInvalid);" in render
    assert "setStatus(String(err), true);" not in render
    # Both locales explain the format instead of leaving the panel silently empty.
    assert app_js.count("customKeyInvalid:") == 2


def test_prompt_error_is_cleared_by_the_next_good_render_only() -> None:
    app_js = (Path(__file__).parents[1] / "app" / "app.js").read_text(encoding="utf-8")
    render = app_js[app_js.index("async function renderPrompt("):]
    render = render[: render.index("\n}\n")]
    clear = app_js[app_js.index("function clearPromptError("):]
    clear = clear[: clear.index("\n}\n")]

    assert "clearPromptError();" in render
    # Restores only when the status still shows our error, so a status written by
    # another action in between is not overwritten.
    assert "if (status.textContent === promptError.text)" in clear
    # A status written between two errors is what gets restored, not an older one.
    show = app_js[app_js.index("function showPromptError("):]
    show = show[: show.index("\n}\n")]
    assert "if (!promptError || status.textContent !== promptError.text) {" in show
    # An older async render cannot overwrite the panel after a newer input.
    assert render.count("if (seq !== renderSeq) return;") == 2


def test_custom_chroma_hint_appears_once_the_value_cannot_become_a_colour() -> None:
    import re

    app_js = (Path(__file__).parents[1] / "app" / "app.js").read_text(encoding="utf-8")
    still_typing = re.compile(r"^(#[0-9a-f]{0,5})?$", re.IGNORECASE)

    # The JS uses this exact pattern; check what it means on concrete inputs.
    assert "if (!/^(#[0-9a-f]{0,5})?$/i.test(chromaKeyValue())) {" in app_js
    for value in ["", "#", "#FF8", "#ff80"]:
        assert still_typing.match(value), value
    for value in ["FF8000", "#-1FF00", "#GG", "#FF80000", " #FF"]:
        assert not still_typing.match(value), value
