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
