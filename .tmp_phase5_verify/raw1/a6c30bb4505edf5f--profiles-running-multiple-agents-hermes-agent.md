---
schema: source-packet
schema_version: 0.1.0
packet_id: a6c30bb4505edf5f
source_type: docs_page
input_url: https://example.com/docs/profiles
canonical_url: https://example.com/docs/profiles
title: 'Profiles: Running Multiple Agents | Hermes Agent'
retrieved_at: '2026-04-13T09:42:52Z'
published_at: null
language: en
backend_used: native
backend_version: 0.1.0
content_hash: a115c5e52b3a8675b773f7fda44d86b785a1e3c3c0e28145fcc3a66cb7870f83
dedupe_key: c151a61de6c5502e983dbcf5c02c90c2637ee13c1ebf23a952b5c06357322c56
signal_level: high
verdict: AUTO_PASS
confidence: 0.95
provenance:
  fetch_method: requests.get
  fetch_url: https://example.com/docs/profiles
  resolved_url: https://example.com/docs/profiles
  extractor: native-wrapper
  extractor_version: 0.1.0
reason_codes:
- verifier_manual_review
routing:
  suggested_topic: profiles-running-multiple-agents-hermes-agent
  suggested_kind: docs
refs:
  artifact_dir: E:\ai\harmess-website\cliper\.tmp_phase5_verify\archive1\a6c30bb4505edf5f
  raw_html: E:\ai\harmess-website\cliper\.tmp_phase5_verify\archive1\a6c30bb4505edf5f\source.html
  raw_pdf: null
  extracted_json: null
  verifier_report: E:\ai\harmess-website\cliper\.tmp_phase5_verify\archive1\a6c30bb4505edf5f\verifier-report.json
  source_snapshot: E:\ai\harmess-website\cliper\.tmp_phase5_verify\archive1\a6c30bb4505edf5f\source.html
---

# Profiles: Running Multiple Agents

Run multiple independent Hermes agents on the same machine.

## What are profiles?

A profile is a fully isolated Hermes environment with its own config, sessions, skills, and memory.

## Quick start

```bash
hermes profile create coder
coder setup
coder chat
```

## Creating a profile

### Blank profile

Create a fresh profile with bundled skills seeded.

## Using profiles

### Command aliases

Each profile becomes its own command alias.

## Running gateways

### Different bot tokens

Profiles can run gateways with separate bot tokens.

## Configuring profiles

Each profile has its own config.yaml, .env, and SOUL.md.

## How it works

Profiles are isolated directories under the Hermes home directory.
