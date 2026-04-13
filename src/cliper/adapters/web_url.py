from __future__ import annotations

import hashlib
import html
import re
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup, Tag
from markdownify import MarkdownConverter
from readability import Document

DOCS_PRIMARY_SELECTORS = [
    "main article",
    "article",
    "main",
    '[role="main"]',
    ".theme-doc-markdown",
    ".markdown",
    ".mdx-content",
    ".docs-content",
    ".content",
    ".prose",
]

NOISE_SELECTORS = [
    "nav",
    "aside",
    "header",
    "footer",
    ".toc",
    ".table-of-contents",
    ".sidebar",
    ".breadcrumbs",
    ".pagination-nav",
    ".theme-doc-toc-desktop",
    ".theme-doc-sidebar-container",
    ".theme-doc-breadcrumbs",
    ".table-of-contents__left-border",
]

TITLE_RE = re.compile(r"(?is)<title[^>]*>(.*?)</title>")
LANG_RE = re.compile(r'(?is)<html[^>]+lang=["\']([^"\']+)["\']')
PUBLISHED_RE = re.compile(
    r'(?is)<meta[^>]+(?:property|name)=["\'](?:article:published_time|pubdate|date)["\'][^>]+content=["\']([^"\']+)["\']'
)


@dataclass
class FetchedDocument:
    canonical_url: str
    resolved_url: str
    title: str | None
    language: str
    published_at: str | None
    body_markdown: str
    content_hash: str
    dedupe_key: str
    raw_html: str


class ObsidianMarkdownConverter(MarkdownConverter):
    def convert_pre(self, el, text, parent_tags) -> str:  # type: ignore[override]
        code_element = el.find("code")
        code_text = code_element.get_text() if code_element else el.get_text()
        language = ""
        if code_element:
            for css_class in code_element.get("class", []):
                if css_class.startswith("language-"):
                    language = css_class.removeprefix("language-")
                    break
        code_text = code_text.rstrip("\n")
        return f"\n```{language}\n{code_text}\n```\n\n"


def canonicalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    query = urlencode(sorted(parse_qsl(parts.query, keep_blank_values=True)))
    path = parts.path or "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, query, ""))


def dedupe_key_for_url(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def _extract_page_metadata(text: str) -> tuple[str | None, str | None, str | None]:
    title_match = TITLE_RE.search(text)
    language_match = LANG_RE.search(text)
    published_match = PUBLISHED_RE.search(text)
    title = html.unescape(title_match.group(1)).strip() if title_match else None
    language = language_match.group(1) if language_match else None
    published_at = published_match.group(1) if published_match else None
    return title, language, published_at


def _clone_fragment(tag: Tag) -> Tag:
    fragment = BeautifulSoup(str(tag), "lxml")
    if fragment.body and len(fragment.body.contents) == 1 and isinstance(fragment.body.contents[0], Tag):
        return fragment.body.contents[0]
    if fragment.body:
        return fragment.body
    return fragment


def _strip_noise(root: Tag) -> None:
    for selector in NOISE_SELECTORS:
        for node in root.select(selector):
            node.decompose()
    for node in root.select("[aria-hidden='true']"):
        node.decompose()
    for node in root.find_all(["button"]):
        node.decompose()


def _content_score(tag: Tag) -> int:
    text_len = len(tag.get_text(" ", strip=True))
    headings = len(tag.select("h1, h2, h3"))
    blocks = len(tag.select("p, li, pre, table"))
    return text_len + headings * 400 + blocks * 120


def _iter_candidates(soup: BeautifulSoup) -> Iterable[Tag]:
    seen: set[int] = set()
    for selector in DOCS_PRIMARY_SELECTORS:
        for node in soup.select(selector):
            node_id = id(node)
            if node_id in seen or not isinstance(node, Tag):
                continue
            seen.add(node_id)
            yield node


def _choose_docs_fragment(soup: BeautifulSoup) -> Tag | None:
    best_fragment: Tag | None = None
    best_score = 0
    for candidate in _iter_candidates(soup):
        fragment = _clone_fragment(candidate)
        _strip_noise(fragment)
        score = _content_score(fragment)
        if score > best_score:
            best_score = score
            best_fragment = fragment
    return best_fragment


def _has_sufficient_structure(fragment: Tag | None) -> bool:
    if fragment is None:
        return False
    text_len = len(fragment.get_text(" ", strip=True))
    headings = len(fragment.select("h1, h2, h3"))
    blocks = len(fragment.select("p, li, pre, table"))
    return text_len >= 800 or (headings >= 3 and blocks >= 8)


def _readability_fragment(text: str) -> Tag:
    document = Document(text)
    summary_html = document.summary(html_partial=True)
    fragment = BeautifulSoup(summary_html, "lxml")
    if fragment.body and len(fragment.body.contents) == 1 and isinstance(fragment.body.contents[0], Tag):
        root = fragment.body.contents[0]
    elif fragment.body:
        root = fragment.body
    else:
        root = fragment
    _strip_noise(root)
    return root


def _markdownify(fragment: Tag) -> str:
    converter = ObsidianMarkdownConverter(
        heading_style="ATX",
        bullets="-",
        escape_asterisks=False,
        escape_underscores=False,
        code_language_callback=lambda el: "",
    )
    markdown = converter.convert_soup(fragment)
    markdown = markdown.replace("\r\n", "\n")
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    markdown = re.sub(r"[ \t]+\n", "\n", markdown)
    return markdown.strip()


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().lower()


def _has_markdown_h1(markdown: str) -> bool:
    return bool(re.search(r"(?m)^#\s+.+$", markdown))


def _ensure_page_title(markdown: str, page_title: str | None, *, fragment_has_h1: bool) -> str:
    if not markdown or not page_title:
        return markdown
    if fragment_has_h1 or _has_markdown_h1(markdown):
        return markdown
    return f"# {page_title.strip()}\n\n{markdown}".strip()


def _dedupe_leading_title(markdown: str, page_title: str | None) -> str:
    if not markdown:
        return markdown
    if not page_title:
        return markdown
    lines = markdown.splitlines()
    if len(lines) >= 3 and lines[0].startswith("# "):
        normalized_heading = _normalize_text(lines[0][2:])
        normalized_title = _normalize_text(page_title)
        if normalized_heading == normalized_title:
            remaining = "\n".join(lines[1:]).lstrip()
            return f"{lines[0]}\n\n{remaining}".strip()
    return markdown


def extract_document(text: str, *, source_url: str, resolved_url: str | None = None) -> FetchedDocument:
    title, language, published_at = _extract_page_metadata(text)
    soup = BeautifulSoup(text, "lxml")
    docs_fragment = _choose_docs_fragment(soup)
    fragment = docs_fragment if _has_sufficient_structure(docs_fragment) else _readability_fragment(text)
    body_markdown = _markdownify(fragment)
    body_markdown = _ensure_page_title(body_markdown, title, fragment_has_h1=bool(fragment.select_one("h1")))
    body_markdown = _dedupe_leading_title(body_markdown, title)
    if not body_markdown:
        raise ValueError("no extractable text found")
    canonical_url = canonicalize_url(resolved_url or source_url)
    content_hash = hashlib.sha256(body_markdown.encode("utf-8")).hexdigest()
    return FetchedDocument(
        canonical_url=canonical_url,
        resolved_url=resolved_url or source_url,
        title=title,
        language=language or "unknown",
        published_at=published_at,
        body_markdown=body_markdown,
        content_hash=content_hash,
        dedupe_key=dedupe_key_for_url(canonical_url),
        raw_html=text,
    )


def fetch_document(url: str, *, timeout: int = 20, session: requests.Session | None = None) -> FetchedDocument:
    current_session = session or requests.Session()
    response = current_session.get(url, timeout=timeout, headers={"User-Agent": "cliper/0.1"})
    response.raise_for_status()
    response.encoding = response.encoding or "utf-8"
    return extract_document(response.text, source_url=url, resolved_url=response.url or url)
