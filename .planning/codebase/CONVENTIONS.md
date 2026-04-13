# Conventions

**Analysis Date:** 2026-04-13

## Naming and Layout

- Python modules use snake_case filenames and class names in PascalCase
- Contracts use Markdown with YAML frontmatter, not standalone JSON documents
- Schema identifiers live in the `schema` frontmatter field and are validated through aliased Pydantic fields
- Output directories are date partitioned for raw assets and flat for run manifests

## Code Organization

- CLI commands stay thin and delegate immediately to services
- Filesystem paths are centralized behind `Workspace` helpers instead of being hand-built all over the codebase
- Frontmatter parsing and writing lives in `markdown.py`, not inline inside services
- Adapters encapsulate extraction mechanics; `service.py` owns orchestration and repo layout

## Data and Contract Rules

- Every registry or asset document must have YAML frontmatter
- Canonical URL is the dedupe anchor
- UTC timestamps are written as ISO 8601 strings ending in `Z`
- Raw assets and future source packets must always keep provenance refs to their inputs and run artifacts

## Testing Conventions

- Tests live in a dedicated `tests/` tree, not alongside source modules
- `workspace_factory` builds disposable on-disk repos so tests exercise the real file layout
- Integration tests prefer mocking the network boundary instead of mocking internal orchestration

## Documentation and Governance

- Contract changes require migration notes under `docs/migrations/`
- Architecture boundary changes must stay consistent with `AGENTS.md`
- Planning docs should describe phase goals in behavior terms, not just file inventories

## Near-Term Milestone Conventions

- The optional skill should stay outside `src/cliper/` unless a reusable native primitive belongs in core
- Firecrawl and MinerU integration plans should declare human setup explicitly instead of assuming credentials or local services exist
- Verifier output must stay deterministic and machine-readable

---

*Conventions analysis: 2026-04-13*
*Update when code patterns or planning norms change*
