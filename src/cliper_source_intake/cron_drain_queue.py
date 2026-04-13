"""Drain queued source-intake work for cron execution."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from cliper.adapters.web_url import canonicalize_url
from cliper.markdown import read_markdown_document

from .intake_url import intake_url
from .route_packet import collect_canonical_urls

DEFAULT_QUEUE_PATH = Path.home() / ".hermes" / "intake" / "queue.jsonl"


def _read_queue(queue_path: Path) -> list[dict[str, Any]]:
    if not queue_path.exists():
        return []
    items: list[dict[str, Any]] = []
    for line in queue_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            payload = json.loads(stripped)
        except ValueError:
            continue
        if isinstance(payload, dict) and isinstance(payload.get("url"), str):
            items.append(payload)
    return items


def drain_queue(
    *,
    raw_dir: Path,
    review_dir: Path,
    archive_dir: Path,
    queue_path: Path = DEFAULT_QUEUE_PATH,
) -> str:
    queue_file = queue_path.expanduser().resolve()
    items = _read_queue(queue_file)
    if not items:
        return "[SILENT]"

    raw_root = raw_dir.expanduser().resolve()
    review_root = review_dir.expanduser().resolve()
    existing_canonical_urls = collect_canonical_urls(raw_root, review_root)
    seen_requested_urls: set[str] = set()
    verdict_counts: Counter[str] = Counter()

    for item in items:
        url = item["url"].strip()
        requested_canonical = canonicalize_url(url)
        if requested_canonical in seen_requested_urls or requested_canonical in existing_canonical_urls:
            continue
        seen_requested_urls.add(requested_canonical)

        destination = intake_url(
            url,
            raw_dir=raw_root,
            review_dir=review_root,
            archive_dir=archive_dir,
            verdict=item.get("verdict"),
            confidence=item.get("confidence"),
            signal_level=item.get("signal_level"),
            reason_codes=item.get("reason_codes"),
            suggested_topic=item.get("suggested_topic"),
            suggested_kind=item.get("suggested_kind"),
        )
        metadata, _ = read_markdown_document(destination)
        canonical_url = metadata.get("canonical_url")
        if not isinstance(canonical_url, str) or not canonical_url:
            continue
        if canonical_url in existing_canonical_urls:
            continue
        existing_canonical_urls.add(canonical_url)
        verdict = metadata.get("verdict")
        if isinstance(verdict, str):
            verdict_counts[verdict] += 1

    if queue_file.exists():
        queue_file.write_text("", encoding="utf-8")

    if not verdict_counts:
        return "[SILENT]"

    ordered_verdicts = ("AUTO_PASS", "REVIEW_REQUIRED", "LOW_SIGNAL", "UNSUPPORTED")
    return " ".join(f"{verdict}={verdict_counts[verdict]}" for verdict in ordered_verdicts if verdict_counts[verdict])


def main() -> None:
    parser = argparse.ArgumentParser(description="Drain queued source-intake work for cron execution.")
    parser.add_argument("--raw-dir", required=True)
    parser.add_argument("--review-dir", required=True)
    parser.add_argument("--archive-dir", required=True)
    parser.add_argument("--queue-path", default=str(DEFAULT_QUEUE_PATH))
    args = parser.parse_args()
    print(
        drain_queue(
            raw_dir=Path(args.raw_dir),
            review_dir=Path(args.review_dir),
            archive_dir=Path(args.archive_dir),
            queue_path=Path(args.queue_path),
        )
    )


if __name__ == "__main__":
    main()
