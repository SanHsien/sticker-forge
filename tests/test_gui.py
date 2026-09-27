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
