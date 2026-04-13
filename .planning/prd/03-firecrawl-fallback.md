# PRD: Phase 3 Firecrawl Fallback

## Goal

Add a Firecrawl fallback path for low-signal or JS-heavy pages while keeping native extraction as the default path.

## In Scope

- Firecrawl backend wrapper script
- API key configuration and operator docs
- Heuristics for when to switch from native to Firecrawl
- Reason-code reporting for fallback decisions and failures
- Mocked integration tests and a live-verification checkpoint path

## Out of Scope

- PDF fallback to MinerU
- Final verifier verdict routing
- Queue and cron behavior

## Acceptance Criteria

1. Native low-signal extraction can trigger a Firecrawl retry.
2. JS-heavy pages can route to Firecrawl even when native fetch succeeds.
3. Missing credentials or failed Firecrawl calls return explicit reason codes and do not silently pass.

## Canonical Refs

- `optional-skills/research/source-intake/references/backend-matrix.md`
- `src/cliper/adapters/web_url.py`
- `.planning/codebase/INTEGRATIONS.md`
- Firecrawl official site: <https://www.firecrawl.dev/>
