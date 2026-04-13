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


def test_verify_packet_returns_only_allowed_fields() -> None:
    module = load_script_module(
        "source_intake_verify_packet_module",
        "optional-skills/research/source-intake/scripts/verify_packet.py",
    )
    payload = {
        "title": "Structured Docs",
        "backend_used": "native",
        "body_markdown": "\n".join(
            [
                "# Structured Docs",
                "",
                "## Overview",
                "",
                "This document has enough structure and enough words to justify an automatic pass.",
                "",
                "## Details",
                "",
            ]
            + ["More useful technical content." for _ in range(40)]
        ),
    }

    result = module.verify_packet(
        source_type="docs_page",
        backend_payload=payload,
        reason_codes=[],
    )

    assert result.verdict in {"AUTO_PASS", "REVIEW_REQUIRED", "LOW_SIGNAL", "UNSUPPORTED"}
    assert 0.0 <= result.confidence <= 1.0
    assert result.signal_level in {"high", "medium", "low"}
    assert isinstance(result.reason_codes, list)
    assert isinstance(result.summary, str)
    assert result.suggested_kind == "docs"


def test_intake_url_routes_auto_pass_to_raw(monkeypatch, tmp_path) -> None:
    module = load_script_module(
        "source_intake_verifier_routing_raw",
        "optional-skills/research/source-intake/scripts/intake_url.py",
    )
    html_body = (Path(__file__).resolve().parents[1] / "fixtures" / "hermes_profiles_like.html").read_text(encoding="utf-8")

    def fake_get(self, url, timeout, headers):
        return FakeResponse(html_body, "https://example.com/docs/profiles")

    monkeypatch.setattr("cliper.adapters.web_url.requests.Session.get", fake_get)

    destination = module.intake_url(
        "https://example.com/docs/profiles",
        raw_dir=tmp_path / "raw",
        review_dir=tmp_path / "review",
        archive_dir=tmp_path / "archive",
        verdict="AUTO_PASS",
        confidence=0.95,
        signal_level="high",
    )

    metadata, _ = read_markdown_document(destination)
    assert metadata["verdict"] == "AUTO_PASS"
    assert destination.parent == (tmp_path / "raw").resolve()
    assert metadata["canonical_url"] == "https://example.com/docs/profiles"


def test_intake_url_routes_non_auto_pass_to_review(monkeypatch, tmp_path) -> None:
    module = load_script_module(
        "source_intake_verifier_routing_review",
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
    )

    metadata, _ = read_markdown_document(destination)
    assert metadata["verdict"] in {"REVIEW_REQUIRED", "LOW_SIGNAL", "UNSUPPORTED"}
    assert destination.parent == (tmp_path / "review").resolve()


def test_canonical_url_dedupe_holds_across_review_and_raw(monkeypatch, tmp_path) -> None:
    module = load_script_module(
        "source_intake_verifier_route_dedupe",
        "optional-skills/research/source-intake/scripts/intake_url.py",
    )
    html_body = (Path(__file__).resolve().parents[1] / "fixtures" / "hermes_profiles_like.html").read_text(encoding="utf-8")

    def fake_get(self, url, timeout, headers):
        return FakeResponse(html_body, "https://example.com/docs/profiles")

    monkeypatch.setattr("cliper.adapters.web_url.requests.Session.get", fake_get)

    review_path = module.intake_url(
        "https://example.com/docs/profiles?from=review",
        raw_dir=tmp_path / "raw",
        review_dir=tmp_path / "review",
        archive_dir=tmp_path / "archive",
        verdict="REVIEW_REQUIRED",
        confidence=0.5,
        signal_level="medium",
    )
    raw_attempt = module.intake_url(
        "https://example.com/docs/profiles",
        raw_dir=tmp_path / "raw",
        review_dir=tmp_path / "review",
        archive_dir=tmp_path / "archive",
        verdict="AUTO_PASS",
        confidence=0.95,
        signal_level="high",
    )

    assert review_path == raw_attempt
    assert len(list((tmp_path / "review").rglob("*.md"))) == 1
    assert len(list((tmp_path / "raw").rglob("*.md"))) == 0
