"""Pure policy tests for guarded Dependabot merging."""

from tools import classify_dependabot_update as policy


def classify(
    name: str,
    *,
    ecosystem: str = "pip",
    dependency_type: str = "direct:development",
    update_type: str = "version-update:semver-patch",
    files: list[str] | None = None,
) -> dict[str, str]:
    return policy.classify_update(
        ecosystem=ecosystem,
        dependency_type=dependency_type,
        update_type=update_type,
        changed_files=files or ["pyproject.toml"],
        dependency_names=[name],
    )


def test_auto_merges_ci_tooling_minor_and_patch() -> None:
    for update_type in (
        "version-update:semver-patch",
        "version-update:semver-minor",
    ):
        for package in ("pytest", "packaging", "setuptools", "wheel"):
            result = classify(
                package,
                dependency_type=(
                    "direct:production"
                    if package in {"setuptools", "wheel"}
                    else "direct:development"
                ),
                update_type=update_type,
            )
            assert result["decision"] == "auto_merge"


def test_requires_manual_review_for_runtime_gui_and_packaging() -> None:
    for package in ("Pillow", "pywebview", "PyInstaller"):
        result = classify(package, dependency_type="direct:production")
        assert result["decision"] == "manual"


def test_requires_manual_review_for_all_major_updates() -> None:
    result = classify(
        "pytest",
        update_type="version-update:semver-major",
    )
    assert result["decision"] == "manual"


def test_requires_manual_review_for_mixed_safe_and_unsafe_group() -> None:
    result = policy.classify_update(
        ecosystem="pip",
        dependency_type="direct:development",
        update_type="version-update:semver-minor",
        changed_files=["pyproject.toml"],
        dependency_names=["pytest", "pywebview"],
    )
    assert result["decision"] == "manual"


def test_requires_manual_review_outside_pyproject() -> None:
    result = classify(
        "pytest",
        files=["pyproject.toml", "src/sticker_forge/cli.py"],
    )
    assert result["decision"] == "manual"


def test_auto_merges_actions_minor_or_patch_in_workflow_scope() -> None:
    for update_type in (
        "version-update:semver-patch",
        "version-update:semver-minor",
    ):
        result = classify(
            "actions/checkout",
            ecosystem="github-actions",
            dependency_type="direct:production",
            update_type=update_type,
            files=[".github/workflows/ci.yml"],
        )
        assert result["decision"] == "auto_merge"


def test_requires_manual_review_for_actions_major_or_extra_files() -> None:
    major = classify(
        "actions/checkout",
        ecosystem="github-actions",
        dependency_type="direct:production",
        update_type="version-update:semver-major",
        files=[".github/workflows/ci.yml"],
    )
    extra_file = classify(
        "actions/checkout",
        ecosystem="github-actions",
        dependency_type="direct:production",
        files=[".github/workflows/ci.yml", "README.md"],
    )
    assert major["decision"] == "manual"
    assert extra_file["decision"] == "manual"


def test_requires_manual_review_for_indirect_action() -> None:
    result = classify(
        "actions/checkout",
        ecosystem="github-actions",
        dependency_type="indirect",
        files=[".github/workflows/ci.yml"],
    )
    assert result["decision"] == "manual"


def test_requires_manual_review_for_unknown_metadata() -> None:
    result = policy.classify_update(
        ecosystem="pip",
        dependency_type="indirect",
        update_type="unknown",
        changed_files=[],
        dependency_names=[],
    )
    assert result["decision"] == "manual"
