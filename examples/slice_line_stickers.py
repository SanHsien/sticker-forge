#!/usr/bin/env python3
"""16 宮格工具的相容入口，實作位於 sticker_forge.grid_tool。"""
import json
from pathlib import Path
import sys

# 支援尚未 editable install 的原始碼工作目錄。
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def main(argv: list[str] | None = None) -> int:
    try:
        from sticker_forge.grid_tool import main as run
    except ModuleNotFoundError as exc:
        if exc.name != "PIL":
            raise
        for stream in (sys.stdout, sys.stderr):
            if hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding="utf-8", errors="replace")
        message = "錯誤：缺少必要第三方套件 'Pillow' (PIL)。請執行 'pip install Pillow' 安裝依賴。"
        if "--json" in (sys.argv[1:] if argv is None else argv):
            print(json.dumps({"error": message, "code": "MISSING_PILLOW"}, ensure_ascii=False))
        else:
            print(message, file=sys.stderr)
        return 2
    return run(argv)


if __name__ == "__main__":
    raise SystemExit(main())
