# PRD: Phase 5 Verifier and Cron

## Goal

Add the quality gate and automation path that turns the multi-backend intake chain into a durable, reviewable source-ingestion workflow.

## In Scope

- Verifier verdict contract and reason codes
- Raw vs review routing enforcement
- Dedupe across route destinations and queued runs
- `queue.jsonl` and `cron_drain_queue.py`
- `[SILENT]` behavior and result summaries
- Integration tests for routing, dedupe, and cron output

## Out of Scope

- GitHub deep ingestion
- Topic linking, wiki compilation, or output generation

## Acceptance Criteria

1. Verifier output contains only approved verdict values plus machine-readable metadata.
2. `AUTO_PASS` is the only verdict that can land in the wiki raw inbox.
3. Queue runs and manual runs use the same intake pipeline and dedupe rules.
4. Empty cron runs emit `[SILENT]`; non-empty runs summarize counts by verdict.

## Canonical Refs

- `optional-skills/research/source-intake/references/verifier-rubric.md`
- `optional-skills/research/source-intake/references/packet-contract.md`
- `docs/validation/contract-gates.md`
