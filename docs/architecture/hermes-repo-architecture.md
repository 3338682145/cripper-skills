# Hermes Cliper Repository Architecture

## Boundaries

- `cliper` owns ingestion only.
- `llm-wiki` owns knowledge linking and wiki maintenance.
- Output systems must consume topic dossiers, not raw assets.
- Every durable artifact must preserve provenance and traceability back to registry-defined sources.

## Milestone 1A

1. Markdown source and job registry entries define what can run.
2. A `web_url` adapter fetches and extracts content.
3. Cliper writes one raw Markdown asset per canonical source URL.
4. A run manifest records what happened for each ingest run.
5. Validation commands enforce frontmatter, references, and dedupe expectations.

## Non-goals

- No topic dossier builder yet
- No `llm-wiki` runtime integration
- No publishing flow

