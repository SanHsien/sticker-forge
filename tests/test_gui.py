from __future__ import annotations

from sticker_forge.gui import main


def test_gui_smoke_mode_does_not_open_window() -> None:
    assert main(["--smoke"]) == 0
