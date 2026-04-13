"""Normalize backend output into the source-packet contract."""

from __future__ import annotations

import argparse
import json
import sys
from hashlib import sha256
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from cliper.markdown import dump_markdown_document  # noqa: E402
from cliper.models import Provenance, SourcePacketRecord, SourcePacketRefs, SourcePacketRouting  # noqa: E402
from cliper.service import utc_now  # noqa: E402


def build_source_packet(
    *,
    source_type: str,
    input_url: str,
    backend_payload: dict[str, Any],
    archive_dir: Path,
    verdict: str = "REVIEW_REQUIRED",
    confidence: float = 0.0,
    signal_level: str = "medium",
    reason_codes: list[str] | None = None,
    suggested_topic: str | None = None,
    suggested_kind: str | None = None,
) -> tuple[SourcePacketRecord, str]:
    archive_root = archive_dir.expanduser().resolve()
    packet_id = sha256(f"{source_type}|{backend_payload['canonical_url']}".encode("utf-8")).hexdigest()[:16]
    packet_archive_dir = archive_root / packet_id
    packet_archive_dir.mkdir(parents=True, exist_ok=True)

    artifact_files = backend_payload.get("artifact_files") or {}

    raw_html_path: Path | None = None
    raw_html = backend_payload.get("raw_html")
    if isinstance(raw_html, str) and raw_html.strip():
        raw_html_path = packet_archive_dir / "source.html"
        raw_html_path.write_text(raw_html, encoding="utf-8")

    raw_pdf_path: Path | None = None
    raw_pdf = artifact_files.get("raw_pdf")
    if raw_pdf is not None:
        raw_pdf_path = packet_archive_dir / "source.pdf"
        if isinstance(raw_pdf, bytes):
            raw_pdf_path.write_bytes(raw_pdf)
        else:
            raw_pdf_path.write_bytes(str(raw_pdf).encode("utf-8"))

    extracted_json_path: Path | None = None
    extracted_json = artifact_files.get("extracted_json")
    if extracted_json is not None:
        extracted_json_path = packet_archive_dir / "extracted.json"
        if isinstance(extracted_json, str):
            extracted_json_path.write_text(extracted_json, encoding="utf-8")
        else:
            extracted_json_path.write_text(json.dumps(extracted_json, indent=2), encoding="utf-8")

    source_snapshot_path: Path | None = None
    source_snapshot = artifact_files.get("source_snapshot")
    if source_snapshot is not None:
        source_snapshot_path = packet_archive_dir / "source-snapshot.md"
        source_snapshot_path.write_text(str(source_snapshot), encoding="utf-8")

    verifier_report_path = packet_archive_dir / "verifier-report.json"
    verifier_payload = {
        "verdict": verdict,
        "confidence": confidence,
        "signal_level": signal_level,
        "reason_codes": reason_codes or [],
        "summary": backend_payload.get("verifier_summary", "Source-intake verifier routing result."),
        "suggested_topic": suggested_topic,
        "suggested_kind": suggested_kind,
    }
    verifier_report_path.write_text(json.dumps(verifier_payload, indent=2), encoding="utf-8")

    provenance_payload = backend_payload.get("provenance") or {}
    backend_used = backend_payload.get("backend_used", "native")
    backend_version = backend_payload.get("backend_version", "0.0.0")

    record = SourcePacketRecord(
        schema="source-packet",
        schema_version="0.1.0",
        packet_id=packet_id,
        source_type=source_type,
        input_url=input_url,
        canonical_url=backend_payload["canonical_url"],
        title=backend_payload.get("title"),
        retrieved_at=utc_now(),
        published_at=backend_payload.get("published_at"),
        language=backend_payload.get("language") or "unknown",
        backend_used=backend_used,
        backend_version=backend_version,
        content_hash=backend_payload["content_hash"],
        dedupe_key=backend_payload["dedupe_key"],
        signal_level=signal_level,
        verdict=verdict,
        confidence=confidence,
        provenance=Provenance(
            fetch_method=provenance_payload.get("fetch_method", "requests.get"),
            fetch_url=provenance_payload.get("fetch_url", input_url),
            resolved_url=provenance_payload.get("resolved_url", backend_payload.get("resolved_url", backend_payload["canonical_url"])),
            extractor=provenance_payload.get("extractor", f"{backend_used}-wrapper"),
            extractor_version=provenance_payload.get("extractor_version", backend_version),
        ),
        reason_codes=reason_codes or [],
        routing=SourcePacketRouting(
            suggested_topic=suggested_topic,
            suggested_kind=suggested_kind,
        ),
        refs=SourcePacketRefs(
            artifact_dir=str(packet_archive_dir),
            raw_html=str(raw_html_path) if raw_html_path else None,
            raw_pdf=str(raw_pdf_path) if raw_pdf_path else None,
            extracted_json=str(extracted_json_path) if extracted_json_path else None,
            verifier_report=str(verifier_report_path),
            source_snapshot=str(source_snapshot_path or raw_html_path) if (source_snapshot_path or raw_html_path) else None,
        ),
    )
    return record, backend_payload["body_markdown"]


def packet_to_markdown(record: SourcePacketRecord, body: str) -> str:
    return dump_markdown_document(record.model_dump(mode="json", by_alias=True), body)


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize a backend payload into a source-packet.")
    parser.add_argument("payload_json", help="Path to backend payload JSON")
    parser.add_argument("--source-type", required=True)
    parser.add_argument("--input-url", required=True)
    parser.add_argument("--archive-dir", required=True)
    args = parser.parse_args()

    payload = json.loads(Path(args.payload_json).read_text(encoding="utf-8"))
    record, body = build_source_packet(
        source_type=args.source_type,
        input_url=args.input_url,
        backend_payload=payload,
        archive_dir=Path(args.archive_dir),
    )
    print(packet_to_markdown(record, body))


if __name__ == "__main__":
    main()
