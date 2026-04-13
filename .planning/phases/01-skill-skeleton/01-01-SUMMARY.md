---
phase: 01-skill-skeleton
plan: 01
subsystem: ingestion
tags: [skill, source-intake, markdown, packet-contract]
requires: []
provides:
  - "Optional skill package skeleton for source intake"
  - "Script entrypoint stubs for all planned orchestration steps"
  - "Reference docs for backend selection, packet contract, verifier rubric, and examples"
affects: [02-native-backend-orchestration, 03-firecrawl-fallback, 04-mineru-pdf-fallback, 05-verifier-and-cron, 06-github-placeholder-adapter]
tech-stack:
  added: []
  patterns:
    - "Optional skill layout under optional-skills/research/source-intake/"
    - "One Python entrypoint per orchestration step"
key-files:
  created:
    - optional-skills/research/source-intake/SKILL.md
    - optional-skills/research/source-intake/scripts/intake_url.py
    - optional-skills/research/source-intake/references/packet-contract.md
  modified: []
key-decisions:
  - "Kept phase 1 documentation-only and stub-only so later phases can reuse stable filenames without premature implementation."
  - "Added official Firecrawl and MinerU references to lock external dependency assumptions early."
patterns-established:
  - "Skill references are the source of truth for backend, packet, and verifier boundaries."
  - "Phase 2+ should fill in the existing stub files rather than rename them."
requirements-completed: [SKILL-01, SKILL-02]
duration: 25min
completed: 2026-04-13
---

# Phase 1: Skill Skeleton Summary

**Source-intake optional skill skeleton with stable script entrypoints and locked reference docs for packet, backend, verifier, and external dependency behavior**

## Performance

- **Duration:** 25 min
- **Started:** 2026-04-13T15:35:00Z
- **Completed:** 2026-04-13T16:00:00Z
- **Tasks:** 3
- **Files modified:** 14

## Accomplishments
- Added the `source-intake` optional skill package with Hermes config and env-var metadata.
- Created all planned Python entrypoint stubs so later phases can implement in place.
- Wrote the reference docs that lock backend routing, packet fields, verifier vocabulary, examples, and official external dependency references.

## Task Commits

This workspace is not operating as a tracked git repository for commits, so no task hashes were recorded.

## Files Created/Modified
- `optional-skills/research/source-intake/SKILL.md` - skill metadata and operating rules
- `optional-skills/research/source-intake/scripts/*.py` - orchestration stubs for intake, backends, normalization, verification, routing, and cron
- `optional-skills/research/source-intake/references/backend-matrix.md` - backend selection rules and external dependency notes
- `optional-skills/research/source-intake/references/packet-contract.md` - `source-packet` frontmatter contract
- `optional-skills/research/source-intake/references/verifier-rubric.md` - approved verdict set and guardrails
- `optional-skills/research/source-intake/references/examples.md` - representative flow examples

## Decisions & Deviations

- Kept all phase 1 scripts as explicit `main()` stubs that raise `NotImplementedError` instead of silently doing nothing.
- Locked the GitHub v1 boundary in docs from the start so later phases do not drift into repo ingestion.
- Added official Firecrawl and MinerU references during execution after dependency assumptions were explicitly called out.

## Next Phase Readiness

- Phase 2 can now implement the native backend wrapper, classifier, normalizer, and router in the pre-created files.
- The stable filenames and docs mean Firecrawl, MinerU, verifier, and GitHub phases can layer on without reopening package design.
