# PRD: Hermes Cliper Milestone 1A

## Goal

Define contracts, stand up a Markdown registry, and implement one executable web URL ingestion path that writes validated raw assets and run manifests.

## In Scope

- Repository bootstrap for GSD planning artifacts
- Source and job registry schemas
- Raw asset schema and writer
- Topic dossier schema as contract-only
- Validation CLI
- Web URL ingestion adapter with dedupe and manifests
- Contract and integration tests

## Out of Scope

- Topic dossier builder
- Feed, video, transcript, or browser-driven ingestion
- `llm-wiki` integration logic
- Publishing/output code

## Acceptance Criteria

1. `cliper registry validate` succeeds for valid sample registry files.
2. `cliper ingest run --source <source_id>` writes a raw Markdown asset plus a run manifest.
3. Re-running the same source dedupes on canonical URL.
4. `cliper validate all` catches malformed raw assets and broken job references.
5. Schema contracts and migration rules are present in-repo.
