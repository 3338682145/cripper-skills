# Architecture

**Analysis Date:** 2026-04-13

## Pattern Overview

**Overall:** Monolithic Python CLI with file-based state and a small adapter/service split

**Key Characteristics:**
- One executable package (`cliper`) with subcommands for validation and ingestion
- Contracts are Markdown documents with YAML frontmatter, not database records
- State is persisted on disk as Markdown assets, JSON manifests, and derived indexes
- Extraction is adapter based, but orchestration currently lives in a single service module

## Layers

**Command Layer:**
- Purpose: Parse CLI input and route to validation or ingestion flows
- Contains: `src/cliper/cli.py`, `src/cliper/__main__.py`
- Depends on: Service layer
- Used by: Human or agent CLI invocations

**Service Layer:**
- Purpose: Load registries, validate contracts, orchestrate ingestion, write outputs
- Contains: `src/cliper/service.py`
- Depends on: Models, markdown I/O helpers, adapters
- Used by: CLI commands and future native backend wrappers

**Contract Layer:**
- Purpose: Define typed records for registry, raw asset, and run-manifest frontmatter
- Contains: `src/cliper/models.py`, `contracts/schemas/*.yaml`
- Depends on: Pydantic and schema governance docs
- Used by: Service layer, validation, tests

**Adapter Layer:**
- Purpose: Fetch and extract page content
- Contains: `src/cliper/adapters/web_url.py`
- Depends on: requests, BeautifulSoup, readability, markdownify
- Used by: `IngestService`

**Document I/O Layer:**
- Purpose: Parse and write Markdown frontmatter documents
- Contains: `src/cliper/markdown.py`
- Depends on: PyYAML and filesystem paths
- Used by: Service layer and tests

## Data Flow

**CLI Ingestion Flow:**

1. User or agent runs `cliper ingest run --source ... --job ...`
2. `cli.py` routes to `IngestService.run()`
3. `Workspace` resolves `content/` and `state/` paths and ensures layout
4. Registry files are loaded from `content/registry/` and validated into Pydantic models
5. `fetch_document()` downloads the seed URL and extracts Markdown content
6. The service dedupes by canonical URL, writes HTML snapshot and raw asset Markdown, then emits a JSON run manifest
7. Validation updates `state/indexes/raw-assets.json`

**Validation Flow:**

1. CLI routes to `ValidationService`
2. Registry frontmatter is parsed and validated
3. Raw assets are scanned for broken refs and empty bodies
4. Validation issues are surfaced to the CLI, not swallowed

**State Management:**
- File based only
- Canonical URL is the current dedupe key
- No persistent queue, worker, or external state service yet

## Key Abstractions

**Workspace:**
- Purpose: Canonical path resolver for the repo layout
- Examples: `Workspace.source_registry_dir`, `Workspace.raw_dir`, `Workspace.runs_dir`
- Pattern: Thin path/service helper

**Record Models:**
- Purpose: Typed frontmatter contracts for source/job/raw asset/run manifest
- Examples: `SourceRecord`, `JobRecord`, `RawAssetRecord`, `RunManifest`
- Pattern: Pydantic schema objects with field and model validators

**FetchedDocument:**
- Purpose: In-memory result from HTML extraction before it becomes a raw asset
- Examples: canonical URL, title, language, markdown body, raw HTML
- Pattern: Dataclass adapter payload

## Entry Points

**CLI Entry:**
- Location: `src/cliper/cli.py`
- Triggers: `cliper registry validate`, `cliper ingest run`, `cliper validate all`
- Responsibilities: Parse args, echo failures, exit non-zero on invalid state

**Module Entry:**
- Location: `src/cliper/__main__.py`
- Triggers: `python -m cliper`
- Responsibilities: Delegate to the CLI entrypoint

## Error Handling

**Strategy:** Fail fast with explicit `ValueError` or validation errors that bubble to the CLI

**Patterns:**
- Registry and raw-asset validation errors are accumulated into `ValidationIssue` lists
- Ingestion stops on invalid registry or raw store state before writing new assets
- Per-URL fetch failures are recorded in the run manifest instead of crashing the whole run

## Cross-Cutting Concerns

**Validation:**
- Contract validation happens at file boundaries
- Seed URLs must remain inside `allowed_domains`

**Traceability:**
- Raw assets point back to registry source, run manifest, and HTML snapshot
- Timestamps are normalized to UTC ISO strings

**Extraction Quality:**
- Native extraction prefers docs-like DOM fragments first
- Readability is the current fallback when DOM structure is weak

---

*Architecture analysis: 2026-04-13*
*Update when the optional-skill layer introduces new orchestration patterns*
