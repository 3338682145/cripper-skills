---
status: complete
phase: 02-native-backend-orchestration
source: [02-01-SUMMARY.md]
started: 2026-04-13T16:40:00Z
updated: 2026-04-13T16:50:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Native AUTO_PASS Writes Source Packet
expected: A single article URL produces a `source-packet` in the raw directory with provenance, refs, and markdown body.
result: pass

### 2. Canonical URL Dedupe Reuses Existing Packet
expected: Re-ingesting the same canonical URL with query-order variation returns the existing packet and does not create a second raw file.
result: pass

### 3. REVIEW_REQUIRED Routes to Review
expected: A non-pass baseline verdict writes the packet into the configured review directory instead of the raw directory.
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
