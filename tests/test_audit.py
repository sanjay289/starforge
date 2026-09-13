from pathlib import Path

from starforge.audit import audit_repo, render_text


def test_audit_scores_common_repo_signals(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n\n## Install\n\npip install demo\n\n## Usage\n\n```bash\ndemo\n```\n",
        encoding="utf-8",
    )
    (tmp_path / "LICENSE").write_text("MIT", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / ".github" / "workflows").mkdir(parents=True)

    audit = audit_repo(tmp_path)
    ids = {check.id: check.passed for check in audit.checks}

    assert ids["readme"]
    assert ids["install"]
    assert ids["usage"]
    assert ids["license"]
    assert ids["tests"]
    assert ids["ci"]
    assert ids["package_metadata"]
    assert audit.score > 50


def test_render_text_prioritizes_missing_high_impact_items(tmp_path: Path) -> None:
    audit = audit_repo(tmp_path)
    output = render_text(audit)

    assert "Starforge score:" in output
    assert "[missing] README exists" in output
    assert output.index("README exists") < output.index("Package metadata")
