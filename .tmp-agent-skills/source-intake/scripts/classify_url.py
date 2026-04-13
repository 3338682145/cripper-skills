"""Classify a URL into one of the supported source types."""

from __future__ import annotations

import argparse
from urllib.parse import urlsplit


def _is_github_input(host: str, path: str) -> bool:
    if not host.endswith("github.com"):
        return False
    if path in {"", "/"}:
        return False
    return True


def classify_url(url: str) -> str:
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    path = parts.path.lower()

    if _is_github_input(host, path):
        return "github_repo"
    if path.endswith(".pdf"):
        return "pdf_url"
    if any(token in host for token in ("arxiv.org", "openreview.net", "doi.org")) or "/paper" in path:
        return "paper_page"
    if any(token in host for token in ("docs.", "doc.")) or any(
        token in path for token in ("/docs", "/doc", "/reference", "/manual", "/api/")
    ):
        return "docs_page"
    if any(token in path for token in ("/blog", "/blogs", "/post", "/posts", "/article", "/articles")):
        return "blog_article"
    return "unknown"


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify a URL for source-intake.")
    parser.add_argument("url", help="URL to classify")
    args = parser.parse_args()
    print(classify_url(args.url))


if __name__ == "__main__":
    main()
