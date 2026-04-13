"""Run the MinerU backend for PDF and complex documents."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import requests

REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from cliper.adapters.web_url import canonicalize_url, dedupe_key_for_url  # noqa: E402


class MinerUBackendError(RuntimeError):
    def __init__(self, message: str, *, reason_codes: list[str], status_code: int | None = None) -> None:
        super().__init__(message)
        self.reason_codes = reason_codes
        self.status_code = status_code


def _download_pdf(url: str, *, timeout: int) -> bytes:
    response = requests.get(url, timeout=timeout, headers={"User-Agent": "cliper/0.1"})
    response.raise_for_status()
    return response.content


def _find_first(directory: Path, suffix: str) -> Path | None:
    for path in sorted(directory.rglob(f"*{suffix}")):
        if path.is_file():
            return path
    return None


def _payload_from_outputs(
    *,
    url: str,
    pdf_bytes: bytes,
    markdown: str,
    extracted_json: Any,
    raw_pdf_name: str = "source.pdf",
) -> dict[str, Any]:
    canonical_url = canonicalize_url(url)
    return {
        "canonical_url": canonical_url,
        "resolved_url": canonical_url,
        "title": Path(canonical_url).name or "MinerU Document",
        "language": "unknown",
        "published_at": None,
        "body_markdown": markdown,
        "content_hash": sha256(markdown.encode("utf-8")).hexdigest(),
        "dedupe_key": dedupe_key_for_url(canonical_url),
        "raw_html": "",
        "backend_used": "mineru",
        "backend_version": "mineru",
        "reason_codes": ["mineru_backend_used"],
        "provenance": {
            "fetch_method": "mineru",
            "fetch_url": url,
            "resolved_url": canonical_url,
            "extractor": "mineru",
            "extractor_version": "mineru",
        },
        "artifact_files": {
            "raw_pdf": pdf_bytes,
            "extracted_json": extracted_json,
            "source_snapshot": markdown,
        },
        "raw_pdf_name": raw_pdf_name,
    }


def _run_mineru_api(endpoint: str, *, url: str, pdf_bytes: bytes, filename: str, timeout: int) -> dict[str, Any]:
    api_base = endpoint.rstrip("/")
    if not api_base.endswith("/file_parse"):
        api_base = f"{api_base}/file_parse"
    response = requests.post(
        api_base,
        files={"file": (filename, pdf_bytes, "application/pdf")},
        timeout=timeout,
    )
    if response.status_code >= 400:
        raise MinerUBackendError(
            response.text or "MinerU request failed.",
            reason_codes=["mineru_request_failed"],
            status_code=response.status_code,
        )
    try:
        payload = response.json()
    except ValueError as exc:
        raise MinerUBackendError(
            f"MinerU returned invalid JSON: {exc}",
            reason_codes=["mineru_invalid_response"],
        ) from exc

    markdown = payload.get("markdown") or payload.get("md_content") or payload.get("text")
    extracted_json = payload.get("json") or payload.get("content_list") or payload
    if not isinstance(markdown, str) or not markdown.strip():
        raise MinerUBackendError(
            "MinerU returned empty content.",
            reason_codes=["mineru_empty_content"],
        )
    return _payload_from_outputs(url=url, pdf_bytes=pdf_bytes, markdown=markdown.strip(), extracted_json=extracted_json, raw_pdf_name=filename)


def _run_mineru_cli(command: str, *, url: str, pdf_bytes: bytes, filename: str) -> dict[str, Any]:
    temp_root = REPO_ROOT / ".tmp_mineru_cli"
    temp_root.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=temp_root) as temp_dir:
        temp_path = Path(temp_dir)
        input_path = temp_path / filename
        output_path = temp_path / "out"
        input_path.write_bytes(pdf_bytes)
        output_path.mkdir(parents=True, exist_ok=True)

        cmd = shlex.split(command, posix=os.name != "nt")
        if not cmd:
            raise MinerUBackendError(
                "MINERU_ENDPOINT is empty.",
                reason_codes=["mineru_missing_endpoint"],
            )
        cmd.extend(["-p", str(input_path), "-o", str(output_path)])
        mineru_backend = os.getenv("MINERU_BACKEND")
        if mineru_backend:
            cmd.extend(["-b", mineru_backend])

        completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if completed.returncode != 0:
            raise MinerUBackendError(
                completed.stderr.strip() or completed.stdout.strip() or "MinerU CLI failed.",
                reason_codes=["mineru_cli_failed"],
            )

        markdown_path = _find_first(output_path, ".md")
        json_path = _find_first(output_path, ".json")
        if not markdown_path or not markdown_path.read_text(encoding="utf-8").strip():
            raise MinerUBackendError(
                "MinerU CLI returned empty content.",
                reason_codes=["mineru_empty_content"],
            )
        extracted_json: Any = {}
        if json_path:
            try:
                extracted_json = json.loads(json_path.read_text(encoding="utf-8"))
            except ValueError:
                extracted_json = json_path.read_text(encoding="utf-8")
        return _payload_from_outputs(
            url=url,
            pdf_bytes=pdf_bytes,
            markdown=markdown_path.read_text(encoding="utf-8").strip(),
            extracted_json=extracted_json,
            raw_pdf_name=filename,
        )


def run_mineru_backend(
    url: str,
    *,
    endpoint: str | None = None,
    pdf_bytes: bytes | None = None,
    filename: str | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    mineru_endpoint = endpoint or os.getenv("MINERU_ENDPOINT")
    if not mineru_endpoint:
        raise MinerUBackendError(
            "Missing MINERU_ENDPOINT for MinerU fallback.",
            reason_codes=["mineru_missing_endpoint"],
        )

    content = pdf_bytes or _download_pdf(url, timeout=timeout)
    pdf_name = filename or Path(canonicalize_url(url)).name or "source.pdf"
    if not pdf_name.lower().endswith(".pdf"):
        pdf_name = f"{pdf_name}.pdf"

    if mineru_endpoint.startswith(("http://", "https://")):
        return _run_mineru_api(mineru_endpoint, url=url, pdf_bytes=content, filename=pdf_name, timeout=timeout)
    return _run_mineru_cli(mineru_endpoint, url=url, pdf_bytes=content, filename=pdf_name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the MinerU backend for PDF and complex documents.")
    parser.add_argument("url", help="PDF URL to parse through MinerU")
    args = parser.parse_args()
    print(json.dumps(run_mineru_backend(args.url), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
