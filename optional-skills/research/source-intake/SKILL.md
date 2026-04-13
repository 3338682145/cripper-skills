---
name: source-intake
description: "Convert a URL into a traceable source packet using native Cliper extraction first, then optional fallback backends and verifier-driven routing."
version: 0.1.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags:
      - Research
      - Ingestion
      - Web
      - PDF
      - Wiki
    related_skills:
      - wiki
    config:
      - key: wiki.path
        description: llm-wiki root directory
        default: "~/wiki"
      - key: source_intake.review_dir
        description: review and staging directory for non-pass packets
        default: "~/.hermes/intake/review"
      - key: source_intake.archive_dir
        description: archive directory for intermediate artifacts
        default: "~/.hermes/intake/archive"
      - key: source_intake.default_backend
        description: default backend before fallback logic
        default: "native"
      - key: source_intake.github_mode
        description: GitHub URL handling strategy
        default: "placeholder"
required_environment_variables:
  - name: FIRECRAWL_API_KEY
    prompt: Firecrawl API key
    required_for: Firecrawl fallback backend
---

# Source Intake

The `source-intake` skill is the intake layer for durable source material. It accepts a URL, classifies the source, runs a backend, normalizes the result into a Markdown `source-packet`, verifies quality, and routes the packet to either a raw inbox or a review directory.

## Scope

- Primary path: native Cliper extraction
- Fallback paths: Firecrawl for difficult web pages, MinerU for PDF and complex documents
- Routing: `AUTO_PASS` packets can move to wiki raw, everything else goes to review
- GitHub URLs are placeholder-only in v1

## Main Entry Point

- `scripts/intake_url.py` - orchestrates classify -> backend -> normalize -> verify -> route
- packaged CLI: `source-intake`
- packaged cron CLI: `source-intake-cron`
- packaged wizard CLI: `source-intake-wizard`

## Helper Scripts

- `scripts/classify_url.py` - source type classification
- `scripts/run_native_backend.py` - native Cliper backend wrapper
- `scripts/run_firecrawl_backend.py` - Firecrawl fallback wrapper
- `scripts/run_mineru_backend.py` - MinerU PDF wrapper
- `scripts/normalize_packet.py` - `source-packet` normalization
- `scripts/verify_packet.py` - quality gate verdicts
- `scripts/route_packet.py` - raw vs review routing
- `scripts/cron_drain_queue.py` - queue and cron batch runner

## External Dependencies

- Firecrawl: configure `FIRECRAWL_API_KEY` before Phase 3 implementation
- MinerU: install a local CLI or service before Phase 4 implementation
- See `references/backend-matrix.md` for the official dependency references and operator expectations

## References

- `references/backend-matrix.md` - backend selection and escalation rules
- `references/packet-contract.md` - required `source-packet` frontmatter
- `references/verifier-rubric.md` - verdict definitions and reason-code intent
- `references/examples.md` - representative source flows
- `README.md` - packaging and direct-call guide in English
- `README.zh-CN.md` - packaging and direct-call guide in Simplified Chinese

## Install As An Agent Skill

1. Copy this whole folder into your agent's skill root as `source-intake`
2. Keep `SKILL.md` at the root of the copied folder
3. Keep the `references/` folder next to it
4. Invoke it in your agent by referencing `source-intake`
5. Or run `install-skill.ps1` to install into any agent skill directory
6. `install-to-codex.ps1` / `install-to-codex.cmd` are just Codex convenience wrappers
7. Use `install-runtime.ps1` if you want skill files plus executable runtime in one step

## Operating Rules

- Keep `cliper` as ingestion-only native backend
- Preserve provenance for every packet and archived artifact
- Add migration notes before changing contract meaning
- Never route low-confidence content directly into wiki raw
