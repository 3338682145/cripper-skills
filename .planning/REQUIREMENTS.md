# Hermes Cliper Requirements

## Milestone v0.2 — Source Intake Skill

This milestone turns the existing `cliper` ingestion spine into the native backend for a Hermes optional skill. The milestone is successful only when the skill package, packet contract, fallback backends, verifier routing, cron path, and GitHub placeholder adapter are all planned and ready for phased execution.

Audit status (2026-04-13): 0/14 milestone requirements are formally satisfied right now. The implementation exists, but all v0.2 requirements are pending re-verification in Phase 7 after the milestone audit flagged missing `VERIFICATION.md` evidence.

## v1 Requirements

### Skill Packaging

- [ ] **SKILL-01**: Hermes MUST ship an optional skill package at `optional-skills/research/source-intake/` with valid skill metadata, config keys, and required environment variables.
- [ ] **SKILL-02**: The skill package MUST include helper script entrypoints and reference docs for backend selection, packet contract, verifier rubric, and examples.

### Native Orchestration

- [ ] **NATIVE-01**: A single URL intake entrypoint MUST classify a source, invoke the native `cliper` extraction path, and normalize the result into a `source-packet`.
- [ ] **NATIVE-02**: Existing `cliper` registry, extraction, dedupe, and manifest primitives MUST remain reusable as the native backend instead of being reimplemented from scratch in the skill.

### Packet Contract

- [ ] **PACKET-01**: The system MUST output a Markdown `source-packet` contract with stable provenance, routing, backend, verdict, dedupe, and refs metadata.
- [ ] **PACKET-02**: Intermediate artifacts MUST be archived outside the wiki raw inbox and referenced from packet frontmatter.

### Fallback Backends

- [ ] **FALLBACK-01**: Native extraction MUST retry with Firecrawl when the extracted content is too short, too noisy, structurally incomplete, or clearly JS-heavy.
- [ ] **FALLBACK-02**: PDF and complex document URLs MUST route to MinerU, including fallback from poor Firecrawl PDF extraction.

### Verifier and Routing

- [ ] **VERIFY-01**: A verifier MUST return only `AUTO_PASS`, `REVIEW_REQUIRED`, `LOW_SIGNAL`, or `UNSUPPORTED`, plus confidence, signal level, reason codes, and a short reviewer summary.
- [ ] **ROUTE-01**: Only `AUTO_PASS` packets MUST land in the configured wiki raw inbox. All other verdicts MUST land in the configured review directory.
- [ ] **ROUTE-02**: Dedupe on `canonical_url` MUST apply consistently across raw writes, review writes, and queued cron items.

### Automation and GitHub

- [ ] **CRON-01**: Queue draining and manual single-URL intake MUST share one processing pipeline, and empty cron runs MUST return `[SILENT]`.
- [ ] **GITHUB-01**: GitHub URLs MUST produce placeholder packets with `UNSUPPORTED` verdict and MUST NOT do deep repository ingestion in v1.

### Governance

- [ ] **GOV-01**: Contract or schema changes MUST add migration notes and preserve the AGENTS.md boundary that `cliper` handles ingestion only.

## Future Requirements

- [ ] Manual clip and human-review workflows for difficult pages
- [ ] Browser-driven fallback extraction
- [ ] Full GitHub repository ingestion
- [ ] Topic linking or wiki entity generation in downstream systems

## Out of Scope

- Publishing directly from raw packets or raw assets
- `llm-wiki` runtime ownership inside `cliper`
- Database-backed queue state
- Automated account setup for external services such as Firecrawl or MinerU

## Traceability

| Requirement | Phase | Notes |
|-------------|-------|-------|
| SKILL-01 | Phase 7 | Pending re-verification of skill package metadata and directory layout |
| SKILL-02 | Phase 7 | Pending re-verification of script entrypoints and reference docs |
| NATIVE-01 | Phase 7 | Pending re-verification of single-URL orchestration using current `cliper` logic |
| NATIVE-02 | Phase 7 | Pending re-verification of reuse of current services and manifests |
| PACKET-01 | Phase 7 | Pending re-verification of the `source-packet` frontmatter contract |
| PACKET-02 | Phase 7 | Pending re-verification of archive refs and artifact storage rules |
| GOV-01 | Phase 7 | Pending re-verification of migration notes and boundary preservation |
| FALLBACK-01 | Phase 7 | Pending re-verification of Firecrawl fallback heuristics |
| FALLBACK-02 | Phase 7 | Pending re-verification of MinerU routing and artifact handling |
| VERIFY-01 | Phase 7 | Pending re-verification of the verifier verdict contract |
| ROUTE-01 | Phase 7 | Pending re-verification of raw vs review routing |
| ROUTE-02 | Phase 7 | Pending re-verification of dedupe across routes and queue |
| CRON-01 | Phase 7 | Pending re-verification of queue and cron behavior |
| GITHUB-01 | Phase 7 | Pending re-verification of placeholder-only GitHub handling |
