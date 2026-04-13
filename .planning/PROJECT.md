# Hermes Cliper

## What This Is

Hermes Cliper is the ingestion repository and native extraction backend for Hermes. In milestone `v0.2`, the repo also becomes the brownfield planning base for a `source-intake` optional skill that packages native extraction, fallback backends, verifier-driven routing, and cron automation without collapsing the boundary between ingestion, knowledge linking, and output.

## Core Value

Every downstream content artifact must be traceable back to a validated source packet or raw source asset with durable provenance.

## Current Milestone: v0.2 Source Intake Skill

**Goal:** Turn the existing contract-first ingestion spine into the native backend for a reusable Hermes optional skill.

**Target features:**
- An optional skill package under `optional-skills/research/source-intake/`
- A normalized `source-packet` contract layered on top of the existing `cliper` primitives
- Native, Firecrawl, and MinerU backend selection with verifier-based routing
- Queue and cron orchestration for sustained source intake
- A GitHub placeholder adapter that preserves the v1 scope boundary

## Requirements

### Validated

- [x] A contract-first CLI exists for registry validation, ingestion, and validation gates
- [x] Markdown registries, raw assets, run manifests, and HTML snapshots are stored on disk with traceable refs
- [x] A `web_url` adapter can extract docs-like and generic article pages into Markdown
- [x] A discoverable optional skill package skeleton exists with stable script names and source-intake reference docs
- [x] A single-URL source-intake path can classify URLs, reuse native `cliper` extraction, and write provenance-rich `source-packet` files with archive refs
- [x] Firecrawl fallback now covers low-signal, JS-heavy, and native-failure web pages with explicit reason codes
- [x] MinerU fallback now covers direct PDF intake and complex-document escalation with traceable packet artifacts
- [x] Verifier-based routing and cron queue draining now enforce one durable intake policy across manual and queued runs
- [x] GitHub URLs now degrade to explicit placeholder packets instead of drifting into repository ingestion

### Active

- [ ] Phase 7: backfill `VERIFICATION.md` evidence and formally re-close all v0.2 requirements
- [ ] Phase 8: add `VALIDATION.md`, runnable verification commands, and live Firecrawl/MinerU smoke evidence, then re-audit the milestone

### Out of Scope

- Knowledge linking inside `cliper`, still delegated to `llm-wiki`
- Publishing directly from raw packets or raw assets
- Browser-automation backends in `cliper`
- Database-backed intake state management
- Full GitHub repository ingestion in v1

## Context

The repository already shipped a Milestone 1A bootstrap: contracts, registries, one executable `web_url` path, run manifests, and validation gates. The new milestone does not replace that work. It preserves `cliper` as the native backend and adds an optional-skill layer that can route into wiki raw or review destinations only after packet normalization and verifier gating.

## Constraints

- **Architecture**: `cliper` remains ingestion-only. The optional skill may write into configured wiki inboxes, but `cliper` core must not become a wiki compiler.
- **Traceability**: every packet or asset must preserve canonical URL, hashes, provenance, archive refs, and routing evidence.
- **Schema governance**: contract changes require migration notes under `docs/migrations/`.
- **Brownfield reality**: the repo already contains CLI, models, extraction logic, and tests that must be reused as the native backend.
- **Execution safety**: Firecrawl and MinerU phases need human checkpoints for credentials or local service setup, especially on Windows.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Start a new milestone instead of mutating the legacy roadmap in place | Avoid two conflicting roadmaps that describe different products | Approved |
| Keep `cliper` runtime as the native backend | Reuse current extraction, dedupe, and manifest primitives instead of rewriting them in the skill | Approved |
| Introduce `source-packet` as an additive contract | Preserve current raw-asset stability while enabling richer routing and verifier metadata | Approved |
| Treat Firecrawl and MinerU as fallbacks, not the mainline backend | Native extraction should stay the default for deterministic, low-cost ingestion | Approved |
| Only `AUTO_PASS` may enter the wiki raw inbox | Protect downstream knowledge systems from low-signal or unsupported inputs | Approved |
| Keep GitHub ingestion at placeholder-only in v1 | Prevent scope drift into repository crawling before the core packet flow is stable | Approved |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition:**
1. Move validated milestone requirements from Active to Validated with a phase reference.
2. Record any new contract or routing decisions under Key Decisions.
3. Update Context if the repository boundary has shifted or if a fallback backend changed the operating model.
4. Record new blockers only when they materially affect the next phase.

**After each milestone:**
1. Review What This Is and Core Value for product drift.
2. Archive milestone outcomes and replace Current Milestone with the next active milestone.
3. Audit Out of Scope to confirm deferred items still belong outside the repo.

---
*Last updated: 2026-04-13 during milestone reset to v0.2 Source Intake Skill*
