---
schema: raw-asset
schema_version: 1.0.0
asset_id: fixture-asset
source_id: example-web-source
run_id: run-fixture
source_kind: web_url
adapter: web_url
canonical_url: https://example.com/article
retrieved_at: 2026-04-13T10:05:00Z
published_at: 2026-04-13T10:00:00Z
language: en
content_hash: fixturehash
dedupe_key: fixturekey
status: ingested
title: Example Ingest Article
default_topics:
  - sample-topic
provenance:
  fetch_method: requests.get
  fetch_url: https://example.com/article
  resolved_url: https://example.com/article
  extractor: regex-cleaner
  extractor_version: 1.0.0
refs:
  registry_source: content/registry/sources/example-web-source.md
  registry_job: content/registry/jobs/example-web-job.md
  run_manifest: state/runs/run-fixture.json
  source_snapshot: null
---

# Example Ingest Article

Fixture body content.
