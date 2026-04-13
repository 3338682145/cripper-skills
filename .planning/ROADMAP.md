# Roadmap: Hermes Cliper v0.2

## Overview

Use the existing `cliper` ingestion spine as the native backend for a Hermes `source-intake` optional skill. The milestone flows from package skeleton to native orchestration, then to fallback backends, verifier-driven routing, cron automation, and a tightly scoped GitHub placeholder adapter.

## Phases

- [x] **Phase 1: Skill Skeleton** - Create the optional skill package, script entrypoints, and contract reference docs.
- [x] **Phase 2: Native Backend Orchestration** - Reuse current `cliper` primitives to produce normalized `source-packet` output and baseline routing.
- [x] **Phase 3: Firecrawl Fallback** - Add fallback routing for low-signal and JS-heavy pages using Firecrawl.
- [x] **Phase 4: MinerU PDF Fallback** - Add PDF and complex-document handling with MinerU and artifact governance.
- [x] **Phase 5: Verifier + Cron** - Add verdicts, raw/review routing, queue draining, and cron behavior.
- [x] **Phase 6: GitHub Placeholder Adapter** - Add placeholder-only GitHub handling without deep ingestion.
- [ ] **Phase 7: Verification Evidence Backfill** - Add formal phase verification artifacts and requirement coverage evidence for Phases 1-6.
- [ ] **Phase 8: Validation and Live Smoke Coverage** - Add Nyquist validation artifacts, runnable test evidence, and live fallback smoke records.

## Phase Details

### Phase 1: Skill Skeleton
**Goal**: Stand up a discoverable optional skill package with the scripts and references the later phases build on.
**Depends on**: Nothing (first phase)
**Requirements**: [SKILL-01, SKILL-02]
**Canonical refs**:
- `PLAN.md` — reviewed source-intake design
- `AGENTS.md` — repo boundaries and validation rules
- `.planning/codebase/ARCHITECTURE.md` — current backend architecture
**Success Criteria** (what must be TRUE):
  1. `optional-skills/research/source-intake/` exists with a valid `SKILL.md`.
  2. The skill documents config keys, env vars, backend matrix, packet contract, verifier rubric, and examples.
  3. Placeholder script entrypoints exist for every planned backend and orchestration step.
**Plans**: 1 plan

Plans:
- [x] 01-01: Scaffold the optional skill package, helper scripts, and reference docs

### Phase 2: Native Backend Orchestration
**Goal**: Turn the current `cliper` code into a reusable native backend that emits `source-packet` output.
**Depends on**: Phase 1
**Requirements**: [NATIVE-01, NATIVE-02, PACKET-01, PACKET-02, GOV-01]
**Canonical refs**:
- `src/cliper/service.py` — current orchestration and manifest logic
- `src/cliper/models.py` — current contract layer
- `docs/migrations/README.md` — migration-note policy
**Success Criteria** (what must be TRUE):
  1. A single URL can flow through classify -> native backend -> normalize -> route.
  2. The resulting Markdown follows the `source-packet` contract.
  3. Archive refs are captured without polluting the wiki raw inbox.
**Plans**: 1 plan

Plans:
- [x] 02-01: Build native orchestration, packet normalization, and baseline routing

### Phase 3: Firecrawl Fallback
**Goal**: Add a deterministic fallback path for pages the native backend cannot extract well.
**Depends on**: Phase 2
**Requirements**: [FALLBACK-01]
**Canonical refs**:
- `optional-skills/research/source-intake/references/backend-matrix.md` — backend decision rules
- `src/cliper/adapters/web_url.py` — native extraction quality signals
- `.planning/codebase/INTEGRATIONS.md` — current and planned external services
**Success Criteria** (what must be TRUE):
  1. Native low-signal results can retry with Firecrawl.
  2. JS-heavy or structurally incomplete pages reach a documented fallback path.
  3. Firecrawl failures surface explicit reason codes and never silently pass.
**Plans**: 1 plan

Plans:
- [x] 03-01: Add Firecrawl backend wrapper, heuristics, and fallback tests

### Phase 4: MinerU PDF Fallback
**Goal**: Handle PDF and complex document flows with explicit artifact management and fallback rules.
**Depends on**: Phase 3
**Requirements**: [FALLBACK-02]
**Canonical refs**:
- `optional-skills/research/source-intake/references/backend-matrix.md` — PDF routing rules
- `optional-skills/research/source-intake/references/packet-contract.md` — archive refs and packet fields
- `.planning/codebase/CONCERNS.md` — current external-service risks
**Success Criteria** (what must be TRUE):
  1. PDF URLs can route to MinerU.
  2. Firecrawl PDF failures can escalate to MinerU.
  3. Raw PDF, extracted JSON, and verifier refs remain traceable from the packet.
**Plans**: 1 plan

Plans:
- [x] 04-01: Add MinerU backend integration, PDF routing, and artifact governance

### Phase 5: Verifier + Cron
**Goal**: Add the quality gate and automation layer that moves high-signal packets to raw and low-confidence packets to review.
**Depends on**: Phase 4
**Requirements**: [VERIFY-01, ROUTE-01, ROUTE-02, CRON-01]
**Canonical refs**:
- `optional-skills/research/source-intake/references/verifier-rubric.md` — verdict criteria
- `optional-skills/research/source-intake/references/packet-contract.md` — routing fields
- `docs/validation/contract-gates.md` — migration and validation expectations
**Success Criteria** (what must be TRUE):
  1. The verifier emits only the approved verdicts and metadata fields.
  2. Raw/review routing and dedupe are enforced across single-run and queued intake.
  3. Empty cron runs return `[SILENT]` and non-empty runs summarize verdict counts.
**Plans**: 1 plan

Plans:
- [x] 05-01: Implement verifier verdicts, route enforcement, and cron queue draining

### Phase 6: GitHub Placeholder Adapter
**Goal**: Recognize GitHub URLs without letting scope expand into repository ingestion.
**Depends on**: Phase 5
**Requirements**: [GITHUB-01]
**Canonical refs**:
- `PLAN.md` — locked v1 scope boundary
- `optional-skills/research/source-intake/references/examples.md` — placeholder examples
- `.planning/codebase/CONCERNS.md` — scope-drift risks
**Success Criteria** (what must be TRUE):
  1. GitHub URLs are classified explicitly.
  2. The system writes placeholder packets with `UNSUPPORTED` verdict.
  3. No GitHub flow attempts repository crawling, wiki compilation, or output generation.
**Plans**: 1 plan

Plans:
- [x] 06-01: Add GitHub URL classification and placeholder packet routing

### Phase 7: Verification Evidence Backfill
**Goal**: Close the milestone audit blocker by turning implemented Phase 1-6 behavior into formal verification evidence with requirement coverage.
**Depends on**: Phase 6
**Requirements**: [SKILL-01, SKILL-02, NATIVE-01, NATIVE-02, PACKET-01, PACKET-02, GOV-01, FALLBACK-01, FALLBACK-02, VERIFY-01, ROUTE-01, ROUTE-02, CRON-01, GITHUB-01]
**Gap Closure**: Closes orphaned requirement evidence and missing `VERIFICATION.md` artifacts from `.planning/v0.2-MILESTONE-AUDIT.md`
**Canonical refs**:
- `.planning/v0.2-MILESTONE-AUDIT.md` - audit blockers and orphaned requirement evidence
- `.planning/phases/*/*-SUMMARY.md` - implemented scope claims that now need formal verification
- `.planning/phases/*/*-UAT.md` - existing test evidence to fold into verification reports
**Success Criteria** (what must be TRUE):
  1. Every Phase 1-6 directory has a `VERIFICATION.md` with requirement status, evidence, and open gaps.
  2. Phase 1 has explicit verification coverage instead of summary-only evidence.
  3. `REQUIREMENTS.md` can restore all milestone REQ-IDs to formally satisfied after verification is complete.
**Plans**: 1 plan

Plans:
- [ ] 07-01: Backfill formal verification artifacts and re-close requirement evidence for Phases 1-6

### Phase 8: Validation and Live Smoke Coverage
**Goal**: Close Nyquist and operational evidence gaps by adding validation artifacts, runnable test evidence, and live fallback smoke coverage.
**Depends on**: Phase 7
**Requirements**: []
**Gap Closure**: Closes missing `VALIDATION.md`, missing executable test-runner evidence, and missing live Firecrawl/MinerU smoke records from `.planning/v0.2-MILESTONE-AUDIT.md`
**Canonical refs**:
- `.planning/v0.2-MILESTONE-AUDIT.md` - validation and flow evidence gaps
- `.planning/config.json` - `workflow.nyquist_validation: true`
- `tests/integration/` - mocked evidence that must be promoted into runnable validation coverage
**Success Criteria** (what must be TRUE):
  1. Every Phase 1-6 directory has a `VALIDATION.md` or explicit Nyquist discovery result.
  2. The active environment has a documented runnable command for repo verification instead of harness-only fallback.
  3. Firecrawl and MinerU each have one recorded live smoke result or a formal environment-blocked validation artifact.
**Plans**: 1 plan

Plans:
- [ ] 08-01: Add validation artifacts, runnable verification commands, and live fallback smoke evidence

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Skill Skeleton | 1/1 | Completed | 2026-04-13 |
| 2. Native Backend Orchestration | 1/1 | Completed | 2026-04-13 |
| 3. Firecrawl Fallback | 1/1 | Completed | 2026-04-13 |
| 4. MinerU PDF Fallback | 1/1 | Completed | 2026-04-13 |
| 5. Verifier + Cron | 1/1 | Completed | 2026-04-13 |
| 6. GitHub Placeholder Adapter | 1/1 | Completed | 2026-04-13 |
| 7. Verification Evidence Backfill | 0/1 | Pending | - |
| 8. Validation and Live Smoke Coverage | 0/1 | Pending | - |
