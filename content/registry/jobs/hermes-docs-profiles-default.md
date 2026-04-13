---
schema: ingestion-job
schema_version: 1.0.0
job_id: hermes-docs-profiles-default
source_id: hermes-docs-profiles
trigger: manual
cadence: on-demand
max_items: 1
fetch_budget: 1
retry_policy:
  max_attempts: 2
  backoff_seconds: 1
write_targets:
  - raw-assets
  - run-manifest
dossier_policy: contract-only
---

Default manual ingest job for the Hermes docs profiles page.
