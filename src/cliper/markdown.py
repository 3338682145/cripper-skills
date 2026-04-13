from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

FRONTMATTER_RE = re.compile(r"\A---\s*\r?\n(.*?)\r?\n---\s*\r?\n?(.*)\Z", re.DOTALL)


def parse_markdown_document(text: str) -> tuple[dict[str, Any], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError("missing YAML frontmatter")
    metadata = yaml.safe_load(match.group(1)) or {}
    if not isinstance(metadata, dict):
        raise ValueError("frontmatter must decode to a mapping")
    return metadata, match.group(2).strip()


def read_markdown_document(path: Path) -> tuple[dict[str, Any], str]:
    return parse_markdown_document(path.read_text(encoding="utf-8"))


def dump_markdown_document(metadata: dict[str, Any], body: str) -> str:
    frontmatter = yaml.safe_dump(metadata, sort_keys=False, allow_unicode=False).strip()
    normalized_body = body.strip()
    return f"---\n{frontmatter}\n---\n\n{normalized_body}\n"


def write_markdown_document(path: Path, metadata: dict[str, Any], body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_markdown_document(metadata, body), encoding="utf-8")
