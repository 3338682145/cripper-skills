from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from cliper.markdown import write_markdown_document


def load_script_module(name: str, relative_path: str):
    path = Path(__file__).resolve().parents[2] / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _fake_packet(path: Path, *, canonical_url: str, verdict: str) -> Path:
    metadata = {
        "schema": "source-packet",
        "schema_version": "0.1.0",
        "packet_id": path.stem,
        "source_type": "docs_page",
        "input_url": canonical_url,
        "canonical_url": canonical_url,
        "title": path.stem,
        "retrieved_at": "2026-04-13T00:00:00Z",
        "published_at": None,
        "language": "en",
        "backend_used": "native",
        "backend_version": "0.1.0",
        "content_hash": path.stem,
        "dedupe_key": path.stem,
        "signal_level": "medium",
        "verdict": verdict,
        "confidence": 0.5,
        "provenance": {
            "fetch_method": "requests.get",
            "fetch_url": canonical_url,
            "resolved_url": canonical_url,
            "extractor": "cliper-native",
            "extractor_version": "0.1.0",
        },
        "reason_codes": ["test_reason"],
        "routing": {
            "suggested_topic": "test-topic",
            "suggested_kind": "docs",
        },
        "refs": {
            "artifact_dir": str(path.parent / "artifacts"),
            "raw_html": None,
            "raw_pdf": None,
            "extracted_json": None,
            "verifier_report": str(path.parent / "verifier-report.json"),
            "source_snapshot": None,
        },
    }
    write_markdown_document(path, metadata, "# Packet\n\nbody")
    return path


def test_empty_queue_returns_silent(tmp_path) -> None:
    module = load_script_module(
        "source_intake_cron_empty",
        "optional-skills/research/source-intake/scripts/cron_drain_queue.py",
    )
    queue_path = tmp_path / "queue.jsonl"
    queue_path.write_text("", encoding="utf-8")

    result = module.drain_queue(
        raw_dir=tmp_path / "raw",
        review_dir=tmp_path / "review",
        archive_dir=tmp_path / "archive",
        queue_path=queue_path,
    )

    assert result == "[SILENT]"


def test_cron_summarizes_mixed_verdicts(monkeypatch, tmp_path) -> None:
    module = load_script_module(
        "source_intake_cron_summary",
        "optional-skills/research/source-intake/scripts/cron_drain_queue.py",
    )
    queue_path = tmp_path / "queue.jsonl"
    queue_path.write_text(
        "\n".join(
            [
                json.dumps({"url": "https://example.com/a"}),
                json.dumps({"url": "https://example.com/b"}),
                json.dumps({"url": "https://example.com/c"}),
                json.dumps({"url": "https://example.com/a"}),
            ]
        ),
        encoding="utf-8",
    )

    verdict_by_url = {
        "https://example.com/a": "AUTO_PASS",
        "https://example.com/b": "REVIEW_REQUIRED",
        "https://example.com/c": "LOW_SIGNAL",
    }

    def fake_intake_url(url, *, raw_dir, review_dir, archive_dir, **kwargs):
        verdict = verdict_by_url[url]
        destination_root = raw_dir if verdict == "AUTO_PASS" else review_dir
        destination_root.mkdir(parents=True, exist_ok=True)
        slug = url.rstrip("/").rsplit("/", 1)[-1]
        return _fake_packet(destination_root / f"{verdict.lower()}-{slug}.md", canonical_url=url, verdict=verdict)

    monkeypatch.setattr(module, "intake_url", fake_intake_url)

    result = module.drain_queue(
        raw_dir=tmp_path / "raw",
        review_dir=tmp_path / "review",
        archive_dir=tmp_path / "archive",
        queue_path=queue_path,
    )

    assert result == "AUTO_PASS=1 REVIEW_REQUIRED=1 LOW_SIGNAL=1"
    assert queue_path.read_text(encoding="utf-8") == ""


def test_cron_skips_existing_or_duplicate_work_before_run(monkeypatch, tmp_path) -> None:
    module = load_script_module(
        "source_intake_cron_dedupe",
        "optional-skills/research/source-intake/scripts/cron_drain_queue.py",
    )
    queue_path = tmp_path / "queue.jsonl"
    queue_path.write_text(
        "\n".join(
            [
                json.dumps({"url": "https://example.com/already-there"}),
                json.dumps({"url": "https://example.com/already-there"}),
            ]
        ),
        encoding="utf-8",
    )
    existing_root = tmp_path / "raw"
    existing_root.mkdir(parents=True, exist_ok=True)
    _fake_packet(existing_root / "existing.md", canonical_url="https://example.com/already-there", verdict="AUTO_PASS")

    calls: list[str] = []

    def fake_intake_url(url, *, raw_dir, review_dir, archive_dir, **kwargs):
        calls.append(url)
        destination_root = review_dir
        destination_root.mkdir(parents=True, exist_ok=True)
        return _fake_packet(destination_root / "should-not-run.md", canonical_url=url, verdict="REVIEW_REQUIRED")

    monkeypatch.setattr(module, "intake_url", fake_intake_url)

    result = module.drain_queue(
        raw_dir=tmp_path / "raw",
        review_dir=tmp_path / "review",
        archive_dir=tmp_path / "archive",
        queue_path=queue_path,
    )

    assert result == "[SILENT]"
    assert calls == []
