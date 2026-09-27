#!/usr/bin/env python3
"""Classify Dependabot pull requests for guarded automatic merging."""

from __future__ import annotations

import argparse
import json
import os
import re
from collections.abc import Iterable
from pathlib import Path

AUTO_MERGE_LABEL = "dependencies-auto-merge"
MANUAL_REVIEW_LABEL = "dependencies-manual-review"

SAFE_UPDATE_TYPES = {
    "version-update:semver-patch",
    "version-update:semver-minor",
}
DIRECT_DEPENDENCY_TYPES = {
    "direct:development",
    "direct:production",
}
CI_EXERCISED_PIP_PACKAGES = {
    "packaging",
    "pytest",
    "setuptools",
    "wheel",
}


def _normalize_package_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _manual(reason: str) -> dict[str, str]:
    return {
        "decision": "manual",
        "label": MANUAL_REVIEW_LABEL,
        "reason": reason,
    }


def classify_update(
    ecosystem: str,
    dependency_type: str,
    update_type: str,
    changed_files: Iterable[str],
    dependency_names: Iterable[str],
) -> dict[str, str]:
    """Return an auto-merge or manual-review policy decision."""
    files = {Path(path).as_posix() for path in changed_files if path}
    names = {
        _normalize_package_name(name)
        for name in dependency_names
        if name and name.strip()
    }

    if not files:
        return _manual("沒有可驗證的變更檔案，保留人工審查。")
    if update_type not in SAFE_UPDATE_TYPES:
        return _manual("只有 minor／patch 更新可自動處理。")
    if not names:
        return _manual("沒有可驗證的依賴名稱，保留人工審查。")

    if ecosystem == "pip":
        if files != {"pyproject.toml"}:
            return _manual("Python 依賴 PR 超出 pyproject.toml 範圍。")
        if dependency_type not in DIRECT_DEPENDENCY_TYPES:
            return _manual("不是可自動處理的直接 Python 依賴。")
        if not names.issubset(CI_EXERCISED_PIP_PACKAGES):
            return _manual(
                "包含圖片執行期、GUI、打包或未列入政策的 Python 依賴。"
            )
        return {
            "decision": "auto_merge",
            "label": AUTO_MERGE_LABEL,
            "reason": (
                "CI 直接執行或安裝這批維護工具，更新僅限 minor／patch "
                "且只修改 pyproject.toml。"
            ),
        }

    if ecosystem == "github-actions":
        if dependency_type not in DIRECT_DEPENDENCY_TYPES:
            return _manual("不是可自動處理的直接 GitHub Actions 依賴。")
        workflow_only = all(
            path.startswith(".github/workflows/")
            and Path(path).suffix.lower() in {".yml", ".yaml"}
            for path in files
        )
        if not workflow_only:
            return _manual("GitHub Actions PR 超出 workflow 檔案範圍。")
        return {
            "decision": "auto_merge",
            "label": AUTO_MERGE_LABEL,
            "reason": (
                "GitHub Actions minor／patch 更新只修改 workflow，"
                "且更新後的 workflow 必須通過完整 CI。"
            ),
        }

    return _manual("未列入自動核准政策的套件生態系。")


def write_github_output(result: dict[str, str]) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as output:
        for key in ("decision", "label", "reason"):
            output.write(f"{key}={result[key]}\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Classify a Dependabot pull request for guarded merging"
    )
    parser.add_argument("--ecosystem", required=True)
    parser.add_argument("--dependency-type", required=True)
    parser.add_argument("--update-type", required=True)
    parser.add_argument("--dependency-names", required=True)
    parser.add_argument("--changed-file", action="append", default=[])
    parser.add_argument("--github-output", action="store_true")
    args = parser.parse_args()

    result = classify_update(
        ecosystem=args.ecosystem,
        dependency_type=args.dependency_type,
        update_type=args.update_type,
        changed_files=args.changed_file,
        dependency_names=[
            name.strip() for name in args.dependency_names.split(",")
        ],
    )
    print(json.dumps(result, ensure_ascii=False))
    if args.github_output:
        write_github_output(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
