---
phase: 04-mineru-pdf-fallback
plan: 01
subsystem: ingestion
tags: [mineru, pdf, source-packet, artifact-refs, mock-verification]
requires:
  - "03-firecrawl-fallback"
provides:
  - "MinerU backend wrapper for direct PDF intake and complex-document escalation"
  - "Packet archive refs for raw PDF, extracted JSON, and markdown source snapshots"
  - "Mocked PDF-path regression coverage including unsupported fallback behavior"
affects: [05-verifier-and-cron, 06-github-placeholder-adapter]
tech-stack:
  added: []
  patterns:
    - "Document backends return in-memory artifact payloads and normalization writes them into packet archives"
    - "PDF flows downgrade to UNSUPPORTED when MinerU is unavailable rather than pretending extraction succeeded"
key-files:
  created:
    - tests/integration/test_source_intake_mineru.py
  modified:
    - optional-skills/research/source-intake/scripts/normalize_packet.py
    - optional-skills/research/source-intake/scripts/run_mineru_backend.py
    - optional-skills/research/source-intake/scripts/intake_url.py
    - optional-skills/research/source-intake/references/backend-matrix.md
    - optional-skills/research/source-intake/references/packet-contract.md
    - optional-skills/research/source-intake/references/examples.md
key-decisions:
  - "Selected mock-only verification for Phase 4 because no live MinerU endpoint or local CLI was configured in the current environment."
  - "Used the official MinerU CLI and `/file_parse` API shapes as the wrapper boundary, based on the upstream project documentation."
  - "Preserved raw PDF, extracted JSON, and markdown snapshot refs directly in the packet archive so downstream review remains traceable."
patterns-established:
  - "Complex-document backends should provide artifact payloads, not write directly into wiki destinations."
  - "PDF routing and escalation reasons are shared between code, tests, and reference docs."
requirements-completed: [FALLBACK-02]
duration: 45min
completed: 2026-04-13
---

# Phase 4: MinerU PDF Fallback Summary

**PDF and complex-document intake now routes through MinerU, preserves raw PDF and extracted artifacts in packet refs, and degrades to `UNSUPPORTED` when no MinerU path is configured**

## Performance

- **Duration:** 45 min
- **Started:** 2026-04-13T17:40:00Z
- **Completed:** 2026-04-13T18:25:00Z
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments
- Implemented a MinerU wrapper that supports the official CLI shape and `/file_parse` API shape, using `MINERU_ENDPOINT` as the runtime selector.
- Extended packet normalization so PDF flows can persist `raw_pdf`, `extracted_json`, and markdown `source_snapshot` refs inside the archive.
- Added mocked coverage for direct PDF routing, Firecrawl-to-MinerU escalation, wrapper API behavior, and unsupported fallback when MinerU is unavailable.

## Task Commits

This workspace is not operating as a tracked git repository for commits, so no task hashes were recorded.

## Files Created/Modified
- `optional-skills/research/source-intake/scripts/run_mineru_backend.py` - MinerU API/CLI wrapper plus normalized artifact payloads
- `optional-skills/research/source-intake/scripts/intake_url.py` - direct PDF routing and MinerU escalation handling
- `optional-skills/research/source-intake/scripts/normalize_packet.py` - packet archive writing for raw PDF, extracted JSON, and source snapshots
- `optional-skills/research/source-intake/references/backend-matrix.md` - direct MinerU routing rules, escalation reason codes, and official CLI notes
- `optional-skills/research/source-intake/references/packet-contract.md` - explicit PDF artifact ref expectations
- `optional-skills/research/source-intake/references/examples.md` - direct PDF and Firecrawl-to-MinerU examples
- `tests/integration/test_source_intake_mineru.py` - mocked regression coverage for MinerU paths

## Decisions Made

- Chose `mock-only` verification because no live MinerU endpoint or local executable was configured yet.
- Standardized MinerU success payloads on the same packet contract used by native and Firecrawl so later verifier logic remains backend-agnostic.
- Treated missing MinerU configuration as `UNSUPPORTED` for PDF flows, which is safer than inventing partial article extraction for documents the current chain cannot parse.

## Deviations from Plan

### Auto-fixed Issues

**1. [Review Gate - Environment] Independent external AI review was unavailable**
- **Found during:** Pre-execution review routing for Phase 4
- **Issue:** As with Phase 3, only the current Codex runtime was installed locally, so `/gsd-review --phase 4 --all` could not produce an independent cross-AI review.
- **Fix:** Recorded the environment limitation and completed the phase with mocked execution and verification instead of blocking on missing reviewer CLIs.
- **Files modified:** .planning/STATE.md
- **Verification:** Local CLI detection still showed only `codex`, while the Phase 4 PDF-path harness passed all mocked checks.

---

**Total deviations:** 1 auto-fixed (environment-only)
**Impact on plan:** No scope change. The only omitted artifact is an independent review file; the code, docs, and mocked PDF-path verification are complete.

## Issues Encountered

- The current environment has no live MinerU endpoint or CLI configured, so interactive execution used the plan's allowed `mock-only` path.

## User Setup Required

Optional only: configure `MINERU_ENDPOINT` if you want to run a live MinerU smoke test later. The wrapper supports either an HTTP endpoint or a CLI command such as `mineru`.

## Next Phase Readiness

- Phase 5 can now consume stable packet refs across native, Firecrawl, and MinerU without reopening backend-specific archive behavior.
- The next workflow step should be Phase 5 verifier and cron implementation, with review still subject to the current local CLI limitation.

---
*Phase: 04-mineru-pdf-fallback*
*Completed: 2026-04-13*
