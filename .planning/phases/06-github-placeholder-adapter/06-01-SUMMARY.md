---
phase: 06-github-placeholder-adapter
plan: 01
subsystem: ingestion
tags: [github, placeholder, unsupported, scope-boundary]
requires:
  - "05-verifier-and-cron"
provides:
  - "GitHub URL classification bounded to one placeholder route"
  - "Placeholder packet generation with backend_used github_placeholder and UNSUPPORTED verdict"
  - "Regression coverage that prevents GitHub crawl, clone, or wiki-generation scope creep"
affects: [milestone-audit]
tech-stack:
  added: []
  patterns:
    - "Unsupported source families still produce traceable packets instead of silent drops"
    - "Scope boundaries are enforced through explicit placeholder routing and tests"
key-files:
  created:
    - tests/integration/test_source_intake_github.py
  modified:
    - optional-skills/research/source-intake/scripts/classify_url.py
    - optional-skills/research/source-intake/scripts/intake_url.py
    - optional-skills/research/source-intake/scripts/normalize_packet.py
    - optional-skills/research/source-intake/references/examples.md
key-decisions:
  - "Kept all GitHub URLs on a single github_repo classification instead of introducing deeper GitHub subtypes."
  - "GitHub placeholder packets are review-only and intentionally bypass every content backend."
  - "The placeholder body states the deferred scope explicitly so downstream reviewers know no repo ingestion was attempted."
patterns-established:
  - "Deferred source classes should degrade into explicit placeholder packets, not hidden failures."
  - "Unsupported behavior is protected by tests that assert backends are never invoked."
requirements-completed: [GITHUB-01]
duration: 25min
completed: 2026-04-13
---

# Phase 6: GitHub Placeholder Adapter Summary

**GitHub URLs now resolve to explicit placeholder packets with `github_placeholder` and `UNSUPPORTED`, making the v1 scope boundary visible in code, packets, and tests**

## Performance

- **Duration:** 25 min
- **Started:** 2026-04-13T19:25:00Z
- **Completed:** 2026-04-13T19:50:00Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments
- Tightened GitHub URL classification so repository, blob, and issue URLs all resolve to the single `github_repo` placeholder route.
- Implemented placeholder packet generation that bypasses native, Firecrawl, and MinerU and writes `backend_used: github_placeholder` plus `verdict: UNSUPPORTED`.
- Added regression coverage that verifies classification, placeholder packet fields, review routing, and the absence of backend calls for GitHub inputs.

## Task Commits

This workspace is not operating as a tracked git repository for commits, so no task hashes were recorded.

## Files Created/Modified
- `optional-skills/research/source-intake/scripts/classify_url.py` - bounded GitHub input detection
- `optional-skills/research/source-intake/scripts/intake_url.py` - placeholder packet generation and fixed unsupported routing for GitHub URLs
- `optional-skills/research/source-intake/scripts/normalize_packet.py` - verifier report summary support used by placeholder packets
- `optional-skills/research/source-intake/references/examples.md` - explicit GitHub placeholder example and reason codes
- `tests/integration/test_source_intake_github.py` - regression coverage for repo/blob/issue URLs and no-backend behavior

## Decisions Made

- Preserved one GitHub classification (`github_repo`) for all v1 GitHub inputs so the codebase does not accidentally imply partial repo ingestion support.
- Reused the shared packet normalization path instead of inventing a separate unsupported packet format.
- Encoded the deferred GitHub scope in packet body text and reason codes so reviewers and downstream tools can see the boundary directly.

## Deviations from Plan

None - plan executed as written.

## Issues Encountered

- None. This phase stayed fully local and did not depend on external services or reviewer CLIs.

## User Setup Required

None.

## Next Phase Readiness

- All six phases in the v0.2 milestone are now complete.
- The next workflow step is `/gsd-audit-milestone`.

---
*Phase: 06-github-placeholder-adapter*
*Completed: 2026-04-13*
