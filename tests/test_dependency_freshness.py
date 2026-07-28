"""Dependency freshness parser, comparison, and report tests."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from tools import check_dependency_freshness as freshness


def test_loads_runtime_optional_and_build_dependencies(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[project]
dependencies = ["Pillow>=10.0"]

[project.optional-dependencies]
gui = ["pywebview>=5.0"]
packaging = ["pyinstaller>=6.0"]

[build-system]
requires = ["setuptools>=69", "wheel"]
build-backend = "setuptools.build_meta"
""".strip(),
        encoding="utf-8",
    )

    packages = freshness.load_direct_dependencies(pyproject)
    by_name = {
        freshness.normalize_package_name(row["name"]): row for row in packages
    }

    assert by_name["pillow"]["minimum"] == "10.0"
    assert by_name["pillow"]["group"] == "runtime"
    assert by_name["pywebview"]["group"] == "optional:gui"
    assert by_name["pyinstaller"]["group"] == "optional:packaging"
    assert by_name["setuptools"]["group"] == "build-system"
    assert by_name["wheel"]["minimum"] == ""


def test_version_comparison_follows_pep_440() -> None:
    assert not freshness.is_newer_version("1.14", "1.14.0")
    assert freshness.is_newer_version("1.14.1", "1.14")
    assert freshness.is_newer_version("6.10.1", "6.6")
    assert freshness.is_newer_version("1.0", "1.0rc1")
    assert not freshness.is_newer_version("2.0", "1!1.0")


def test_status_and_report_mark_updates_and_failures() -> None:
    packages = [
        {
            "name": "Pillow",
            "minimum": "10.0",
            "requirement": "Pillow>=10.0",
            "group": "runtime",
        },
        {
            "name": "wheel",
            "minimum": "",
            "requirement": "wheel",
            "group": "build-system",
        },
    ]
    with patch.object(
        freshness,
        "fetch_pypi_version",
        side_effect=lambda name, timeout=10.0: {
            "Pillow": "11.3.0",
            "wheel": "0.46.1",
        }[name],
    ):
        rows = freshness.collect_status(packages)

    assert rows[0]["outdated"] is True
    assert rows[0]["check_failed"] is False
    assert rows[1]["check_failed"] is True

    report = freshness.render_markdown(rows)
    assert "REVIEW UPDATE" in report
    assert "CHECK FAILED" in report
    assert "never merged automatically" in report
