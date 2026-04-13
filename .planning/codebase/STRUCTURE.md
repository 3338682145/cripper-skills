# Structure

**Analysis Date:** 2026-04-13

## Top-Level Layout

```text
.planning/              GSD project, roadmap, requirements, PRDs, and phase plans
content/                Source registry inputs and raw Markdown outputs
contracts/              Canonical YAML schema documents
docs/                   Architecture, migration, and validation documentation
llm-wiki/               Sibling consumer package kept outside runtime coupling
src/cliper/             Python package, CLI, services, models, adapters
state/                  Run manifests and derived indexes
tests/                  Contract fixtures and integration tests
```

## Source Tree

```text
src/cliper/
  __main__.py           Python module entrypoint
  cli.py                Typer CLI definitions
  markdown.py           Frontmatter parse/write helpers
  models.py             Pydantic contract models
  service.py            Workspace, validation, and ingestion orchestration
  adapters/
    web_url.py          Native HTML fetch and extraction logic
```

## Registry and Output Data

```text
content/
  registry/
    sources/*.md        Markdown source definitions
    jobs/*.md           Markdown ingest-job definitions
  raw/YYYY/MM/DD/...    Written raw assets

state/
  runs/*.json           Per-run manifests
  indexes/raw-assets.json
```

## Tests

```text
tests/
  conftest.py                     Shared tmp workspace factory
  contract/                       Registry and raw-asset validation tests
  integration/                    End-to-end ingest tests
  fixtures/                       HTML and Markdown fixture files
```

## Planning Artifacts

- `.planning/PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md` hold the current milestone state
- `.planning/prd/` now stores the legacy milestone bootstrap PRD plus the new phase-scoped PRDs
- `.planning/phases/` will contain the executable phase plans for the `source-intake` milestone
- `.planning/codebase/` is the brownfield map for future GSD agents

## Important Files

- `AGENTS.md` - repo-specific operating rules and architecture boundaries
- `PLAN.md` - source-intake design and review summary
- `pyproject.toml` - Python project metadata and dependencies
- `README.md` - current operator overview for the native backend
- `docs/validation/contract-gates.md` - validation and governance rules

---

*Structure analysis: 2026-04-13*
*Update when directories or core entrypoints move*
