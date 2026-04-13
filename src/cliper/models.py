from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _host_allowed(url: str, allowed_domains: list[str]) -> bool:
    host = (urlsplit(url).hostname or "").lower()
    return any(host == domain or host.endswith(f".{domain}") for domain in allowed_domains)


class CliperModel(BaseModel):
    model_config = ConfigDict(protected_namespaces=(), populate_by_name=True)


class ValidationIssue(CliperModel):
    location: str
    message: str


class Provenance(CliperModel):
    fetch_method: str
    fetch_url: str
    resolved_url: str
    extractor: str
    extractor_version: str


class DocumentRefs(CliperModel):
    registry_source: str
    run_manifest: str
    registry_job: str | None = None
    source_snapshot: str | None = None


class SourcePacketRouting(CliperModel):
    suggested_topic: str | None = None
    suggested_kind: Literal["docs", "blog", "paper", "reference"] | None = None


class SourcePacketRefs(CliperModel):
    artifact_dir: str
    raw_html: str | None = None
    raw_pdf: str | None = None
    extracted_json: str | None = None
    verifier_report: str
    source_snapshot: str | None = None


class SourceRecord(CliperModel):
    schema_name: Literal["ingestion-source"] = Field(alias="schema")
    schema_version: str
    source_id: str
    display_name: str
    status: Literal["active", "paused", "deprecated"]
    source_kind: Literal["web_url"]
    adapter: Literal["web_url"]
    seed_urls: list[str]
    allowed_domains: list[str]
    discovery_mode: Literal["seed_urls"]
    default_topics: list[str] = Field(default_factory=list)
    schedule: dict[str, Any]
    owner: str
    validation_profile: str

    @field_validator("seed_urls", "allowed_domains")
    @classmethod
    def validate_non_empty_lists(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("must not be empty")
        return value

    @model_validator(mode="after")
    def validate_seed_domains(self) -> "SourceRecord":
        invalid = [url for url in self.seed_urls if not _host_allowed(url, self.allowed_domains)]
        if invalid:
            joined = ", ".join(invalid)
            raise ValueError(f"seed_urls outside allowed_domains: {joined}")
        return self


class JobRecord(CliperModel):
    schema_name: Literal["ingestion-job"] = Field(alias="schema")
    schema_version: str
    job_id: str
    source_id: str
    trigger: Literal["manual", "scheduled"]
    cadence: str
    max_items: int = Field(ge=1)
    fetch_budget: int = Field(ge=1)
    retry_policy: dict[str, Any]
    write_targets: list[str]
    dossier_policy: str

    @field_validator("write_targets")
    @classmethod
    def validate_write_targets(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("must not be empty")
        return value


class RawAssetRecord(CliperModel):
    schema_name: Literal["raw-asset"] = Field(alias="schema")
    schema_version: str
    asset_id: str
    source_id: str
    run_id: str
    source_kind: str
    adapter: str
    canonical_url: str
    retrieved_at: str
    published_at: str | None = None
    language: str
    content_hash: str
    dedupe_key: str
    status: Literal["ingested", "deduped", "invalid"]
    title: str | None = None
    default_topics: list[str] = Field(default_factory=list)
    provenance: Provenance
    refs: DocumentRefs

    @field_validator("retrieved_at", "published_at", mode="before")
    @classmethod
    def stringify_datetimes(cls, value: Any) -> Any:
        if isinstance(value, datetime):
            return value.isoformat().replace("+00:00", "Z")
        return value


class SourcePacketRecord(CliperModel):
    schema_name: Literal["source-packet"] = Field(alias="schema")
    schema_version: str
    packet_id: str
    source_type: Literal["blog_article", "docs_page", "paper_page", "pdf_url", "github_repo", "unknown"]
    input_url: str
    canonical_url: str
    title: str | None = None
    retrieved_at: str
    published_at: str | None = None
    language: str
    backend_used: Literal["native", "firecrawl", "mineru", "github_placeholder"]
    backend_version: str
    content_hash: str
    dedupe_key: str
    signal_level: Literal["high", "medium", "low"]
    verdict: Literal["AUTO_PASS", "REVIEW_REQUIRED", "LOW_SIGNAL", "UNSUPPORTED"]
    confidence: float = Field(ge=0.0, le=1.0)
    provenance: Provenance
    reason_codes: list[str] = Field(default_factory=list)
    routing: SourcePacketRouting
    refs: SourcePacketRefs

    @field_validator("retrieved_at", "published_at", mode="before")
    @classmethod
    def stringify_packet_datetimes(cls, value: Any) -> Any:
        if isinstance(value, datetime):
            return value.isoformat().replace("+00:00", "Z")
        return value


class VerifierResult(CliperModel):
    verdict: Literal["AUTO_PASS", "REVIEW_REQUIRED", "LOW_SIGNAL", "UNSUPPORTED"]
    confidence: float = Field(ge=0.0, le=1.0)
    signal_level: Literal["high", "medium", "low"]
    reason_codes: list[str] = Field(default_factory=list)
    summary: str
    suggested_topic: str | None = None
    suggested_kind: Literal["docs", "blog", "paper", "reference"] | None = None


class RunFailure(CliperModel):
    url: str
    error: str


class RunManifest(CliperModel):
    run_id: str
    source_id: str
    job_id: str | None = None
    trigger: str
    status: Literal["completed", "partial", "failed"]
    started_at: str
    completed_at: str
    created_assets: list[str] = Field(default_factory=list)
    deduped_assets: list[str] = Field(default_factory=list)
    failed_items: list[RunFailure] = Field(default_factory=list)
    skipped_items: list[str] = Field(default_factory=list)
