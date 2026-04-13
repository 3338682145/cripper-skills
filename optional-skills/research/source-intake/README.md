# Source Intake Skill

`source-intake` packages the Hermes URL-to-packet intake flow as both:

- a Hermes optional skill described by [`SKILL.md`](./SKILL.md)
- a Python-distributed command surface that can be called directly after install

The runtime path stays the same:

`classify -> native/Firecrawl/MinerU -> normalize -> verify -> route`

## What Gets Packaged

When you build the repo package, the following direct-call commands are included:

- `source-intake`
- `source-intake-cron`
- `source-intake-wizard`
- `cliper source-intake run`
- `cliper source-intake cron`
- `cliper source-intake wizard`

The Hermes skill manifest and operator references stay in this folder:

- [`SKILL.md`](./SKILL.md)
- [`references/backend-matrix.md`](./references/backend-matrix.md)
- [`references/packet-contract.md`](./references/packet-contract.md)
- [`references/verifier-rubric.md`](./references/verifier-rubric.md)
- [`references/examples.md`](./references/examples.md)

## Quick Start

From the repo root:

```bash
uv sync
uv run source-intake "https://example.com/post" \
  --raw-dir ./llm-wiki/docs/raw \
  --review-dir ~/.hermes/intake/review \
  --archive-dir ~/.hermes/intake/archive
```

Queued cron-style drain:

```bash
uv run source-intake-cron \
  --raw-dir ./llm-wiki/docs/raw \
  --review-dir ~/.hermes/intake/review \
  --archive-dir ~/.hermes/intake/archive
```

Interactive parameter wizard:

```bash
uv run source-intake-wizard
uv run cliper source-intake wizard
```

Equivalent calls through the main CLI:

```bash
uv run cliper source-intake run "https://example.com/post" \
  --raw-dir ./llm-wiki/docs/raw \
  --review-dir ~/.hermes/intake/review \
  --archive-dir ~/.hermes/intake/archive

uv run cliper source-intake cron \
  --raw-dir ./llm-wiki/docs/raw \
  --review-dir ~/.hermes/intake/review \
  --archive-dir ~/.hermes/intake/archive
```

## Build A Package

From the repo root:

```bash
uv build
```

This creates `dist/` artifacts for the `cliper` package. After that you can install the wheel and call the skill directly:

```bash
pip install dist/cliper-*.whl
source-intake "https://example.com/post" \
  --raw-dir ./llm-wiki/docs/raw \
  --review-dir ~/.hermes/intake/review \
  --archive-dir ~/.hermes/intake/archive
```

## Required Inputs

Direct intake requires these paths:

- `--raw-dir`
- `--review-dir`
- `--archive-dir`

Optional overrides:

- `--verdict`
- `--confidence`
- `--signal-level`
- `--reason-code`
- `--suggested-topic`
- `--suggested-kind`
- `--queue-path` for cron mode

The wizard enforces required fields:

- `URL` for `run` mode
- `--raw-dir`
- `--review-dir`
- `--archive-dir`

Optional fields can be left blank in the wizard and will simply be omitted from the generated command.

## Load As A Codex Skill

Copy the skill folder into your Codex home:

```powershell
Copy-Item -Recurse -Force .\optional-skills\research\source-intake "$env:USERPROFILE\.codex\skills\source-intake"
```

After that, keep this structure:

- `%USERPROFILE%\.codex\skills\source-intake\SKILL.md`
- `%USERPROFILE%\.codex\skills\source-intake\references\...`

Then you can call it as a local skill in Codex. The packaged CLI commands and the skill manifest can coexist; the skill provides the operator guidance, while the package provides the executable commands.

## External Dependencies

Optional only:

- `FIRECRAWL_API_KEY` for Firecrawl fallback
- `MINERU_ENDPOINT` for MinerU HTTP or CLI mode
- `MINERU_BACKEND` when you need to pass a MinerU backend selector to the CLI

Without Firecrawl or MinerU configured, the skill still runs but degrades to review-safe behavior instead of silently passing.

## README Strategy

This skill now keeps separate operator docs by language:

- English: [`README.md`](./README.md)
- Simplified Chinese: [`README.zh-CN.md`](./README.zh-CN.md)

Recommended practice:

- keep command examples identical across both files
- keep terms like `source-packet`, `AUTO_PASS`, and `UNSUPPORTED` untranslated
- update both files in the same change whenever CLI flags or packaging steps change

## Scope Guardrails

- `cliper` remains ingestion-only
- the skill may route packets into raw or review inboxes, but does not compile wiki pages
- GitHub URLs remain placeholder-only in v1
- migration notes are required before changing contract meaning
