"""Report upstream `line-sticker-studio` commits that have not been reviewed.

`sticker-forge` is a conceptual fork: it shares no git history with upstream and
reimplements the pipeline in Python, so upstream changes can never be merged
directly. What they can do is carry algorithm fixes and format-spec corrections
worth reimplementing (see `docs/DECISIONS.md`).

This checker answers one question on a schedule: *are there upstream commits we
have not looked at yet?* It deliberately does not decide whether a commit should
be ported -- that judgement stays with a human. It only lowers the noise by
flagging commits whose files are all in known-irrelevant areas (the upstream PWA
shell, the Cloudflare Worker, marketing assets), which this project does not and
will not have.

Reviewed state lives in `tools/upstream_baseline.json`.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = REPO_ROOT / "tools" / "upstream_baseline.json"

# Upstream paths that cannot apply to this project by construction:
# the Cloudflare Worker and quota/proxy backend are forbidden here, and the PWA
# shell, service worker, and marketing assets have no counterpart in a local
# Python + pywebview desktop app.
IRRELEVANT_PREFIXES = (
    "worker/",
    "tools/make_og",
    "tools/make_icons",
    "assets/",
    "icons/",
    "campaigns/",
    ".github/",
)
IRRELEVANT_FILES = (
    "sw.js",
    "manifest.json",
    "og.png",
    "index.html",
    "styles.css",
    "robots.txt",
    "sitemap.xml",
    "CNAME",
)
# Marketing screenshots land at the repository root rather than under `assets/`,
# which is what made commit 1c5d448 (PWA/SEO polish) read as "needs review" when
# every file in it was store-listing material. Matching the extension keeps the
# rule from depending on where upstream happens to drop the next one.
IRRELEVANT_SUFFIXES = (
    ".webp",
    ".avif",
)


class UpstreamCheckError(RuntimeError):
    """Raised when upstream history cannot be inspected."""


def load_baseline(path: Path = BASELINE_PATH) -> dict:
    if not path.exists():
        raise UpstreamCheckError(f"missing baseline file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def run_git(args: list[str], repo_dir: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise UpstreamCheckError(
            f"git {' '.join(args)} failed: {result.stderr.strip()}"
        )
    return result.stdout


def fetch_upstream(baseline: dict, repo_dir: Path) -> None:
    """Fetch the upstream branch into a detached ref we control."""
    branch = baseline["branch"]
    run_git(
        [
            "fetch",
            "--quiet",
            baseline["repo"],
            f"+refs/heads/{branch}:refs/upstream-check/{branch}",
        ],
        repo_dir,
    )


def is_irrelevant(files: list[str]) -> bool:
    """True when every changed file is in an area this project cannot have."""
    if not files:
        return False
    return all(
        path.startswith(IRRELEVANT_PREFIXES)
        or path in IRRELEVANT_FILES
        or path.endswith(IRRELEVANT_SUFFIXES)
        for path in files
    )


def collect_new_commits(baseline: dict, repo_dir: Path) -> list[dict]:
    branch = baseline["branch"]
    ref = f"refs/upstream-check/{branch}"
    reviewed = baseline["reviewed_through"]
    raw = run_git(
        ["log", "--reverse", "--date=short", "--format=%H%x1f%ad%x1f%s", f"{reviewed}..{ref}"],
        repo_dir,
    )
    commits = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        sha, date, subject = line.split("\x1f", 2)
        files = [
            path
            for path in run_git(
                ["show", "--name-only", "--format=", sha], repo_dir
            ).splitlines()
            if path.strip()
        ]
        commits.append(
            {
                "sha": sha,
                "short": sha[:7],
                "date": date,
                "subject": subject,
                "files": files,
                "irrelevant": is_irrelevant(files),
            }
        )
    return commits


def render_markdown(baseline: dict, commits: list[dict], error: str | None = None) -> str:
    lines = ["# Upstream commit review", ""]
    lines.append(f"- Upstream: `{baseline['repo']}` (`{baseline['branch']}`)")
    lines.append(f"- Reviewed through: `{baseline['reviewed_through'][:7]}`")
    lines.append(f"- Last review date: {baseline.get('reviewed_date', 'unknown')}")
    lines.append("")

    if error:
        lines += ["## Check failed", "", f"```\n{error}\n```", ""]
        return "\n".join(lines) + "\n"

    needs = [c for c in commits if not c["irrelevant"]]
    skipped = [c for c in commits if c["irrelevant"]]

    if not commits:
        lines += ["## Result", "", "No new upstream commits. Nothing to review.", ""]
        return "\n".join(lines) + "\n"

    lines += [
        "## Result",
        "",
        f"{len(commits)} new upstream commit(s): "
        f"**{len(needs)} to review**, {len(skipped)} in known-irrelevant areas.",
        "",
    ]

    if needs:
        lines += ["## Needs review", "", "| Commit | Date | Subject |", "| --- | --- | --- |"]
        for commit in needs:
            subject = commit["subject"].replace("|", "\\|")
            lines.append(f"| `{commit['short']}` | {commit['date']} | {subject} |")
        lines.append("")

    if skipped:
        lines += [
            "<details><summary>Known-irrelevant (PWA shell / Worker / assets)</summary>",
            "",
            "| Commit | Date | Subject |",
            "| --- | --- | --- |",
        ]
        for commit in skipped:
            subject = commit["subject"].replace("|", "\\|")
            lines.append(f"| `{commit['short']}` | {commit['date']} | {subject} |")
        lines += ["", "</details>", ""]

    lines += [
        "## Review policy",
        "",
        "1. Upstream is a JS/PWA web app; this project is a local-first Python core. "
        "Port *concepts and fixes*, never source code.",
        "2. Anything requiring a hosted backend (Worker, quota, proxy, Turnstile) is "
        "out of scope by project rule -- record it as N/A.",
        "3. After triaging, update `tools/upstream_baseline.json` "
        "(`reviewed_through`, `reviewed_date`) and note the outcome in "
        "`docs/DECISIONS.md`.",
    ]
    return "\n".join(lines) + "\n"


def write_github_output(
    to_review: int, check_failed: bool, report_path: Path
) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    needs_attention = to_review > 0 or check_failed
    with open(output_path, "a", encoding="utf-8") as output:
        output.write(f"to_review={to_review}\n")
        output.write(f"check_failed={'true' if check_failed else 'false'}\n")
        output.write(f"needs_attention={'true' if needs_attention else 'false'}\n")
        output.write(f"report_path={report_path.as_posix()}\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check upstream line-sticker-studio for unreviewed commits"
    )
    parser.add_argument(
        "--output",
        default="upstream-review-report.md",
        help="Markdown report output path",
    )
    parser.add_argument(
        "--github-output",
        action="store_true",
        help="Write status fields to GITHUB_OUTPUT",
    )
    parser.add_argument(
        "--repo-dir",
        default=str(REPO_ROOT),
        help="Repository directory to run git in",
    )
    args = parser.parse_args()

    repo_dir = Path(args.repo_dir)
    baseline = load_baseline()
    commits: list[dict] = []
    error: str | None = None
    try:
        fetch_upstream(baseline, repo_dir)
        commits = collect_new_commits(baseline, repo_dir)
    except UpstreamCheckError as exc:
        error = str(exc)

    report = render_markdown(baseline, commits, error)
    output_path = Path(args.output)
    output_path.write_text(report, encoding="utf-8")
    print(report)

    to_review = sum(1 for commit in commits if not commit["irrelevant"])
    if args.github_output:
        write_github_output(to_review, error is not None, output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
