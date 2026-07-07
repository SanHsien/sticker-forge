from __future__ import annotations

import pytest

from sticker_forge.gui import main
from sticker_forge.prompts import SUGGESTIONS


def test_gui_smoke_mode_does_not_open_window() -> None:
    assert main(["--smoke"]) == 0


def _make_app():
    tk = pytest.importorskip("tkinter")
    from sticker_forge.gui import StickerForgeApp

    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("no display available for tkinter")
    root.withdraw()
    return root, StickerForgeApp(root, locale="zh-Hant")


def test_gui_prompt_fields_offer_editable_suggestions() -> None:
    root, app = _make_app()
    try:
        # Prompt fields and text/action slots are editable comboboxes with suggestions.
        assert list(app.field_combos["character"]["values"]) == SUGGESTIONS["zh-Hant"]["character"]
        assert len(app.text_combos) == 8 and len(app.action_combos) == 8
        assert list(app.text_combos[0]["values"]) == SUGGESTIONS["zh-Hant"]["texts"]
        assert str(app.field_combos["character"].cget("state")) == "normal"  # editable, not readonly

        # Free text still flows into the prompt.
        app.fields["character"].set("會飛的墨水魚")
        app.render_prompt()
        assert "會飛的墨水魚" in app.prompt_text.get("1.0", "end")

        # Switching locale refreshes the suggestion lists.
        app.change_locale("en")
        assert list(app.field_combos["character"]["values"]) == SUGGESTIONS["en"]["character"]
        assert list(app.action_combos[0]["values"]) == SUGGESTIONS["en"]["actions"]
    finally:
        root.destroy()
