# PRD: Phase 1 Skill Skeleton

## Goal

Create the optional skill package that later phases can fill in without renegotiating metadata, directory layout, or operator-facing references.

## In Scope

- `optional-skills/research/source-intake/` directory layout
- `SKILL.md` metadata, config keys, and required environment variables
- Placeholder script entrypoints for classification, native backend, fallbacks, normalization, verification, routing, and cron
- Reference docs for backend matrix, packet contract, verifier rubric, and examples

## Out of Scope

- Real backend logic
- Verifier implementation
- Queue processing
- Firecrawl or MinerU integration

## Acceptance Criteria

1. The skill package is discoverable and documents `wiki.path`, `review_dir`, `archive_dir`, `default_backend`, and `github_mode`.
2. The package contains script entrypoints matching the reviewed design.
3. Reference docs define the packet shape, backend decision rules, verifier categories, and sample flows.

## Canonical Refs

- `PLAN.md`
- `AGENTS.md`
- `.planning/codebase/ARCHITECTURE.md`
