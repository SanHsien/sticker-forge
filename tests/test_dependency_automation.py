"""Minimum contracts for dependency maintenance automation."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_dependabot_tracks_python_and_actions_without_auto_merge() -> None:
    content = (ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8")

    assert 'package-ecosystem: "pip"' in content
    assert 'package-ecosystem: "github-actions"' in content
    assert 'timezone: "Asia/Taipei"' in content
    assert "auto-merge" not in content


def test_ci_covers_supported_python_and_windows_package() -> None:
    content = (
        ROOT / ".github" / "workflows" / "ci.yml"
    ).read_text(encoding="utf-8")

    for version in ("3.11", "3.12", "3.13", "3.14"):
        assert f'"{version}"' in content
    assert "./packaging/build-windows.ps1" in content
    assert "node --check app/app.js" in content
    assert "contents: read" in content
    assert "contents: write" not in content


def test_freshness_schedule_is_read_only_and_fails_for_attention() -> None:
    content = (
        ROOT / ".github" / "workflows" / "dependency-freshness.yml"
    ).read_text(encoding="utf-8")

    assert "schedule:" in content
    assert "workflow_dispatch:" in content
    assert "tools/check_dependency_freshness.py" in content
    assert "--author app/dependabot" in content
    assert "pull-requests: read" in content
    assert "contents: read" in content
    assert "issues: write" not in content
    assert "contents: write" not in content
    assert "exit 1" in content
