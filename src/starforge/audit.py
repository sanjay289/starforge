from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Check:
    id: str
    label: str
    points: int
    passed: bool
    detail: str
    fix: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class Audit:
    path: str
    score: int
    possible: int
    checks: tuple[Check, ...]

    @property
    def percent(self) -> int:
        if self.possible == 0:
            return 0
        return round((self.score / self.possible) * 100)

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "score": self.score,
            "possible": self.possible,
            "percent": self.percent,
            "checks": [check.to_dict() for check in self.checks],
        }


README_NAMES = ("README.md", "README.rst", "README.txt", "readme.md")
LICENSE_NAMES = ("LICENSE", "LICENSE.md", "COPYING")
CHANGELOG_NAMES = ("CHANGELOG.md", "HISTORY.md", "RELEASES.md")
PACKAGE_FILES = ("pyproject.toml", "package.json", "Cargo.toml", "go.mod", "Gemfile", "composer.json")
CI_DIRS = (".github/workflows", ".gitlab-ci.yml", ".circleci")
TEST_DIRS = ("tests", "test", "spec", "__tests__")


def audit_repo(path: str | Path) -> Audit:
    root = Path(path).expanduser().resolve()
    readme = _first_existing(root, README_NAMES)
    readme_text = _read_text(readme) if readme else ""

    checks = (
        _check_file(root, README_NAMES, "readme", "README exists", 15, "Add a README that explains the project in plain language."),
        _check_readme_section(readme_text, ("install", "installation", "setup"), "install", "Install instructions", 10, "Add an Install section with copy-pasteable commands."),
        _check_readme_section(readme_text, ("usage", "quickstart", "example"), "usage", "Usage or quickstart", 12, "Show the fastest useful command or code example."),
        _check_visual_proof(readme_text, root),
        _check_file(root, LICENSE_NAMES, "license", "License exists", 10, "Add a license so people know whether they can use the project."),
        _check_tests(root),
        _check_ci(root),
        _check_file(root, CHANGELOG_NAMES, "changelog", "Changelog exists", 5, "Add a changelog or release notes so visitors see project momentum."),
        _check_file(root, ("CONTRIBUTING.md", ".github/CONTRIBUTING.md"), "contributing", "Contribution guide", 5, "Add contribution instructions for issues, PRs, and local setup."),
        _check_file(root, ("CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md"), "code_of_conduct", "Code of conduct", 3, "Add a code of conduct for community expectations."),
        _check_file(root, ("SECURITY.md", ".github/SECURITY.md"), "security", "Security policy", 4, "Add a security policy explaining how to report vulnerabilities."),
        _check_file(root, PACKAGE_FILES, "package_metadata", "Package metadata", 8, "Add package metadata for the language ecosystem you use."),
        _check_file(root, (".github/ISSUE_TEMPLATE", ".github/ISSUE_TEMPLATE.md"), "issue_template", "Issue template", 3, "Add an issue template to improve bug reports."),
        _check_file(root, (".github/pull_request_template.md", ".github/PULL_REQUEST_TEMPLATE.md"), "pr_template", "Pull request template", 3, "Add a pull request template with testing and context prompts."),
    )

    score = sum(check.points for check in checks if check.passed)
    possible = sum(check.points for check in checks)
    return Audit(str(root), score, possible, checks)


def render_text(audit: Audit) -> str:
    lines = [f"Starforge score: {audit.score}/{audit.possible} ({audit.percent}%)", ""]
    passed = [check for check in audit.checks if check.passed]
    failed = [check for check in audit.checks if not check.passed]

    if passed:
        lines.append("Strong signals")
        for check in passed:
            lines.append(f"  [ok] {check.label}: {check.detail}")
        lines.append("")

    if failed:
        lines.append("Highest impact fixes")
        for check in sorted(failed, key=lambda item: item.points, reverse=True):
            lines.append(f"  [missing] {check.label}: {check.fix}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _check_file(root: Path, names: Iterable[str], id_: str, label: str, points: int, fix: str) -> Check:
    found = _first_existing(root, names)
    return Check(
        id=id_,
        label=label,
        points=points,
        passed=found is not None,
        detail=str(found.relative_to(root)) if found else "Not found",
        fix=fix,
    )


def _check_readme_section(
    readme_text: str,
    keywords: tuple[str, ...],
    id_: str,
    label: str,
    points: int,
    fix: str,
) -> Check:
    text = readme_text.lower()
    passed = any(keyword in text for keyword in keywords)
    return Check(
        id=id_,
        label=label,
        points=points,
        passed=passed,
        detail="README contains a matching section" if passed else "No matching README section",
        fix=fix,
    )


def _check_visual_proof(readme_text: str, root: Path) -> Check:
    text = readme_text.lower()
    visual_words = ("![", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", "screenshot", "demo")
    asset_dirs = ("assets", "docs", "media")
    has_visual = any(word in text for word in visual_words)
    has_asset = any((root / directory).exists() for directory in asset_dirs)
    passed = has_visual or has_asset
    return Check(
        id="visual_proof",
        label="Visual proof",
        points=10,
        passed=passed,
        detail="Screenshot, demo, or asset directory detected" if passed else "No screenshot or demo detected",
        fix="Add screenshots, demo GIFs, SVGs, or terminal output examples.",
    )


def _check_tests(root: Path) -> Check:
    has_test_dir = any((root / name).exists() for name in TEST_DIRS)
    has_test_file = any(_has_glob_match(root, pattern) for pattern in ("test_*.py", "*_test.go", "*.test.js", "*.spec.ts"))
    passed = has_test_dir or has_test_file
    return Check(
        id="tests",
        label="Tests detected",
        points=8,
        passed=passed,
        detail="Test files or directories found" if passed else "No tests found",
        fix="Add at least one test that proves the main workflow still works.",
    )


def _check_ci(root: Path) -> Check:
    passed = any((root / name).exists() for name in CI_DIRS)
    return Check(
        id="ci",
        label="Continuous integration",
        points=8,
        passed=passed,
        detail="CI configuration found" if passed else "No CI configuration found",
        fix="Add GitHub Actions or another CI workflow that runs tests on pull requests.",
    )


def _first_existing(root: Path, names: Iterable[str]) -> Path | None:
    for name in names:
        candidate = root / name
        if candidate.exists():
            return candidate
    return None


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(errors="ignore")

def _has_glob_match(root: Path, pattern: str) -> bool:
    return next(root.glob(pattern), None) is not None
