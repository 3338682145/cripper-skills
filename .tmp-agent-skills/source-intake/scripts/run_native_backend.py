"""Run the native Cliper backend for supported web sources."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from cliper import __version__  # noqa: E402
from cliper.adapters.web_url import fetch_document  # noqa: E402


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
