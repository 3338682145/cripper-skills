from __future__ import annotations

import shutil
from pathlib import Path

from cliper.service import ValidationService


def test_validate_all_rejects_invalid_raw_asset(workspace_factory) -> None:
    root = workspace_factory()
    broken = root / "content/raw/2026/04/13/example/broken.md"
    broken.parent.mkdir(parents=True, exist_ok=True)
    broken.write_text("not a frontmatter document", encoding="utf-8")

    issues = ValidationService(root).validate_all()

    assert any(issue.location.endswith("broken.md") for issue in issues)


def test_validate_all_accepts_fixture_raw_asset(workspace_factory) -> None:
    root = workspace_factory()
    (root / "state/runs/run-fixture.json").write_text("{}", encoding="utf-8")
    fixture = Path(__file__).resolve().parents[1] / "fixtures" / "raw_asset.fixture.md"
    target = root / "content/raw/2026/04/13/example/fixture-asset.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(fixture, target)

    issues = ValidationService(root).validate_all()

    assert issues == []

