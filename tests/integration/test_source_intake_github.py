from __future__ import annotations

import importlib.util
from pathlib import Path

from cliper.markdown import read_markdown_document


def load_script_module(name: str, relative_path: str):
    path = Path(__file__).resolve().parents[2] / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_classify_url_marks_repo_blob_and_issue_as_github_repo() -> None:
    module = load_script_module(
        "source_intake_github_classifier",
        "optional-skills/research/source-intake/scripts/classify_url.py",
    )

    assert module.classify_url("https://github.com/openai/codex") == "github_repo"
    assert module.classify_url("https://github.com/openai/codex/blob/main/README.md") == "github_repo"
    assert module.classify_url("https://github.com/openai/codex/issues/12") == "github_repo"


def test_github_repo_creates_placeholder_packet_without_backend_calls(monkeypatch, tmp_path) -> None:
    module = load_script_module(
        "source_intake_github_placeholder",
        "optional-skills/research/source-intake/scripts/intake_url.py",
    )

    def should_not_run(*args, **kwargs):
        raise AssertionError("GitHub placeholder flow must not call crawl or content backends")

    monkeypatch.setattr(module, "run_native_backend", should_not_run)
    monkeypatch.setattr(module, "run_firecrawl_backend", should_not_run)
    monkeypatch.setattr(module, "run_mineru_backend", should_not_run)

    destination = module.intake_url(
        "https://github.com/openai/codex",
        raw_dir=tmp_path / "raw",
        review_dir=tmp_path / "review",
        archive_dir=tmp_path / "archive",
    )

    metadata, body = read_markdown_document(destination)
    assert metadata["source_type"] == "github_repo"
    assert metadata["backend_used"] == "github_placeholder"
    assert metadata["verdict"] == "UNSUPPORTED"
    assert "github_placeholder" in metadata["reason_codes"]
    assert "github_v1_deferred" in metadata["reason_codes"]
    assert destination.parent == (tmp_path / "review").resolve()
    assert "No repository crawling, cloning" in body


def test_github_blob_and_issue_stay_placeholder_boundary(monkeypatch, tmp_path) -> None:
    module = load_script_module(
        "source_intake_github_boundary",
        "optional-skills/research/source-intake/scripts/intake_url.py",
    )

    calls: list[str] = []

    def should_not_run(*args, **kwargs):
        calls.append("backend")
        raise AssertionError("GitHub placeholder flow must not clone or crawl")

    monkeypatch.setattr(module, "run_native_backend", should_not_run)
    monkeypatch.setattr(module, "run_firecrawl_backend", should_not_run)
    monkeypatch.setattr(module, "run_mineru_backend", should_not_run)

    blob_dest = module.intake_url(
        "https://github.com/openai/codex/blob/main/README.md",
        raw_dir=tmp_path / "raw",
        review_dir=tmp_path / "review",
        archive_dir=tmp_path / "archive",
    )
    issue_dest = module.intake_url(
        "https://github.com/openai/codex/issues/12",
        raw_dir=tmp_path / "raw",
        review_dir=tmp_path / "review",
        archive_dir=tmp_path / "archive",
    )

    blob_metadata, _ = read_markdown_document(blob_dest)
    issue_metadata, _ = read_markdown_document(issue_dest)
    assert blob_metadata["backend_used"] == "github_placeholder"
    assert issue_metadata["backend_used"] == "github_placeholder"
    assert blob_metadata["verdict"] == "UNSUPPORTED"
    assert issue_metadata["verdict"] == "UNSUPPORTED"
    assert calls == []
