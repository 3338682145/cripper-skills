from __future__ import annotations

import importlib.util
from pathlib import Path

from cliper.markdown import read_markdown_document


class FakeResponse:
    def __init__(self, body: str, url: str) -> None:
        self.text = body
        self.url = url
        self.encoding = "utf-8"

    def raise_for_status(self) -> None:
        return None


def load_script_module(name: str, relative_path: str):
    path = Path(__file__).resolve().parents[2] / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_intake_url_writes_source_packet_to_raw(monkeypatch, tmp_path) -> None:
    module = load_script_module(
        "source_intake_intake_url",
        "optional-skills/research/source-intake/scripts/intake_url.py",
    )
    html_body = (Path(__file__).resolve().parents[1] / "fixtures" / "example_article.html").read_text(encoding="utf-8")

    def fake_get(self, url, timeout, headers):
        return FakeResponse(html_body, "https://example.com/article?a=1&b=2")

    monkeypatch.setattr("cliper.adapters.web_url.requests.Session.get", fake_get)

    destination = module.intake_url(
        "https://example.com/article?b=2&a=1#fragment",
        raw_dir=tmp_path / "raw",
        review_dir=tmp_path / "review",
        archive_dir=tmp_path / "archive",
        verdict="AUTO_PASS",
        confidence=0.92,
        signal_level="high",
        reason_codes=["native_complete"],
        suggested_kind="blog",
    )

    metadata, body = read_markdown_document(destination)
    assert metadata["schema"] == "source-packet"
    assert metadata["backend_used"] == "native"
    assert metadata["verdict"] == "AUTO_PASS"
    assert metadata["canonical_url"] == "https://example.com/article?a=1&b=2"
    assert metadata["provenance"]["fetch_url"] == "https://example.com/article?b=2&a=1#fragment"
    assert metadata["provenance"]["resolved_url"] == "https://example.com/article?a=1&b=2"
    assert Path(metadata["refs"]["artifact_dir"]).exists()
    assert Path(metadata["refs"]["raw_html"]).exists()
    assert Path(metadata["refs"]["verifier_report"]).exists()
    assert "Example Ingest Article" in body
    assert destination.parent == (tmp_path / "raw").resolve()


def test_intake_url_dedupes_existing_packet(monkeypatch, tmp_path) -> None:
    module = load_script_module(
        "source_intake_intake_url_dedupe",
        "optional-skills/research/source-intake/scripts/intake_url.py",
    )
    html_body = (Path(__file__).resolve().parents[1] / "fixtures" / "example_article.html").read_text(encoding="utf-8")

    def fake_get(self, url, timeout, headers):
        return FakeResponse(html_body, "https://example.com/article?a=1&b=2")

    monkeypatch.setattr("cliper.adapters.web_url.requests.Session.get", fake_get)

    first = module.intake_url(
        "https://example.com/article?b=2&a=1#fragment",
        raw_dir=tmp_path / "raw",
        review_dir=tmp_path / "review",
        archive_dir=tmp_path / "archive",
        verdict="AUTO_PASS",
        confidence=0.91,
        signal_level="high",
        reason_codes=["native_complete"],
    )
    second = module.intake_url(
        "https://example.com/article?a=1&b=2",
        raw_dir=tmp_path / "raw",
        review_dir=tmp_path / "review",
        archive_dir=tmp_path / "archive",
        verdict="AUTO_PASS",
        confidence=0.91,
        signal_level="high",
        reason_codes=["native_complete"],
    )

    assert first == second
    assert len(list((tmp_path / "raw").rglob("*.md"))) == 1


def test_intake_url_routes_non_pass_packets_to_review(monkeypatch, tmp_path) -> None:
    module = load_script_module(
        "source_intake_intake_url_review",
        "optional-skills/research/source-intake/scripts/intake_url.py",
    )
    html_body = (Path(__file__).resolve().parents[1] / "fixtures" / "example_article.html").read_text(encoding="utf-8")

    def fake_get(self, url, timeout, headers):
        return FakeResponse(html_body, "https://example.com/article")

    monkeypatch.setattr("cliper.adapters.web_url.requests.Session.get", fake_get)

    destination = module.intake_url(
        "https://example.com/article",
        raw_dir=tmp_path / "raw",
        review_dir=tmp_path / "review",
        archive_dir=tmp_path / "archive",
        verdict="REVIEW_REQUIRED",
        confidence=0.35,
        signal_level="medium",
        reason_codes=["phase2_baseline"],
    )

    metadata, _ = read_markdown_document(destination)
    assert metadata["verdict"] == "REVIEW_REQUIRED"
    assert destination.parent == (tmp_path / "review").resolve()
    assert len(list((tmp_path / "raw").rglob("*.md"))) == 0
