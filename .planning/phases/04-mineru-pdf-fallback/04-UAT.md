---
status: complete
phase: 04-mineru-pdf-fallback
source: [04-01-SUMMARY.md]
started: 2026-04-13T18:15:00Z
updated: 2026-04-13T18:25:00Z
---

## Current Test

[testing complete]

## Tests

### 1. MinerU Wrapper Returns PDF Artifacts
expected: The MinerU wrapper returns a normalized backend payload containing raw PDF bytes, extracted JSON, and markdown content.
result: pass

### 2. Direct PDF URL Routes To MinerU
expected: A `pdf_url` input routes directly to MinerU and persists `raw_pdf`, `extracted_json`, and markdown snapshot refs in the packet archive.
result: pass

### 3. Firecrawl PDF Weakness Escalates To MinerU
expected: A packet already marked with a Firecrawl PDF weakness such as `firecrawl_pdf_table_heavy` escalates to MinerU instead of re-entering native extraction.
result: pass

### 4. Missing MinerU Configuration Produces UNSUPPORTED
expected: A PDF URL without a MinerU path routes to review with `UNSUPPORTED` and explicit `mineru_*` reason codes.
result: pass

## Summary

total: 4
passed: 4
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

None.
