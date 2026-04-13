# Integrations

**Analysis Date:** 2026-04-13

## Current Runtime Integrations

**Remote websites:**
- Boundary: `requests.Session.get()` in `src/cliper/adapters/web_url.py`
- Purpose: Fetch HTML for registered `web_url` sources
- Failure mode: network errors are captured per URL in the run manifest

**Filesystem:**
- Boundary: `Workspace` in `src/cliper/service.py`
- Purpose: Persist registries, raw assets, manifests, indexes, and HTML snapshots
- Constraint: all refs must stay repo-relative and traceable

## Parsing and Extraction Libraries

**BeautifulSoup / lxml:**
- Purpose: DOM parsing and element cleanup

**readability-lxml:**
- Purpose: Generic-page fallback when docs-style extraction is weak

**markdownify:**
- Purpose: Convert extracted HTML fragments to Markdown while preserving code fences and headings

## Project-Level Neighbors

**`llm-wiki/`:**
- Status: sibling package only
- Constraint: conceptual consumer, not a runtime dependency of `cliper`

## Planned v0.2 Integrations

**Firecrawl:**
- Use: fallback backend for JS-heavy or low-signal pages
- Requirement: API key managed outside the repo
- Official reference: https://www.firecrawl.dev/

**MinerU:**
- Use: PDF and complex-document backend
- Requirement: local CLI or service setup managed outside the repo
- Official reference: https://github.com/opendatalab/mineru

**Wiki raw/review destinations:**
- Use: configured output targets for the optional skill layer
- Constraint: must be config-driven and stay outside `cliper` core coupling

---

*Integrations analysis: 2026-04-13*
*Update when new external services or runtime consumers are added*
