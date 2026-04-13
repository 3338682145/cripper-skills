---
status: complete
phase: 03-firecrawl-fallback
source: [03-01-SUMMARY.md]
started: 2026-04-13T17:25:00Z
updated: 2026-04-13T17:35:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Low-Signal Native Extraction Retries With Firecrawl
expected: A weak native extraction retries through Firecrawl, writes a packet with `backend_used: firecrawl`, and records fallback reason codes.
result: pass

### 2. Missing Firecrawl Key Downgrades to Review
expected: A JS-heavy page without `FIRECRAWL_API_KEY` does not pass silently and instead routes to review with explicit fallback failure reasons.
result: pass

### 3. Native Fetch Failure Can Recover Through Firecrawl
expected: A native HTTP failure can still produce a packet if Firecrawl succeeds, with `native_fetch_failed` recorded in the reason codes.
result: pass

## Summary

total: 3
passed: 3
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

None.
