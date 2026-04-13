# Concerns

**Analysis Date:** 2026-04-13

## Architectural Concerns

- `src/cliper/service.py` currently owns registry loading, dedupe, output writes, and manifest generation in one module. That is fine for the bootstrap, but the optional-skill work will need cleaner reuse seams for a native backend wrapper.
- The current on-disk contract is `raw-asset`, while the milestone introduces `source-packet`. Without explicit migration notes and compatibility language, it would be easy to create two competing contracts.

## Operational Concerns

- Test execution is slightly fragile in the current environment because `pytest` is not directly on the shell path.
- External services planned for v0.2, especially Firecrawl and MinerU, add credentials, CLI tooling, or local-service setup that the current repo has never needed.
- Wiki raw/review routing risks violating the repo boundary if that logic is pushed into `cliper` core instead of the optional skill layer.

## Scope Concerns

- GitHub ingestion can easily explode into repository crawling, code parsing, or browser automation. The v1 placeholder boundary needs to stay explicit in docs and plans.
- Verifier work can drift into summarization or wiki curation unless its output contract stays tightly constrained.
- Queue and cron work can become a second state system if they stop sharing the same single-URL pipeline.

## Quality Concerns

- Native extraction quality heuristics are currently implicit in DOM scoring and readability fallback. Later fallback phases need explicit signals and reason codes.
- There is no codebase abstraction yet for archive directories or cross-backend artifact refs.
- Existing tests cover the happy native path well, but they do not yet cover multi-backend routing, verdict gating, or cron behavior.

---

*Concern analysis: 2026-04-13*
*Update when the milestone retires or introduces major risks*
