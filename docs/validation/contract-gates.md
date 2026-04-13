# Hermes Cliper Validation Gates

## Registry

- Every source and job file under `content/registry/` must have YAML frontmatter.
- Jobs must reference an existing `source_id`.
- Seed URLs must stay within `allowed_domains`.

## Raw assets

- Every raw asset under `content/raw/` must have frontmatter and a non-empty body.
- Required fields include `source_id`, `canonical_url`, `content_hash`, `dedupe_key`, `provenance`, and `refs`.
- `refs.registry_source` and `refs.run_manifest` must resolve inside the repo.
- New ingests must also write `refs.source_snapshot`, and that HTML snapshot path must resolve inside the repo.

## Runs and governance

- Every ingest execution must write one manifest under `state/runs/`.
- Re-running the same canonical URL must dedupe instead of writing another asset.
- Any schema version change requires a migration note under `docs/migrations/`.
- Topic dossiers remain contract-only in Milestone 1A.
