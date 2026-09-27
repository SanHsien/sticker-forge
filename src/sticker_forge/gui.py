from __future__ import annotations

import argparse

from . import webapi
from .prompts import normalize_locale


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--lang", choices=["zh-Hant", "en"], default="zh-Hant")
    parser.add_argument("--smoke", action="store_true")
    args, _ = parser.parse_known_args(argv)
    if args.smoke:
        return 0
    return webapi.run(locale=normalize_locale(args.lang))


if __name__ == "__main__":
    raise SystemExit(main())
