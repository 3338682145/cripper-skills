"""Evaluate packet quality and assign a routing verdict."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from cliper.models import VerifierResult  # noqa: E402

UNSUPPORTED_REASON_CODES = {
    "github_placeholder",
    "mineru_missing_endpoint",
    "mineru_request_failed",
    "mineru_invalid_response",
    "mineru_empty_content",
    "mineru_cli_failed",
}
REVIEW_REASON_CODES = {
    "native_fetch_failed",
    "firecrawl_missing_api_key",
    "firecrawl_unauthorized",
    "firecrawl_rate_limited",
    "firecrawl_request_failed",
    "firecrawl_invalid_response",
    "firecrawl_empty_content",
    "native_heading_structure_incomplete",
    "native_noise_ratio_high",
    "native_js_heavy_page",
}


def _default_kind(source_type: str) -> str | None:
    mapping = {
        "docs_page": "docs",
        "blog_article": "blog",
        "paper_page": "paper",
        "pdf_url": "reference",
    }
    return mapping.get(source_type)


def _default_topic(title: str | None, source_type: str) -> str | None:
    if title:
        words = re.findall(r"[A-Za-z0-9]+", title.lower())
        if words:
            return "-".join(words[:6])
    kind = _default_kind(source_type)
    return f"{kind}-source" if kind else None


def verify_packet(
    *,
    source_type: str,
    backend_payload: dict[str, Any],
    reason_codes: list[str] | None = None,
    suggested_topic: str | None = None,
    suggested_kind: str | None = None,
) -> VerifierResult:
    """Return only routing metadata. This verifier does not generate wiki or output content."""

    effective_reason_codes = list(dict.fromkeys(reason_codes or []))
    body = str(backend_payload.get("body_markdown", "")).strip()
    title = backend_payload.get("title")
    word_count = len(re.findall(r"\w+", body))
    headings = len(re.findall(r"(?m)^#{1,3}\s+\S", body))
    backend_used = str(backend_payload.get("backend_used", "native"))

    if source_type == "github_repo" or backend_used == "github_placeholder":
        if "github_placeholder" not in effective_reason_codes:
            effective_reason_codes.append("github_placeholder")
        return VerifierResult(
            verdict="UNSUPPORTED",
            confidence=0.1,
            signal_level="low",
            reason_codes=effective_reason_codes,
            summary="Unsupported source type for v1 intake. The verifier only gates routing and does not generate wiki or output content.",
            suggested_topic=suggested_topic or _default_topic(title, source_type),
            suggested_kind=suggested_kind or _default_kind(source_type),
        )

    if any(code in UNSUPPORTED_REASON_CODES for code in effective_reason_codes):
        return VerifierResult(
            verdict="UNSUPPORTED",
            confidence=0.15,
            signal_level="low",
            reason_codes=effective_reason_codes,
            summary="Backend support is unavailable or failed for this source. The verifier remains a quality gate only.",
            suggested_topic=suggested_topic or _default_topic(title, source_type),
            suggested_kind=suggested_kind or _default_kind(source_type),
        )

    if not body or word_count < 30:
        if "verifier_low_word_count" not in effective_reason_codes:
            effective_reason_codes.append("verifier_low_word_count")
        return VerifierResult(
            verdict="LOW_SIGNAL",
            confidence=0.2,
            signal_level="low",
            reason_codes=effective_reason_codes,
            summary="Extracted content is too thin to trust for automatic intake. The verifier does not write wiki or output content.",
            suggested_topic=suggested_topic or _default_topic(title, source_type),
            suggested_kind=suggested_kind or _default_kind(source_type),
        )

    if any(code in REVIEW_REASON_CODES for code in effective_reason_codes):
        return VerifierResult(
            verdict="REVIEW_REQUIRED",
            confidence=0.45,
            signal_level="medium" if word_count >= 120 else "low",
            reason_codes=effective_reason_codes,
            summary="The source is usable but quality or backend confidence needs review. The verifier is scoped to routing, not summarization.",
            suggested_topic=suggested_topic or _default_topic(title, source_type),
            suggested_kind=suggested_kind or _default_kind(source_type),
        )

    if word_count >= 180 and headings >= 2:
        if "verifier_structured_content" not in effective_reason_codes:
            effective_reason_codes.append("verifier_structured_content")
        return VerifierResult(
            verdict="AUTO_PASS",
            confidence=0.92,
            signal_level="high",
            reason_codes=effective_reason_codes,
            summary="Content is complete and structurally usable for automatic intake. The verifier only returns gating metadata.",
            suggested_topic=suggested_topic or _default_topic(title, source_type),
            suggested_kind=suggested_kind or _default_kind(source_type),
        )

    if word_count >= 80:
        if "verifier_manual_review" not in effective_reason_codes:
            effective_reason_codes.append("verifier_manual_review")
        return VerifierResult(
            verdict="REVIEW_REQUIRED",
            confidence=0.6,
            signal_level="medium",
            reason_codes=effective_reason_codes,
            summary="Content is mostly usable but does not meet automatic-pass confidence. The verifier does not generate downstream content.",
            suggested_topic=suggested_topic or _default_topic(title, source_type),
            suggested_kind=suggested_kind or _default_kind(source_type),
        )

    if "verifier_low_signal_content" not in effective_reason_codes:
        effective_reason_codes.append("verifier_low_signal_content")
    return VerifierResult(
        verdict="LOW_SIGNAL",
        confidence=0.35,
        signal_level="low",
        reason_codes=effective_reason_codes,
        summary="Content is present but not strong enough for reliable automatic intake. The verifier is limited to gating.",
        suggested_topic=suggested_topic or _default_topic(title, source_type),
        suggested_kind=suggested_kind or _default_kind(source_type),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate packet quality and assign a routing verdict.")
    parser.add_argument("payload_json", help="Path to a backend payload JSON file")
    parser.add_argument("--source-type", required=True)
    parser.add_argument("--reason-code", action="append", default=[])
    parser.add_argument("--suggested-topic")
    parser.add_argument("--suggested-kind")
    args = parser.parse_args()

    payload = json.loads(Path(args.payload_json).read_text(encoding="utf-8"))
    verdict = verify_packet(
        source_type=args.source_type,
        backend_payload=payload,
        reason_codes=args.reason_code,
        suggested_topic=args.suggested_topic,
        suggested_kind=args.suggested_kind,
    )
    print(json.dumps(verdict.model_dump(mode="json"), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
