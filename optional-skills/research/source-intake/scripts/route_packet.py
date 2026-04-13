"""Route a packet into raw or review destinations."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from cliper.markdown import read_markdown_document, write_markdown_document  # noqa: E402
from cliper.models import SourcePacketRecord  # noqa: E402
from cliper.service import slugify  # noqa: E402

ALLOWED_VERDICTS = {"AUTO_PASS", "REVIEW_REQUIRED", "LOW_SIGNAL", "UNSUPPORTED"}


def _find_existing_packet(destinations: list[Path], canonical_url: str) -> Path | None:
    for destination in destinations:
        if not destination.exists():
            continue
        for path in destination.rglob("*.md"):
            try:
                metadata, _ = read_markdown_document(path)
            except Exception:
                continue
            if metadata.get("canonical_url") == canonical_url:
                return path
    return None


def _destination_for_verdict(verdict: str, raw_root: Path, review_root: Path) -> Path:
    if verdict not in ALLOWED_VERDICTS:
        raise ValueError(f"unsupported verifier verdict: {verdict}")
    if verdict == "AUTO_PASS":
        return raw_root
    if verdict == "REVIEW_REQUIRED":
        return review_root
    if verdict == "LOW_SIGNAL":
        return review_root
    if verdict == "UNSUPPORTED":
        return review_root
    raise ValueError(f"unsupported verifier verdict: {verdict}")


def collect_canonical_urls(*destinations: Path) -> set[str]:
    canonical_urls: set[str] = set()
    for destination in destinations:
        if not destination.exists():
            continue
        for path in destination.rglob("*.md"):
            try:
                metadata, _ = read_markdown_document(path)
            except Exception:
                continue
            canonical_url = metadata.get("canonical_url")
            if isinstance(canonical_url, str) and canonical_url:
                canonical_urls.add(canonical_url)
    return canonical_urls


def route_packet(record: SourcePacketRecord, body: str, raw_dir: Path, review_dir: Path) -> Path:
    raw_root = raw_dir.expanduser().resolve()
    review_root = review_dir.expanduser().resolve()
    existing = _find_existing_packet([raw_root, review_root], record.canonical_url)
    if existing:
        return existing

    destination_root = _destination_for_verdict(record.verdict, raw_root, review_root)
    destination_root.mkdir(parents=True, exist_ok=True)
    slug = slugify(record.title or record.packet_id)
    destination = destination_root / f"{record.packet_id}--{slug}.md"
    write_markdown_document(destination, record.model_dump(mode="json", by_alias=True), body)
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description="Route a source-packet to raw or review.")
    parser.add_argument("packet_path", help="Path to a packet markdown file")
    parser.add_argument("--raw-dir", required=True)
    parser.add_argument("--review-dir", required=True)
    args = parser.parse_args()

    metadata, body = read_markdown_document(Path(args.packet_path))
    record = SourcePacketRecord.model_validate(metadata)
    destination = route_packet(record, body, Path(args.raw_dir), Path(args.review_dir))
    print(destination)


if __name__ == "__main__":
    main()
