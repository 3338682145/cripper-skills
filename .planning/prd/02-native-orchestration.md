# PRD: Phase 2 Native Backend Orchestration

## Goal

Reuse the existing `cliper` service and extraction path as the native backend for the optional skill, then normalize the result into a `source-packet` contract with archive refs and baseline routing.

## In Scope

- URL classification for the v1 source types
- Native backend wrapper around current `cliper` primitives
- `source-packet` frontmatter contract and archive refs
- Baseline raw/review routing hooks
- Migration note coverage for additive contract changes

## Out of Scope

- Firecrawl fallback
- MinerU fallback
- Final verifier verdict logic
- Queue draining

## Acceptance Criteria

1. A single URL can move through classify -> native backend -> normalize -> route.
2. The native backend reuses current manifest, dedupe, and extraction behavior instead of duplicating it.
3. Packets include provenance, dedupe, routing, backend, and archive refs fields.
4. Contract changes ship with a migration note and do not break the current raw-asset workflow.

## Canonical Refs

- `src/cliper/service.py`
- `src/cliper/models.py`
- `src/cliper/adapters/web_url.py`
- `docs/migrations/README.md`
