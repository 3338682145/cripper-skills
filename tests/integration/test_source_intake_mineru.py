from __future__ import annotations

import importlib.util
from pathlib import Path

from cliper.markdown import read_markdown_document


class FakePdfResponse:
    def __init__(self, content: bytes) -> None:
        self.content = content

    def raise_for_status(self) -> None:
        return None


class FakeMinerUApiResponse:
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


def fake_mineru_payload(url: str) -> dict:
    canonical_url = url.split("#", 1)[0]
    return {
        "canonical_url": canonical_url,
        "resolved_url": canonical_url,
        "title": "MinerU Parsed Document",
        "language": "en",
        "published_at": None,
        "body_markdown": "# MinerU Parsed Document\n\nStructured PDF content.\n\n## Table\n\n| A | B |\n| - | - |\n| 1 | 2 |",
        "content_hash": "abc123mineru",
        "dedupe_key": "dedupe-mineru",
        "raw_html": "",
        "backend_used": "mineru",
        "backend_version": "mineru",
        "reason_codes": ["mineru_backend_used"],
        "provenance": {
            "fetch_method": "mineru",
            "fetch_url": url,
            "resolved_url": canonical_url,
            "extractor": "mineru",
            "extractor_version": "mineru",
        },
        "artifact_files": {
            "raw_pdf": b"%PDF-1.4\n%Fake PDF\n",
            "extracted_json": {"blocks": [{"type": "paragraph", "text": "Structured PDF content."}]},
            "source_snapshot": "# MinerU Parsed Document\n\nStructured PDF content.",
        },
    }


def test_run_mineru_backend_api_mode_returns_artifacts(monkeypatch) -> None:
    module = load_script_module(
        "source_intake_run_mineru_backend",
        "optional-skills/research/source-intake/scripts/run_mineru_backend.py",
    )

    def fake_get(url, timeout, headers):
        return FakePdfResponse(b"%PDF-1.4\n%Fake PDF\n")

    def fake_post(url, files, timeout):
        return FakeMinerUApiResponse(
            {
                "markdown": "# MinerU Parsed Document\n\nStructured PDF content.",
                "json": {"blocks": [{"type": "paragraph", "text": "Structured PDF content."}]},
            }
        )

    monkeypatch.setattr("requests.get", fake_get)
    monkeypatch.setattr("requests.post", fake_post)
    monkeypatch.setenv("MINERU_ENDPOINT", "http://mineru.local")

    payload = module.run_mineru_backend("https://example.com/report.pdf")
    assert payload["backend_used"] == "mineru"
    assert payload["artifact_files"]["raw_pdf"].startswith(b"%PDF")
    assert "blocks" in payload["artifact_files"]["extracted_json"]
    assert "Structured PDF content." in payload["body_markdown"]


def test_pdf_url_routes_directly_to_mineru(monkeypatch, tmp_path) -> None:
    module = load_script_module(
        "source_intake_intake_url_pdf_direct",
        "optional-skills/research/source-intake/scripts/intake_url.py",
    )

    monkeypatch.setattr(module, "run_mineru_backend", lambda url: fake_mineru_payload(url))

    destination = module.intake_url(
        "https://example.com/report.pdf",
        raw_dir=tmp_path / "raw",
        review_dir=tmp_path / "review",
        archive_dir=tmp_path / "archive",
        verdict="REVIEW_REQUIRED",
        confidence=0.4,
        signal_level="medium",
    )

    metadata, body = read_markdown_document(destination)
    assert metadata["backend_used"] == "mineru"
    assert "pdf_direct_to_mineru" in metadata["reason_codes"]
    assert Path(metadata["refs"]["raw_pdf"]).exists()
    assert Path(metadata["refs"]["extracted_json"]).exists()
    assert Path(metadata["refs"]["source_snapshot"]).exists()
    assert "Structured PDF content." in body


def test_firecrawl_pdf_reason_escalates_to_mineru(monkeypatch, tmp_path) -> None:
    module = load_script_module(
        "source_intake_intake_url_pdf_escalation",
        "optional-skills/research/source-intake/scripts/intake_url.py",
    )

    monkeypatch.setattr(module, "classify_url", lambda url: "docs_page")
    monkeypatch.setattr(module, "run_mineru_backend", lambda url: fake_mineru_payload(url))

    def should_not_run_native(url: str):
        raise AssertionError("native backend should not run when MinerU escalation is already requested")

    monkeypatch.setattr(module, "run_native_backend", should_not_run_native)

    destination = module.intake_url(
        "https://example.com/complex-doc",
        raw_dir=tmp_path / "raw",
        review_dir=tmp_path / "review",
        archive_dir=tmp_path / "archive",
        verdict="REVIEW_REQUIRED",
        confidence=0.35,
        signal_level="low",
        reason_codes=["firecrawl_pdf_table_heavy"],
    )

    metadata, _ = read_markdown_document(destination)
    assert metadata["backend_used"] == "mineru"
    assert "firecrawl_pdf_table_heavy" in metadata["reason_codes"]


def test_pdf_url_without_mineru_routes_as_unsupported(monkeypatch, tmp_path) -> None:
    module = load_script_module(
        "source_intake_intake_url_pdf_unsupported",
        "optional-skills/research/source-intake/scripts/intake_url.py",
    )

    def missing_mineru(url: str):
        raise module.MinerUBackendError(
            "Missing MINERU_ENDPOINT for MinerU fallback.",
            reason_codes=["mineru_missing_endpoint"],
        )

    monkeypatch.setattr(module, "run_mineru_backend", missing_mineru)

    destination = module.intake_url(
        "https://example.com/report.pdf",
        raw_dir=tmp_path / "raw",
        review_dir=tmp_path / "review",
        archive_dir=tmp_path / "archive",
        verdict="REVIEW_REQUIRED",
        confidence=0.2,
        signal_level="low",
    )

    metadata, _ = read_markdown_document(destination)
    assert metadata["verdict"] == "UNSUPPORTED"
    assert metadata["backend_used"] == "mineru"
    assert "mineru_missing_endpoint" in metadata["reason_codes"]
    assert destination.parent == (tmp_path / "review").resolve()
