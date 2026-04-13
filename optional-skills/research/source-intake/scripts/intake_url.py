"""Main source-intake orchestration entrypoint.

Pipeline order:
1. classify the URL
2. pick the backend
3. normalize into a source-packet
4. verify packet quality
5. route the packet
"""

from __future__ import annotations

import argparse
import re
import sys
from hashlib import sha256
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from cliper.adapters.web_url import canonicalize_url, dedupe_key_for_url  # noqa: E402

from classify_url import classify_url  # noqa: E402
from normalize_packet import build_source_packet  # noqa: E402
from route_packet import route_packet  # noqa: E402
from run_firecrawl_backend import FirecrawlBackendError, run_firecrawl_backend  # noqa: E402
from run_mineru_backend import MinerUBackendError, run_mineru_backend  # noqa: E402
from run_native_backend import run_native_backend  # noqa: E402
from verify_packet import verify_packet  # noqa: E402

JS_HEAVY_MARKERS = (
    "__next_data__",
    "data-reactroot",
    "window.__nuxt__",
    "webpackjsonp",
    "hydration",
)
NOISE_MARKERS = (
    "cookie",
    "subscribe",
    "sign up",
    "navigation",
    "table of contents",
    "breadcrumbs",
)
MINERU_ESCALATION_REASON_CODES = {
    "firecrawl_pdf_too_weak",
    "firecrawl_pdf_scan_heavy",
    "firecrawl_pdf_multi_column",
    "firecrawl_pdf_table_heavy",
    "firecrawl_pdf_formula_heavy",
}


def _build_github_placeholder_payload(url: str) -> dict[str, object]:
    canonical_url = canonicalize_url(url)
    body_markdown = "\n".join(
        [
            "# GitHub Placeholder",
            "",
            "This GitHub URL is intentionally deferred in v1.",
            "",
            "No repository crawling, cloning, README extraction, code ingestion, or wiki generation was attempted.",
            "",
            "## Deferred Scope",
            "- repository crawling",
            "- blob or README extraction",
            "- issue or PR ingestion",
            "- wiki or output generation",
        ]
    ).strip()
    return {
        "canonical_url": canonical_url,
        "resolved_url": canonical_url,
        "title": "GitHub placeholder",
        "language": "unknown",
        "published_at": None,
        "body_markdown": body_markdown,
        "content_hash": sha256(body_markdown.encode("utf-8")).hexdigest(),
        "dedupe_key": dedupe_key_for_url(canonical_url),
        "raw_html": "",
        "backend_used": "github_placeholder",
        "backend_version": "v1",
        "verifier_summary": "GitHub ingestion is intentionally unsupported in v1. The verifier remains a routing gate only.",
        "provenance": {
            "fetch_method": "github_placeholder",
            "fetch_url": url,
            "resolved_url": canonical_url,
            "extractor": "github-placeholder",
            "extractor_version": "v1",
        },
    }


def _build_failure_payload(
    url: str,
    reason_codes: list[str],
    *,
    backend_used: str = "firecrawl",
    backend_version: str = "fallback",
    title: str = "Source intake needs review",
) -> dict[str, object]:
    canonical_url = canonicalize_url(url)
    body_markdown = "\n".join(
        [
            f"# {title}",
            "",
            "The configured intake backends did not produce a trusted extraction.",
            "",
            "## Reason Codes",
            *[f"- {code}" for code in reason_codes],
        ]
    ).strip()
    return {
        "canonical_url": canonical_url,
        "resolved_url": canonical_url,
        "title": title,
        "language": "unknown",
        "published_at": None,
        "body_markdown": body_markdown,
        "content_hash": sha256(body_markdown.encode("utf-8")).hexdigest(),
        "dedupe_key": dedupe_key_for_url(canonical_url),
        "raw_html": "",
        "backend_used": backend_used,
        "backend_version": backend_version,
    }


def _native_fallback_reasons(source_type: str, backend_payload: dict[str, object]) -> list[str]:
    body = str(backend_payload.get("body_markdown", "")).strip()
    raw_html = str(backend_payload.get("raw_html", "")).lower()
    headings = len(re.findall(r"(?m)^#{1,3}\s+\S", body))
    words = re.findall(r"\w+", body.lower())
    word_count = len(words)
    reason_codes: list[str] = []

    if len(body) < 250:
        reason_codes.append("native_too_short")
    if source_type in {"docs_page", "paper_page"} and headings < 2:
        reason_codes.append("native_heading_structure_incomplete")
    if word_count:
        noise_hits = sum(body.lower().count(marker) for marker in NOISE_MARKERS)
        if noise_hits / max(word_count, 1) >= 0.04:
            reason_codes.append("native_noise_ratio_high")
    if len(body) < 400 and any(marker in raw_html for marker in JS_HEAVY_MARKERS):
        reason_codes.append("native_js_heavy_page")

    return list(dict.fromkeys(reason_codes))


def _should_use_mineru(source_type: str, reason_codes: list[str]) -> bool:
    return source_type == "pdf_url" or bool(MINERU_ESCALATION_REASON_CODES.intersection(reason_codes))


def intake_url(
    url: str,
    *,
    raw_dir: Path,
    review_dir: Path,
    archive_dir: Path,
    verdict: str | None = None,
    confidence: float | None = None,
    signal_level: str | None = None,
    reason_codes: list[str] | None = None,
    suggested_topic: str | None = None,
    suggested_kind: str | None = None,
) -> Path:
    source_type = classify_url(url)

    effective_verdict = verdict
    effective_confidence = confidence
    effective_signal_level = signal_level
    effective_reason_codes = list(reason_codes or [])

    if source_type == "github_repo":
        if "github_placeholder" not in effective_reason_codes:
            effective_reason_codes.append("github_placeholder")
        if "github_v1_deferred" not in effective_reason_codes:
            effective_reason_codes.append("github_v1_deferred")
        backend_payload = _build_github_placeholder_payload(url)
        effective_verdict = "UNSUPPORTED"
        effective_confidence = 0.1 if effective_confidence is None else min(effective_confidence, 0.1)
        effective_signal_level = "low"
    elif _should_use_mineru(source_type, effective_reason_codes):
        if source_type == "pdf_url" and "pdf_direct_to_mineru" not in effective_reason_codes:
            effective_reason_codes.append("pdf_direct_to_mineru")
        try:
            backend_payload = run_mineru_backend(url)
            effective_reason_codes.extend(backend_payload.get("reason_codes", []))
        except MinerUBackendError as exc:
            effective_reason_codes.extend(exc.reason_codes)
            effective_reason_codes = list(dict.fromkeys(effective_reason_codes))
            effective_verdict = "UNSUPPORTED"
            effective_confidence = min(confidence, 0.15) if confidence else 0.15
            effective_signal_level = "low"
            backend_payload = _build_failure_payload(
                url,
                effective_reason_codes,
                backend_used="mineru",
                backend_version="mineru",
                title="PDF intake unsupported",
            )
        else:
            effective_reason_codes = list(dict.fromkeys(effective_reason_codes))
    else:
        try:
            native_payload = run_native_backend(url)
        except Exception:
            native_payload = None
            firecrawl_trigger_codes = ["native_fetch_failed"]
        else:
            firecrawl_trigger_codes = _native_fallback_reasons(source_type, native_payload)

        if firecrawl_trigger_codes:
            try:
                backend_payload = run_firecrawl_backend(url)
                effective_reason_codes.extend(firecrawl_trigger_codes)
                effective_reason_codes.extend(backend_payload.get("reason_codes", []))
                if _should_use_mineru(source_type, effective_reason_codes):
                    backend_payload = run_mineru_backend(url)
                    effective_reason_codes.extend(backend_payload.get("reason_codes", []))
            except FirecrawlBackendError as exc:
                effective_reason_codes.extend(firecrawl_trigger_codes)
                effective_reason_codes.extend(exc.reason_codes)
                effective_verdict = "REVIEW_REQUIRED"
                effective_confidence = min(confidence, 0.25) if confidence else 0.25
                effective_signal_level = "low"
                backend_payload = native_payload or _build_failure_payload(url, effective_reason_codes)
            except MinerUBackendError as exc:
                effective_reason_codes.extend(exc.reason_codes)
                effective_verdict = "UNSUPPORTED"
                effective_confidence = min(confidence, 0.15) if confidence else 0.15
                effective_signal_level = "low"
                backend_payload = _build_failure_payload(
                    url,
                    effective_reason_codes,
                    backend_used="mineru",
                    backend_version="mineru",
                    title="PDF intake unsupported",
                )
            effective_reason_codes = list(dict.fromkeys(effective_reason_codes))
        else:
            backend_payload = native_payload

    verification = verify_packet(
        source_type=source_type,
        backend_payload=backend_payload,
        reason_codes=effective_reason_codes,
        suggested_topic=suggested_topic,
        suggested_kind=suggested_kind,
    )
    effective_verdict = effective_verdict or verification.verdict
    effective_confidence = effective_confidence if effective_confidence is not None else verification.confidence
    effective_signal_level = effective_signal_level or verification.signal_level
    effective_reason_codes = list(dict.fromkeys(verification.reason_codes))
    suggested_topic = suggested_topic or verification.suggested_topic
    suggested_kind = suggested_kind or verification.suggested_kind

    record, body = build_source_packet(
        source_type=source_type,
        input_url=url,
        backend_payload=backend_payload,
        archive_dir=archive_dir,
        verdict=effective_verdict,
        confidence=effective_confidence,
        signal_level=effective_signal_level,
        reason_codes=effective_reason_codes,
        suggested_topic=suggested_topic,
        suggested_kind=suggested_kind,
    )
    return route_packet(record, body, raw_dir, review_dir)


def main() -> None:
    """Run the source-intake path with backend selection plus verifier routing."""
    parser = argparse.ArgumentParser(description="Run the source-intake path.")
    parser.add_argument("url", help="URL to intake")
    parser.add_argument("--raw-dir", required=True)
    parser.add_argument("--review-dir", required=True)
    parser.add_argument("--archive-dir", required=True)
    parser.add_argument("--verdict")
    parser.add_argument("--confidence", type=float)
    parser.add_argument("--signal-level")
    parser.add_argument("--reason-code", action="append", default=[])
    parser.add_argument("--suggested-topic")
    parser.add_argument("--suggested-kind")
    args = parser.parse_args()
    destination = intake_url(
        args.url,
        raw_dir=Path(args.raw_dir),
        review_dir=Path(args.review_dir),
        archive_dir=Path(args.archive_dir),
        verdict=args.verdict,
        confidence=args.confidence,
        signal_level=args.signal_level,
        reason_codes=args.reason_code,
        suggested_topic=args.suggested_topic,
        suggested_kind=args.suggested_kind,
    )
    print(destination)


if __name__ == "__main__":
    main()
