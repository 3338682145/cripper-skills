# Technology Stack

**Analysis Date:** 2026-04-13

## Languages

**Primary:**
- Python 3.12+ - All application, CLI, extraction, and validation code

**Secondary:**
- Markdown - Registries, raw assets, contracts, and planning artifacts
- YAML - Frontmatter contracts and schema documents
- JSON - Run manifests and derived state indexes

## Runtime

**Environment:**
- CPython 3.12 or newer
- No browser runtime, database server, or background worker required today

**Package Manager:**
- `uv` is the intended runner for local commands
- Lockfile: `uv.lock` present

## Frameworks

**Core:**
- Typer - CLI command routing and user-facing commands
- Pydantic v2 - Contract validation and typed records

**Content Extraction:**
- requests - HTTP fetches
- BeautifulSoup + lxml - HTML parsing and cleanup
- readability-lxml - Fallback extraction for generic pages
- markdownify - HTML to Markdown normalization

**Testing:**
- pytest - Contract and integration tests
- `typer.testing.CliRunner` - CLI command tests

## Key Dependencies

**Critical:**
- `pydantic` - Source, job, raw asset, and manifest models
- `typer` - `cliper` CLI entrypoint
- `requests` - Remote fetch boundary
- `beautifulsoup4` and `lxml` - DOM parsing
- `readability-lxml` - Readability fallback
- `markdownify` - Markdown conversion
- `PyYAML` - Frontmatter parsing and writing

## Configuration

**Environment:**
- Today: no required runtime env vars for the native backend
- Planned in v0.2: Firecrawl API key and optional MinerU service configuration for fallback phases

**Build and project config:**
- `pyproject.toml` - Package metadata, dependencies, pytest settings
- `.planning/config.json` - GSD workflow settings for the new milestone

## Platform Requirements

**Development:**
- Windows is the observed local environment, but the code is standard Python and filesystem based
- Network access required only when fetching remote URLs

**Production / execution model:**
- Local CLI or agent-driven execution from the repo root
- File-based state under `content/` and `state/`

---

*Stack analysis: 2026-04-13*
*Update after major dependency or runtime changes*
