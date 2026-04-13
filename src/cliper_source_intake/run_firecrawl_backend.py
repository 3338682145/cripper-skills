"""Run the Firecrawl fallback backend for difficult web pages."""

from __future__ import annotations

import argparse
import json
import os
from hashlib import sha256
from typing import Any

import requests

from cliper.adapters.web_url import canonicalize_url, dedupe_key_for_url

FIRECRAWL_API_URL = "https://api.firecrawl.dev/v2/scrape"


class FirecrawlBackendError(RuntimeError):
    def __init__(self, message: str, *, reason_codes: list[str], status_code: int | None = None) -> None:
        super().__init__(message)
        self.reason_codes = reason_codes
        self.status_code = status_code


def _extract_markdown(data: dict[str, Any]) -> str:
    for key in ("markdown", "content"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise FirecrawlBackendError(
        "Firecrawl returned empty content.",
        reason_codes=["firecrawl_empty_content"],
    )


def run_firecrawl_backend(
    url: str,
    *,
    api_key: str | None = None,
    timeout: int = 30,
) -> dict[str, Any]:
    token = api_key or os.getenv("FIRECRAWL_API_KEY")
    if not token:
        raise FirecrawlBackendError(
            "Missing FIRECRAWL_API_KEY for Firecrawl fallback.",
            reason_codes=["firecrawl_missing_api_key"],
        )

    payload = {
        "url": url,
        "formats": ["markdown", "rawHtml"],
        "onlyMainContent": True,
        "timeout": timeout * 1000,
    }
    response = requests.post(
        FIRECRAWL_API_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=timeout,
    )
    if response.status_code >= 400:
        try:
            error_payload = response.json()
        except ValueError:
            error_payload = {}
        message = error_payload.get("error") or error_payload.get("message") or response.text or "Firecrawl request failed."
        reason_codes = ["firecrawl_request_failed"]
        if response.status_code == 401:
            reason_codes = ["firecrawl_unauthorized"]
        elif response.status_code == 429:
            reason_codes = ["firecrawl_rate_limited"]
        raise FirecrawlBackendError(message, reason_codes=reason_codes, status_code=response.status_code)

    try:
        response_payload = response.json()
    except ValueError as exc:
        raise FirecrawlBackendError(
            f"Firecrawl returned invalid JSON: {exc}",
            reason_codes=["firecrawl_invalid_response"],
        ) from exc

    data = response_payload.get("data") if isinstance(response_payload.get("data"), dict) else response_payload
    if not isinstance(data, dict):
        raise FirecrawlBackendError(
            "Firecrawl response payload is missing data.",
            reason_codes=["firecrawl_invalid_response"],
        )

    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    markdown = _extract_markdown(data)
    canonical_url = canonicalize_url(
        metadata.get("sourceURL")
        or metadata.get("url")
        or metadata.get("resolvedUrl")
        or url
    )
    raw_html = data.get("rawHtml") or data.get("html") or ""
    title = metadata.get("title")
    language = metadata.get("language") or "unknown"
    published_at = metadata.get("publishedTime") or metadata.get("published_at")
    backend_version = response_payload.get("version") or "firecrawl-v2"

    return {
        "canonical_url": canonical_url,
        "resolved_url": metadata.get("sourceURL") or metadata.get("url") or canonical_url,
        "title": title,
        "language": language,
        "published_at": published_at,
        "body_markdown": markdown,
        "content_hash": sha256(markdown.encode("utf-8")).hexdigest(),
        "dedupe_key": dedupe_key_for_url(canonical_url),
        "raw_html": raw_html,
        "backend_used": "firecrawl",
        "backend_version": str(backend_version),
        "reason_codes": ["firecrawl_fallback_used"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Firecrawl fallback backend.")
    parser.add_argument("url", help="URL to fetch through Firecrawl")
    args = parser.parse_args()
    print(json.dumps(run_firecrawl_backend(args.url), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
