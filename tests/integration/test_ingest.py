from __future__ import annotations

import json
from pathlib import Path

from cliper.adapters.web_url import extract_document
from cliper.markdown import read_markdown_document
from cliper.service import IngestService


class FakeResponse:
    def __init__(self, body: str, url: str) -> None:
        self.text = body
        self.url = url
        self.encoding = "utf-8"

    def raise_for_status(self) -> None:
        return None


def test_ingest_run_writes_raw_asset_and_manifest(monkeypatch, workspace_factory) -> None:
    root = workspace_factory(source_url="https://example.com/article?b=2&a=1#fragment")
    html_body = (Path(__file__).resolve().parents[1] / "fixtures" / "example_article.html").read_text(encoding="utf-8")

    def fake_get(self, url, timeout, headers):
        return FakeResponse(html_body, "https://example.com/article?a=1&b=2")

    monkeypatch.setattr("cliper.adapters.web_url.requests.Session.get", fake_get)

    manifest = IngestService(root).run("example-web-source", "example-web-job")

    assert len(manifest.created_assets) == 1
    assert manifest.deduped_assets == []

    asset_path = root / manifest.created_assets[0]
    metadata, body = read_markdown_document(asset_path)
    assert metadata["schema"] == "raw-asset"
    assert metadata["content_hash"]
    assert metadata["dedupe_key"]
    assert "Example Ingest Article" in body

    manifest_path = root / "state/runs" / f"{manifest.run_id}.json"
    manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest_payload["created_assets"] == manifest.created_assets


def test_ingest_run_dedupes_repeated_url(monkeypatch, workspace_factory) -> None:
    root = workspace_factory()
    html_body = (Path(__file__).resolve().parents[1] / "fixtures" / "example_article.html").read_text(encoding="utf-8")

    def fake_get(self, url, timeout, headers):
        return FakeResponse(html_body, "https://example.com/article")

    monkeypatch.setattr("cliper.adapters.web_url.requests.Session.get", fake_get)

    service = IngestService(root)
    first = service.run("example-web-source", "example-web-job")
    second = service.run("example-web-source", "example-web-job")

    assert len(first.created_assets) == 1
    assert len(second.deduped_assets) == 1
    assert len(list((root / "content/raw").rglob("*.md"))) == 1


def test_docs_like_page_preserves_sections_and_filters_noise(monkeypatch, workspace_factory) -> None:
    root = workspace_factory(source_url="https://example.com/docs/profiles")
    html_body = (Path(__file__).resolve().parents[1] / "fixtures" / "hermes_profiles_like.html").read_text(
        encoding="utf-8"
    )

    def fake_get(self, url, timeout, headers):
        return FakeResponse(html_body, "https://example.com/docs/profiles")

    monkeypatch.setattr("cliper.adapters.web_url.requests.Session.get", fake_get)

    manifest = IngestService(root).run("example-web-source", "example-web-job")
    asset_path = root / manifest.created_assets[0]
    metadata, body = read_markdown_document(asset_path)

    assert "## Using profiles" in body
    assert "## Running gateways" in body
    assert "## Configuring profiles" in body
    assert "## How it works" in body
    assert "Skip to main content" not in body
    assert "On this page" not in body
    assert "```bash" in body
    assert metadata["refs"]["source_snapshot"]
    assert (root / metadata["refs"]["source_snapshot"]).exists()


def test_generic_fallback_uses_readability() -> None:
    html_body = (Path(__file__).resolve().parents[1] / "fixtures" / "generic_readability_article.html").read_text(
        encoding="utf-8"
    )

    extracted = extract_document(
        html_body,
        source_url="https://example.com/generic-article",
        resolved_url="https://example.com/generic-article",
    )

    assert "# Generic Long Article" in extracted.body_markdown
    assert "fallback article exists" in extracted.body_markdown
    assert "```bash" in extracted.body_markdown
