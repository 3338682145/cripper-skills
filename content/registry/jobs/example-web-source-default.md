---
schema: ingestion-job
schema_version: 1.0.0
job_id: example-web-source-default
source_id: example-web-source
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

Default manual ingest job for the example web source.
