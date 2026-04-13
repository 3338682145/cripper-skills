# Hermes Cliper State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-04-13)

**Core value:** Every downstream content artifact must trace back to a validated source packet or raw source asset.
**Current focus:** Phase 7 - Verification Evidence Backfill

## Current Status

- **Milestone**: v0.2 Source Intake Skill
- **Phase**: 7
- **Phase name**: Verification Evidence Backfill
- **Current plan**: `/gsd-plan-phase 7`
- **Status**: Ready to plan

## Notes

- Legacy Milestone 1A bootstrap remains the technical base for the new native backend work.
- Phase 1 completed: the optional skill skeleton, script entrypoints, and reference docs now exist under `optional-skills/research/source-intake/`.
- Phase 2 completed: a single URL can now flow through classification, native extraction, packet normalization, and baseline raw or review routing with canonical dedupe.
- Phase 3 completed: Firecrawl now serves as a native-first fallback for low-signal, JS-heavy, and native-fetch-failure cases with explicit reason codes.
- Phase 4 completed: MinerU now covers direct PDF routing and complex-document escalation with packet-level raw PDF and extracted JSON refs.
- Phase 5 completed: verifier verdicts, raw/review policy, queue draining, and `[SILENT]` cron behavior now share one routing pipeline.
- Phase 6 completed: GitHub URLs now resolve to explicit placeholder packets with `github_placeholder` and `UNSUPPORTED`, with no backend invocation.
- `.planning/codebase/` now captures the current repo layout so later GSD agents can reason from code instead of from the old roadmap.
- The shell environment still lacks a directly callable `pytest`; execution should use `uv run` or an activated virtualenv when test-running begins.
- Firecrawl and MinerU planning now reference the official dependency sources provided during execution: `https://www.firecrawl.dev/` and `https://github.com/opendatalab/mineru`.
- Cross-AI review remains environment-limited right now because only the current Codex runtime is installed locally; no independent reviewer CLI is available.
- Milestone audit completed: see `.planning/v0.2-MILESTONE-AUDIT.md`.
- Gap closure phases 7 and 8 now exist in the roadmap.
- Phase 7 will backfill `VERIFICATION.md` evidence for phases 1-6 and restore formal requirement coverage.
- Phase 8 will backfill `VALIDATION.md`, runnable verification commands, and live fallback smoke evidence.
- Firecrawl and MinerU remain operationally mock-only until Phase 8 records live smoke results or formal environment-blocked validation.
- The next workflow step is `/gsd-plan-phase 7`.
- `cliper` stays ingestion-only. Any wiki raw/review routing belongs to the optional skill layer, not the core runtime path.

---
*Last updated: 2026-04-13 during milestone reset to v0.2 Source Intake Skill*
