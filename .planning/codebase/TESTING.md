# Testing Patterns

**Analysis Date:** 2026-04-13

## Test Framework

**Runner:**
- pytest
- Config: `pyproject.toml` defines `testpaths = ["tests"]` and disables the cache provider

**Assertion style:**
- Plain pytest `assert`
- CLI tests use `typer.testing.CliRunner`

**Run Commands:**
```bash
uv run pytest -q
uv run pytest tests/integration/test_ingest.py -q
uv run pytest tests/contract/test_registry_validation.py -q
```

## Test File Organization

**Location:**
- Dedicated `tests/` tree

**Naming:**
- Contract tests: `tests/contract/test_*.py`
- Integration tests: `tests/integration/test_*.py`
- Shared fixtures: `tests/fixtures/*`

**Structure:**
```text
tests/
  conftest.py
  contract/
    test_registry_validation.py
    test_raw_asset_validation.py
  integration/
    test_ingest.py
```

## Test Structure

**Patterns:**
- Build a temporary on-disk workspace through `workspace_factory`
- Mock only the network boundary via `monkeypatch`
- Validate filesystem side effects by reading the generated Markdown and JSON outputs
- Use direct `assert` statements on frontmatter fields and body content

## Fixtures and Factories

**Shared fixtures:**
- `tests/conftest.py` injects `src/` into `sys.path`
- `workspace_factory` writes a realistic registry and directory layout into `.tmp-tests/`
- HTML fixture files cover docs-like pages, generic fallback pages, and raw asset validation samples

## Coverage Expectations

- No enforced numeric coverage target today
- Existing tests focus on contract validation and the single-URL ingest path
- The v0.2 milestone should extend this with fallback, verifier, and queue tests before execution claims success

## Current Gaps

- `pytest` is not directly available on the current shell path, so local runs need `uv run` or an activated virtual environment
- There is no dedicated test helper yet for the future optional skill scripts
- No live external-service tests exist yet, which is why Firecrawl and MinerU phases need explicit review gates

---

*Testing analysis: 2026-04-13*
*Update when the optional skill adds new test entrypoints or live-service smoke tests*
