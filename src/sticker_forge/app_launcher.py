from __future__ import annotations

from pathlib import Path
import sys
import webbrowser


def app_path() -> Path:
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        return Path(bundle_root) / "app" / "index.html"
    return Path(__file__).resolve().parents[2] / "app" / "index.html"


def open_local_app() -> Path:
    path = app_path()
    webbrowser.open(path.resolve().as_uri())
    return path
