from __future__ import annotations

from sticker_forge.app_launcher import app_path


def test_app_path_points_to_local_html() -> None:
    path = app_path()

    assert path.name == "index.html"
    assert path.exists()
