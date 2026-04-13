"""Run the native Cliper backend for supported web sources."""

from __future__ import annotations

import argparse
import json
from typing import Any

from cliper import __version__
from cliper.adapters.web_url import fetch_document


def run_native_backend(url: str) -> dict[str, Any]:
    document = fetch_document(url)
    return {
        "canonical_url": document.canonical_url,
        "resolved_url": document.resolved_url,
        "title": document.title,
        "language": document.language,
        "published_at": document.published_at,
        "body_markdown": document.body_markdown,
        "content_hash": document.content_hash,
        "dedupe_key": document.dedupe_key,
        "raw_html": document.raw_html,
        "backend_used": "native",
        "backend_version": __version__,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the native Cliper backend.")
    parser.add_argument("url", help="URL to fetch through the native backend")
    args = parser.parse_args()
    print(json.dumps(run_native_backend(args.url), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
