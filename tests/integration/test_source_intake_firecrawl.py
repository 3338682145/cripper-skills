from __future__ import annotations

import importlib.util
from pathlib import Path

from cliper.markdown import read_markdown_document


class FakeNativeResponse:
    def __init__(self, body: str, url: str) -> None:
        self.text = body
        self.url = url
        self.encoding = "utf-8"

    def raise_for_status(self) -> None:
        return None


class FakeFirecrawlResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code
        self.text = ""

    def json(self) -> dict:
        return self._payload


def load_script_module(name: str, relative_path: str):
    path = Path(__file__).resolve().parents[2] / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_low_signal_native_page_uses_firecrawl(monkeypatch, tmp_path) -> None:
    module = load_script_module(
        "source_intake_firecrawl_success",
        "optional-skills/research/source-intake/scripts/intake_url.py",
    )
    html_body = (Path(__file__).resolve().parents[1] / "fixtures" / "example_article.html").read_text(encoding="utf-8")

    def fake_get(self, url, timeout, headers):
        return FakeNativeResponse(html_body, "https://example.com/weak-article")

    def fake_post(url, headers, json, timeout):
        return FakeFirecrawlResponse(
            {
                "data": {
                    "markdown": "# Firecrawl Rescue\n\nRecovered content with better extraction.\n\n## Details\n\nMore structured content.",
                    "rawHtml": "<html><body><main><h1>Firecrawl Rescue</h1></main></body></html>",
                    "metadata": {
                        "title": "Firecrawl Rescue",
                        "language": "en",
                        "sourceURL": "https://example.com/weak-article",
                    },
                }
            }
        )

    monkeypatch.setattr("cliper.adapters.web_url.requests.Session.get", fake_get)
    monkeypatch.setattr("requests.post", fake_post)
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test-key")

    destination = module.intake_url(
        "https://example.com/weak-article",
        raw_dir=tmp_path / "raw",
        review_dir=tmp_path / "review",
        archive_dir=tmp_path / "archive",
        verdict="REVIEW_REQUIRED",
        confidence=0.52,
        signal_level="medium",
    )

    metadata, body = read_markdown_document(destination)
    assert metadata["backend_used"] == "firecrawl"
    assert "native_too_short" in metadata["reason_codes"]
    assert "firecrawl_fallback_used" in metadata["reason_codes"]
    assert metadata["verdict"] == "REVIEW_REQUIRED"
    assert destination.parent == (tmp_path / "review").resolve()
    assert "Recovered content" in body


def test_js_heavy_page_without_firecrawl_key_routes_to_review(monkeypatch, tmp_path) -> None:
    module = load_script_module(
        "source_intake_firecrawl_missing_key",
        "optional-skills/research/source-intake/scripts/intake_url.py",
    )
    js_heavy_html = """
    <html>
      <head><title>JS Heavy Page</title></head>
      <body>
        <div id="__NEXT_DATA__">{}</div>
        <main><p>Short fallback text.</p></main>
      </body>
    </html>
    """

    def fake_get(self, url, timeout, headers):
        return FakeNativeResponse(js_heavy_html, "https://example.com/js-heavy")

    monkeypatch.setattr("cliper.adapters.web_url.requests.Session.get", fake_get)
    monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)

    destination = module.intake_url(
        "https://example.com/js-heavy",
        raw_dir=tmp_path / "raw",
        review_dir=tmp_path / "review",
        archive_dir=tmp_path / "archive",
        verdict="AUTO_PASS",
        confidence=0.9,
        signal_level="high",
    )

    metadata, _ = read_markdown_document(destination)
    assert metadata["verdict"] == "REVIEW_REQUIRED"
    assert "native_js_heavy_page" in metadata["reason_codes"]
    assert "firecrawl_missing_api_key" in metadata["reason_codes"]
    assert destination.parent == (tmp_path / "review").resolve()


def test_native_fetch_failure_can_retry_with_firecrawl(monkeypatch, tmp_path) -> None:
    module = load_script_module(
        "source_intake_firecrawl_native_failure",
        "optional-skills/research/source-intake/scripts/intake_url.py",
    )

    def fake_get(self, url, timeout, headers):
        raise RuntimeError("network down")

    def fake_post(url, headers, json, timeout):
        return FakeFirecrawlResponse(
            {
                "data": {
                    "markdown": "# Recovered After Native Failure\n\nFirecrawl content path.",
                    "rawHtml": "<html><body><main>Recovered</main></body></html>",
                    "metadata": {
                        "title": "Recovered After Native Failure",
                        "language": "en",
                        "sourceURL": "https://example.com/native-failure",
                    },
                }
            }
        )

    monkeypatch.setattr("cliper.adapters.web_url.requests.Session.get", fake_get)
    monkeypatch.setattr("requests.post", fake_post)
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test-key")

    destination = module.intake_url(
        "https://example.com/native-failure",
        raw_dir=tmp_path / "raw",
        review_dir=tmp_path / "review",
        archive_dir=tmp_path / "archive",
        verdict="REVIEW_REQUIRED",
        confidence=0.3,
        signal_level="low",
    )

    metadata, body = read_markdown_document(destination)
    assert metadata["backend_used"] == "firecrawl"
    assert "native_fetch_failed" in metadata["reason_codes"]
    assert "firecrawl_fallback_used" in metadata["reason_codes"]
    assert "Firecrawl content path." in body
