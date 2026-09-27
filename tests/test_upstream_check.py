from __future__ import annotations

import json
from pathlib import Path

import pytest

import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "tools"))

import check_upstream_commits as checker  # noqa: E402


def test_baseline_file_is_valid_and_complete() -> None:
    baseline = checker.load_baseline()

    assert baseline["repo"].endswith("line-sticker-studio.git")
    assert baseline["branch"] == "main"
    # A full 40-character SHA keeps `git log <sha>..<ref>` unambiguous.
    assert len(baseline["reviewed_through"]) == 40
    assert baseline["reviewed_date"]


def test_workflow_is_scheduled_and_fails_on_unreviewed_commits() -> None:
    workflow = (
        Path(__file__).parents[1] / ".github" / "workflows" / "upstream-check.yml"
    ).read_text(encoding="utf-8")

    assert "schedule:" in workflow
    assert "cron:" in workflow
    assert "workflow_dispatch:" in workflow
    assert "tools/check_upstream_commits.py" in workflow
    # The check has to be able to fail, otherwise it is only decoration.
    assert "needs_attention == 'true'" in workflow
    assert "exit 1" in workflow
    # Upstream history is unrelated, so a shallow clone would break `git log`.
    assert "fetch-depth: 0" in workflow


def test_is_irrelevant_classifies_out_of_scope_areas() -> None:
    assert checker.is_irrelevant(["worker/src/index.js"])
    assert checker.is_irrelevant(["sw.js", "manifest.json"])
    assert checker.is_irrelevant(["assets/logo.png", "icons/icon-192.png"])
    # Anything touching real application logic must still be reviewed.
    assert not checker.is_irrelevant(["app.js"])
    assert not checker.is_irrelevant(["worker/src/index.js", "app.js"])
    # An empty file list is not evidence of irrelevance.
    assert not checker.is_irrelevant([])


def test_render_markdown_reports_no_new_commits() -> None:
    baseline = {
        "repo": "https://example.invalid/upstream.git",
        "branch": "main",
        "reviewed_through": "a" * 40,
        "reviewed_date": "2026-08-09",
    }

    report = checker.render_markdown(baseline, [])

    assert "No new upstream commits" in report


def test_render_markdown_separates_review_from_irrelevant() -> None:
    baseline = {
        "repo": "https://example.invalid/upstream.git",
        "branch": "main",
        "reviewed_through": "a" * 40,
        "reviewed_date": "2026-08-09",
    }
    commits = [
        {
            "sha": "b" * 40,
            "short": "bbbbbbb",
            "date": "2026-08-01",
            "subject": "fix: chroma tweak",
            "files": ["app.js"],
            "irrelevant": False,
        },
        {
            "sha": "c" * 40,
            "short": "ccccccc",
            "date": "2026-08-02",
            "subject": "chore: worker only",
            "files": ["worker/src/index.js"],
            "irrelevant": True,
        },
    ]

    report = checker.render_markdown(baseline, commits)

    assert "**1 to review**, 1 in known-irrelevant" in report
    assert "## Needs review" in report
    assert "bbbbbbb" in report
    assert "ccccccc" in report


def test_render_markdown_surfaces_check_failure() -> None:
    baseline = {
        "repo": "https://example.invalid/upstream.git",
        "branch": "main",
        "reviewed_through": "a" * 40,
        "reviewed_date": "2026-08-09",
    }

    report = checker.render_markdown(baseline, [], error="git fetch failed")

    assert "Check failed" in report
    assert "git fetch failed" in report


def test_write_github_output_flags_attention(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "gh-output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))

    checker.write_github_output(2, False, Path("report.md"))
    written = output.read_text(encoding="utf-8")

    assert "to_review=2" in written
    assert "needs_attention=true" in written

    output.write_text("", encoding="utf-8")
    checker.write_github_output(0, False, Path("report.md"))

    assert "needs_attention=false" in output.read_text(encoding="utf-8")


def test_write_github_output_flags_attention_when_check_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "gh-output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))

    checker.write_github_output(0, True, Path("report.md"))
    written = output.read_text(encoding="utf-8")

    # A broken check must not read as "upstream is clean".
    assert "check_failed=true" in written
    assert "needs_attention=true" in written


def test_load_baseline_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(checker.UpstreamCheckError):
        checker.load_baseline(tmp_path / "nope.json")


def test_baseline_matches_decisions_record() -> None:
    # The baseline is only trustworthy if the human-facing decision log says
    # the same review happened.
    decisions = (
        Path(__file__).parents[1] / "docs" / "DECISIONS.md"
    ).read_text(encoding="utf-8")
    baseline = json.loads(
        (Path(__file__).parents[1] / "tools" / "upstream_baseline.json").read_text(
            encoding="utf-8"
        )
    )

    assert baseline["reviewed_date"] in decisions
