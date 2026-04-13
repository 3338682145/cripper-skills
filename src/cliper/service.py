from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from cliper.adapters.web_url import canonicalize_url, fetch_document
from cliper.markdown import read_markdown_document, write_markdown_document
from cliper.models import JobRecord, RawAssetRecord, RunFailure, RunManifest, SourceRecord, ValidationIssue


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "item"


@dataclass
class RegistrySnapshot:
    sources: dict[str, SourceRecord]
    source_paths: dict[str, Path]
    jobs: dict[str, JobRecord]
    job_paths: dict[str, Path]
    issues: list[ValidationIssue]


class Workspace:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    @property
    def source_registry_dir(self) -> Path:
        return self.root / "content" / "registry" / "sources"

    @property
    def job_registry_dir(self) -> Path:
        return self.root / "content" / "registry" / "jobs"

    @property
    def raw_dir(self) -> Path:
        return self.root / "content" / "raw"

    @property
    def runs_dir(self) -> Path:
        return self.root / "state" / "runs"

    @property
    def indexes_dir(self) -> Path:
        return self.root / "state" / "indexes"

    @property
    def raw_index_path(self) -> Path:
        return self.indexes_dir / "raw-assets.json"

    def ensure_layout(self) -> None:
        for path in [
            self.source_registry_dir,
            self.job_registry_dir,
            self.raw_dir,
            self.runs_dir,
            self.indexes_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)

    def rel(self, path: Path) -> str:
        return path.resolve().relative_to(self.root).as_posix()


def _load_registry_files(workspace: Workspace) -> RegistrySnapshot:
    issues: list[ValidationIssue] = []
    sources: dict[str, SourceRecord] = {}
    source_paths: dict[str, Path] = {}
    jobs: dict[str, JobRecord] = {}
    job_paths: dict[str, Path] = {}

    for path in sorted(workspace.source_registry_dir.glob("*.md")):
        try:
            metadata, _ = read_markdown_document(path)
            record = SourceRecord.model_validate(metadata)
        except (ValueError, ValidationError) as exc:
            issues.append(ValidationIssue(location=workspace.rel(path), message=str(exc)))
            continue
        if record.source_id in sources:
            issues.append(ValidationIssue(location=workspace.rel(path), message=f"duplicate source_id: {record.source_id}"))
            continue
        sources[record.source_id] = record
        source_paths[record.source_id] = path

    for path in sorted(workspace.job_registry_dir.glob("*.md")):
        try:
            metadata, _ = read_markdown_document(path)
            record = JobRecord.model_validate(metadata)
        except (ValueError, ValidationError) as exc:
            issues.append(ValidationIssue(location=workspace.rel(path), message=str(exc)))
            continue
        if record.job_id in jobs:
            issues.append(ValidationIssue(location=workspace.rel(path), message=f"duplicate job_id: {record.job_id}"))
            continue
        jobs[record.job_id] = record
        job_paths[record.job_id] = path

    for job_id, job in jobs.items():
        if job.source_id not in sources:
            issues.append(
                ValidationIssue(location=workspace.rel(job_paths[job_id]), message=f"unknown source_id: {job.source_id}")
            )

    return RegistrySnapshot(sources=sources, source_paths=source_paths, jobs=jobs, job_paths=job_paths, issues=issues)


def _scan_raw_assets(workspace: Workspace) -> tuple[list[tuple[RawAssetRecord, Path]], list[ValidationIssue]]:
    entries: list[tuple[RawAssetRecord, Path]] = []
    issues: list[ValidationIssue] = []
    for path in sorted(workspace.raw_dir.rglob("*.md")):
        try:
            metadata, body = read_markdown_document(path)
            record = RawAssetRecord.model_validate(metadata)
            if not body.strip():
                raise ValueError("raw asset body is empty")
            for ref_name in ("registry_source", "run_manifest"):
                ref_path = workspace.root / getattr(record.refs, ref_name)
                if not ref_path.exists():
                    raise ValueError(f"broken ref {ref_name}: {getattr(record.refs, ref_name)}")
            if record.refs.source_snapshot:
                snapshot_path = workspace.root / record.refs.source_snapshot
                if not snapshot_path.exists():
                    raise ValueError(f"broken ref source_snapshot: {record.refs.source_snapshot}")
        except (ValueError, ValidationError) as exc:
            issues.append(ValidationIssue(location=workspace.rel(path), message=str(exc)))
            continue
        entries.append((record, path))
    return entries, issues


def _write_raw_index(workspace: Workspace, entries: list[tuple[RawAssetRecord, Path]]) -> None:
    payload = {
        "generated_at": utc_now(),
        "assets": [
            {
                "asset_id": record.asset_id,
                "canonical_url": record.canonical_url,
                "dedupe_key": record.dedupe_key,
                "path": workspace.rel(path),
            }
            for record, path in entries
        ],
    }
    workspace.indexes_dir.mkdir(parents=True, exist_ok=True)
    workspace.raw_index_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


class ValidationService:
    def __init__(self, root: Path) -> None:
        self.workspace = Workspace(root)
        self.workspace.ensure_layout()

    def validate_registry(self) -> list[ValidationIssue]:
        return _load_registry_files(self.workspace).issues

    def validate_raw_assets(self) -> list[ValidationIssue]:
        entries, issues = _scan_raw_assets(self.workspace)
        _write_raw_index(self.workspace, entries)
        return issues

    def validate_all(self) -> list[ValidationIssue]:
        issues = self.validate_registry()
        issues.extend(self.validate_raw_assets())
        return issues


class IngestService:
    def __init__(self, root: Path) -> None:
        self.workspace = Workspace(root)
        self.workspace.ensure_layout()

    def run(self, source_id: str, job_id: str | None = None) -> RunManifest:
        registry = _load_registry_files(self.workspace)
        if registry.issues:
            message = "; ".join(f"{issue.location}: {issue.message}" for issue in registry.issues)
            raise ValueError(f"registry is invalid: {message}")
        if source_id not in registry.sources:
            raise ValueError(f"unknown source_id: {source_id}")
        if job_id and job_id not in registry.jobs:
            raise ValueError(f"unknown job_id: {job_id}")

        source = registry.sources[source_id]
        job = registry.jobs.get(job_id) if job_id else None
        manifest = RunManifest(
            run_id=f"run-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}",
            source_id=source_id,
            job_id=job_id,
            trigger=job.trigger if job else "manual",
            status="completed",
            started_at=utc_now(),
            completed_at="",
        )
        manifest_path = self.workspace.runs_dir / f"{manifest.run_id}.json"
        existing_entries, raw_issues = _scan_raw_assets(self.workspace)
        if raw_issues:
            message = "; ".join(f"{issue.location}: {issue.message}" for issue in raw_issues)
            raise ValueError(f"raw asset store is invalid: {message}")

        by_canonical_url = {record.canonical_url: self.workspace.rel(path) for record, path in existing_entries}
        max_items = job.max_items if job else len(source.seed_urls)

        for seed_url in source.seed_urls[:max_items]:
            canonical_seed_url = canonicalize_url(seed_url)
            existing = by_canonical_url.get(canonical_seed_url)
            if existing:
                manifest.deduped_assets.append(existing)
                continue

            try:
                fetched = fetch_document(seed_url)
            except Exception as exc:
                manifest.failed_items.append(RunFailure(url=seed_url, error=str(exc)))
                continue
            if fetched.canonical_url in by_canonical_url:
                manifest.deduped_assets.append(by_canonical_url[fetched.canonical_url])
                continue

            day_path = datetime.now(UTC)
            asset_id = sha256(f"{source_id}|{fetched.canonical_url}".encode("utf-8")).hexdigest()[:16]
            asset_path = (
                self.workspace.raw_dir
                / day_path.strftime("%Y")
                / day_path.strftime("%m")
                / day_path.strftime("%d")
                / slugify(source_id)
                / f"{asset_id}.md"
            )
            snapshot_path = asset_path.with_suffix(".source.html")
            snapshot_path.parent.mkdir(parents=True, exist_ok=True)
            snapshot_path.write_text(fetched.raw_html, encoding="utf-8")
            record = RawAssetRecord(
                schema="raw-asset",
                schema_version="1.0.0",
                asset_id=asset_id,
                source_id=source_id,
                run_id=manifest.run_id,
                source_kind=source.source_kind,
                adapter=source.adapter,
                canonical_url=fetched.canonical_url,
                retrieved_at=utc_now(),
                published_at=fetched.published_at,
                language=fetched.language,
                content_hash=fetched.content_hash,
                dedupe_key=fetched.dedupe_key,
                status="ingested",
                title=fetched.title,
                default_topics=source.default_topics,
                provenance={
                    "fetch_method": "requests.get",
                    "fetch_url": seed_url,
                    "resolved_url": fetched.resolved_url,
                    "extractor": "docs-first-dom",
                    "extractor_version": "2.0.0",
                },
                refs={
                    "registry_source": self.workspace.rel(registry.source_paths[source_id]),
                    "registry_job": self.workspace.rel(registry.job_paths[job_id]) if job_id else None,
                    "run_manifest": self.workspace.rel(manifest_path),
                    "source_snapshot": self.workspace.rel(snapshot_path),
                },
            )
            write_markdown_document(asset_path, record.model_dump(mode="json", by_alias=True), fetched.body_markdown)
            rel_asset_path = self.workspace.rel(asset_path)
            manifest.created_assets.append(rel_asset_path)
            by_canonical_url[fetched.canonical_url] = rel_asset_path
            existing_entries.append((record, asset_path))

        if manifest.failed_items and not (manifest.created_assets or manifest.deduped_assets):
            manifest.status = "failed"
        elif manifest.failed_items:
            manifest.status = "partial"

        manifest.completed_at = utc_now()
        manifest_path.write_text(json.dumps(manifest.model_dump(mode="json"), indent=2), encoding="utf-8")
        _write_raw_index(self.workspace, existing_entries)
        return manifest
