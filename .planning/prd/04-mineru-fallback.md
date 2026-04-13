# PRD: Phase 4 MinerU PDF Fallback

## Goal

Handle PDF and complex-document ingestion through MinerU, including fallback from low-quality Firecrawl PDF output.

## In Scope

- MinerU backend wrapper script
- PDF routing and escalation rules
- Artifact archive handling for raw PDF and extracted JSON/Markdown
- Local-service or CLI setup notes for operators
- Mocked integration tests plus an interactive setup checkpoint

## Out of Scope

- Verifier verdict routing
- Queue draining
- GitHub handling

## Acceptance Criteria

1. PDF URLs can route directly to MinerU.
2. Firecrawl PDF quality failures can escalate to MinerU.
3. Packet refs capture raw PDF, extracted output, and backend logs in a traceable way.

## Canonical Refs

- `optional-skills/research/source-intake/references/backend-matrix.md`
- `optional-skills/research/source-intake/references/packet-contract.md`
- `.planning/codebase/CONCERNS.md`
- MinerU official repository: <https://github.com/opendatalab/mineru>
