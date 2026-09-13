"""Minimum contracts for dependency maintenance automation."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_dependabot_separates_guarded_and_manual_dependencies() -> None:
    content = (ROOT / ".github" / "dependabot.yml").read_text(
        encoding="utf-8"
    )

    assert 'package-ecosystem: "pip"' in content
    assert 'package-ecosystem: "github-actions"' in content
    assert 'timezone: "Asia/Taipei"' in content
    assert "ci-tooling-minor-and-patch:" in content
    assert "runtime-gui-and-packaging-minor-and-patch:" in content
    assert "major-updates:" in content


def test_review_uses_trusted_base_and_head_bound_policy_check() -> None:
    content = (
        ROOT / ".github" / "workflows" / "dependabot-review.yml"
    ).read_text(encoding="utf-8")

    assert "pull_request_target:" in content
    assert "github.event.pull_request.base.sha" in content
    assert "persist-credentials: false" in content
    assert "tools/classify_dependabot_update.py" in content
    assert "github.event.pull_request.head.sha" in content
    assert "Dependabot policy" in content
    assert "issues: write" not in content
    assert "gh label create" not in content


def test_merge_revalidates_identity_head_and_required_ci() -> None:
    content = (
        ROOT / ".github" / "workflows" / "dependabot-merge.yml"
    ).read_text(encoding="utf-8")

    assert 'workflows: ["CI"]' in content
    assert "--author app/dependabot" in content
    assert 'base" != "main"' in content
    assert "dependabot-merge-queue" in content
    assert "@dependabot rebase" in content
    assert "Dependabot policy" in content
    for check in (
        "Python 3.11",
        "Python 3.12",
        "Python 3.13",
        "Python 3.14",
        "Windows EXE",
    ):
        assert f'"{check}"' in content
    assert "--match-head-commit" in content
    assert "--squash" in content
    assert "issues: write" not in content
    assert "gh label create" not in content


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
