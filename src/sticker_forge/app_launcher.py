from __future__ import annotations

from pathlib import Path
import sys


def app_path() -> Path:
    """Locate the bundled HTML workspace (used by the pywebview desktop GUI)."""
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        return Path(bundle_root) / "app" / "index.html"
    return Path(__file__).resolve().parents[2] / "app" / "index.html"
