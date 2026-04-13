# PRD: Phase 6 GitHub Placeholder Adapter

## Goal

Recognize GitHub URLs and generate placeholder packets that keep the intake workflow explicit about what is unsupported in v1.

## In Scope

- GitHub URL classification
- Placeholder packet generation
- Fixed `UNSUPPORTED` routing behavior
- Tests and examples that confirm no deep ingestion occurs

## Out of Scope

- Repository crawling
- README or code extraction
- Wiki linking or output generation

## Acceptance Criteria

1. GitHub URLs are classified separately from article, docs, and PDF URLs.
2. The adapter writes a placeholder packet with `UNSUPPORTED` verdict and reason codes.
3. No GitHub code path invokes crawling, cloning, or browser automation.

## Canonical Refs

- `PLAN.md`
- `optional-skills/research/source-intake/references/examples.md`
- `.planning/codebase/CONCERNS.md`
