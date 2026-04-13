from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from cliper.cli import app
from cliper.service import ValidationService


def test_registry_validation_rejects_missing_frontmatter(tmp_path: Path) -> None:
    bad_file = tmp_path / "content/registry/sources/bad.md"
    bad_file.parent.mkdir(parents=True, exist_ok=True)
    bad_file.write_text("no frontmatter here", encoding="utf-8")

    issues = ValidationService(tmp_path).validate_registry()

    assert issues
    assert "missing YAML frontmatter" in issues[0].message


def test_registry_cli_passes_for_valid_registry(workspace_factory) -> None:
    root = workspace_factory()
    runner = CliRunner()

    result = runner.invoke(app, ["registry", "validate", "--root", str(root)])

    assert result.exit_code == 0
    assert "Registry validation passed." in result.stdout

