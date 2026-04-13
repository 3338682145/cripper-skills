---
phase: 02-native-backend-orchestration
plan: 01
subsystem: ingestion
tags: [native-backend, source-packet, routing, provenance, migration]
requires:
  - "01-skill-skeleton"
provides:
  - "Single-URL source-intake orchestration from classify through native extraction and packet routing"
  - "Additive source-packet contract with provenance, routing, archive refs, and verdict metadata"
  - "Baseline raw/review routing with canonical URL dedupe and migration notes"
affects: [03-firecrawl-fallback, 04-mineru-pdf-fallback, 05-verifier-and-cron, 06-github-placeholder-adapter]
tech-stack:
  added: []
  patterns:
    - "Optional skill scripts import cliper primitives rather than reimplementing network fetch or extraction"
    - "Packets are normalized in the skill layer while cliper core remains ingestion-only"
key-files:
  created: []
  modified:
    - src/cliper/models.py
    - optional-skills/research/source-intake/scripts/intake_url.py
    - optional-skills/research/source-intake/scripts/classify_url.py
    - optional-skills/research/source-intake/scripts/run_native_backend.py
    - optional-skills/research/source-intake/scripts/normalize_packet.py
    - optional-skills/research/source-intake/scripts/route_packet.py
    - optional-skills/research/source-intake/references/packet-contract.md
    - docs/migrations/2026-04-13-source-packet-v0-to-v1.md
    - tests/integration/test_source_intake_native.py
key-decisions:
  - "Kept packet writing in the optional skill layer so cliper core did not gain wiki-routing responsibilities."
  - "Made source-packet provenance explicit to preserve AGENTS.md traceability guarantees."
  - "Used canonical_url dedupe across both raw and review destinations before later queue and cron work begins."
patterns-established:
  - "Native wrappers expose a backend payload and normalization turns that into the packet contract."
  - "Phase 3 and later should extend the existing intake_url pipeline rather than creating parallel entrypoints."
requirements-completed: [NATIVE-01, NATIVE-02, PACKET-01, PACKET-02, GOV-01]
duration: 45min
completed: 2026-04-13
---

# Phase 2: Native Backend Orchestration Summary

**Single-URL native source intake now classifies URLs, reuses cliper extraction, emits provenance-rich source-packets, and routes them into raw or review with canonical dedupe**

## Performance

- **Duration:** 45 min
- **Started:** 2026-04-13T16:05:00Z
- **Completed:** 2026-04-13T16:50:00Z
- **Tasks:** 3
- **Files modified:** 9

## Accomplishments
- Implemented the native phase of the optional skill pipeline from URL classification through native extraction, normalization, and route handoff.
- Added the additive `source-packet` contract in code with provenance, routing, verdict, and archive refs while preserving the `cliper` ingestion boundary.
- Added migration guidance and integration coverage for raw routing, review routing, and canonical URL dedupe.

## Task Commits

This workspace is not operating as a tracked git repository for commits, so no task hashes were recorded.

## Files Created/Modified
- `src/cliper/models.py` - adds `source-packet` record types plus routing, refs, verifier, and provenance support
- `optional-skills/research/source-intake/scripts/classify_url.py` - classifies input URLs into the v1 source types
- `optional-skills/research/source-intake/scripts/run_native_backend.py` - wraps existing `cliper` extraction as the native backend payload
- `optional-skills/research/source-intake/scripts/normalize_packet.py` - converts backend payloads into `source-packet` markdown and archive refs
- `optional-skills/research/source-intake/scripts/route_packet.py` - writes packets to raw or review with canonical URL dedupe
- `optional-skills/research/source-intake/scripts/intake_url.py` - orchestrates classify -> native backend -> normalize -> route
- `optional-skills/research/source-intake/references/packet-contract.md` - documents the packet frontmatter, including provenance
- `docs/migrations/2026-04-13-source-packet-v0-to-v1.md` - records the additive migration boundary for `source-packet`
- `tests/integration/test_source_intake_native.py` - covers raw routing, review routing, and canonical URL dedupe

## Decisions Made

- Kept packet routing outside `src/cliper/` so the repo remains ingestion-only and the optional skill owns wiki-target handoff.
- Preserved provenance directly in packet frontmatter because packet refs alone were not enough to satisfy traceability expectations.
- Treated verifier output as baseline phase input for now; final verdict logic still belongs to Phase 5.

## Deviations from Plan

### Auto-fixed Issues

**1. [Environment - Test Runner] Replaced unavailable pytest execution with an inline Python harness**
- **Found during:** Task 3 (integration verification)
- **Issue:** The current `.venv` does not have `pytest` installed, so the default verification command could not run.
- **Fix:** Verified the same route and dedupe behavior with a workspace-local Python harness that loads the intake script and patches HTTP fetches.
- **Files modified:** tests/integration/test_source_intake_native.py
- **Verification:** Inline Python harness passed raw route, review route, packet contract, provenance, and dedupe checks.

---

**Total deviations:** 1 auto-fixed (environment-only)
**Impact on plan:** No scope change. The code path was still verified, and the dedicated integration test file remains ready for future `pytest` runs once dev dependencies are installed.

## Issues Encountered

- Windows sandbox access to the system temp directory caused false-negative verification failures, so verification used a workspace-local temp folder instead.

## User Setup Required

None - no external service configuration is required for the native-only phase.

## Next Phase Readiness

- Phase 3 can now layer Firecrawl fallback onto the existing `intake_url.py` path instead of creating a second ingestion flow.
- The next workflow step should be a Phase 3 review pass, then interactive fallback execution once Firecrawl credential mode is chosen.

---
*Phase: 02-native-backend-orchestration*
*Completed: 2026-04-13*
