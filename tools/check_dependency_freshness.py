#!/usr/bin/env python3
"""Check declared direct dependencies against the latest PyPI releases."""

from __future__ import annotations

import argparse
import json
import os
import re
import tomllib
import urllib.parse
import urllib.request
from collections.abc import Iterable
from pathlib import Path

from packaging.version import InvalidVersion, Version

ROOT = Path(__file__).resolve().parent.parent

_REQUIREMENT_RE = re.compile(r"^\s*([A-Za-z0-9_.-]+)(?:\[[^\]]+\])?\s*(.*)$")
_MINIMUM_RE = re.compile(
    r"(>=|>|==|~=)\s*([0-9][0-9A-Za-z.!+_-]*(?:\.[0-9A-Za-z!+_-]+)*)"
)


def normalize_package_name(package_name: str) -> str:
    return re.sub(r"[-_.]+", "-", package_name).lower()


def is_newer_version(latest: str, current: str) -> bool:
    try:
        return Version(latest) > Version(current)
    except InvalidVersion:
        return False


def _parse_requirements(
    requirements: Iterable[str],
    group: str,
) -> list[dict[str, str]]:
    packages = []
    for requirement in requirements:
        match = _REQUIREMENT_RE.match(requirement)
        if not match:
            continue
        name, specifiers = match.groups()
        minimum_match = _MINIMUM_RE.search(specifiers)
        packages.append(
            {
                "name": name,
                "minimum": minimum_match.group(2) if minimum_match else "",
                "requirement": requirement,
                "group": group,
            }
        )
    return packages


def load_direct_dependencies(
    pyproject_path: Path = ROOT / "pyproject.toml",
) -> list[dict[str, str]]:
    with pyproject_path.open("rb") as file:
        data = tomllib.load(file)

    project = data.get("project", {})
    packages = _parse_requirements(project.get("dependencies", []), "runtime")
    for group, requirements in project.get("optional-dependencies", {}).items():
        packages.extend(_parse_requirements(requirements, f"optional:{group}"))
    packages.extend(
        _parse_requirements(
            data.get("build-system", {}).get("requires", []),
            "build-system",
        )
    )
    return packages


def fetch_pypi_version(package_name: str, timeout: float = 10.0) -> str | None:
    quoted_name = urllib.parse.quote(package_name, safe="")
    request = urllib.request.Request(
        f"https://pypi.org/pypi/{quoted_name}/json",
        headers={
            "Accept": "application/json",
            "User-Agent": "sticker-forge-dependency-check",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # nosec B310
            data = json.loads(response.read().decode("utf-8"))
        return data.get("info", {}).get("version")
    except (OSError, ValueError):
        return None


def collect_status(
    packages: Iterable[dict[str, str]],
) -> list[dict[str, object]]:
    rows = []
    for package in packages:
        minimum = package["minimum"]
        latest = fetch_pypi_version(package["name"])
        check_failed = not minimum or latest is None
        outdated = bool(
            minimum and latest and is_newer_version(str(latest), minimum)
        )
        rows.append(
            {
                **package,
                "latest": latest or "unknown",
                "outdated": outdated,
                "check_failed": check_failed,
            }
        )
    return rows


def render_markdown(rows: list[dict[str, object]]) -> str:
    lines = [
        "# sticker-forge dependency freshness",
        "",
        "| Package | Group | Declared | PyPI latest | Status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        if row["check_failed"]:
            status = "CHECK FAILED"
        elif row["outdated"]:
            status = "REVIEW UPDATE"
        else:
            status = "OK"
        lines.append(
            f"| `{row['name']}` | `{row['group']}` | "
            f"`{row['requirement']}` | `{row['latest']}` | {status} |"
        )
    lines.extend(
        [
            "",
            "This report compares repository declarations with PyPI. "
            "It does not inspect installed packages.",
            "A newer version requires review; dependency pull requests are never "
            "merged automatically.",
            "",
            "## Review policy",
            "",
            "1. Review the package changelog and supported Python/Windows versions.",
            "2. Run all Python test jobs and the Windows EXE build/smoke job.",
            "3. For Pillow, pywebview, or PyInstaller changes, complete the relevant "
            "desktop validation before release.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_github_output(
    outdated: bool,
    check_failed: bool,
    report_path: Path,
) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as output:
        output.write(f"outdated={'true' if outdated else 'false'}\n")
        output.write(f"check_failed={'true' if check_failed else 'false'}\n")
        output.write(
            f"needs_attention={'true' if outdated or check_failed else 'false'}\n"
        )
        output.write(f"report_path={report_path.as_posix()}\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check sticker-forge direct dependencies against PyPI"
    )
    parser.add_argument(
        "--output",
        default="dependency-freshness-report.md",
        help="Markdown report output path",
    )
    parser.add_argument(
        "--github-output",
        action="store_true",
        help="Write status fields to GITHUB_OUTPUT",
    )
    args = parser.parse_args()

    rows = collect_status(load_direct_dependencies())
    report = render_markdown(rows)
    output_path = Path(args.output)
    output_path.write_text(report, encoding="utf-8")
    print(report)

    outdated = any(bool(row["outdated"]) for row in rows)
    check_failed = not rows or any(bool(row["check_failed"]) for row in rows)
    if args.github_output:
        write_github_output(outdated, check_failed, output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
