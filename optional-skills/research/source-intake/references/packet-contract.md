# Source-Packet Contract

`source-packet` is the normalized Markdown contract produced by the `source-intake` skill.

## File Naming

```text
<packet_id>--<slug>.md
```

## Required Frontmatter

```yaml
---
schema: source-packet
schema_version: 0.1.0
packet_id: <stable id>
source_type: <blog_article|docs_page|paper_page|pdf_url|github_repo|unknown>
input_url: <original input url>
canonical_url: <normalized canonical url>
title: <resolved title>
retrieved_at: <ISO8601 UTC>
published_at: <optional>
language: <optional>
backend_used: <native|firecrawl|mineru|github_placeholder>
backend_version: <string>
content_hash: <sha256 of normalized body>
dedupe_key: <sha256 of canonical_url>
signal_level: <high|medium|low>
verdict: <AUTO_PASS|REVIEW_REQUIRED|LOW_SIGNAL|UNSUPPORTED>
confidence: <0.00-1.00>
provenance:
  fetch_method: <requests.get or backend fetch method>
  fetch_url: <original fetch url>
  resolved_url: <final resolved url>
  extractor: <native|firecrawl|mineru wrapper name>
  extractor_version: <backend version>
reason_codes:
  - <verifier reason>
routing:
  suggested_topic: <string or null>
  suggested_kind: <docs|blog|paper|reference|null>
refs:
  artifact_dir: <archive dir>
  raw_html: <optional path>
  raw_pdf: <optional path for MinerU PDF flows>
  extracted_json: <optional path for MinerU structured output>
  verifier_report: <path>
  source_snapshot: <optional path, often the extracted markdown snapshot>
---
```

## Archive Rules

- intermediate artifacts live under the configured `artifact_dir`
- wiki raw should receive only the normalized packet, not the whole archive
- refs must stay traceable even when the packet routes to review
- MinerU flows should preserve `raw_pdf`, `extracted_json`, and a markdown `source_snapshot`

## Routing Rules

- only `AUTO_PASS` may land in the configured raw inbox
- `REVIEW_REQUIRED`, `LOW_SIGNAL`, and `UNSUPPORTED` must land in the review directory
- queue and cron runs must reuse the same packet verification and routing policy as manual intake

## Compatibility Rule

`source-packet` is additive to the current `raw-asset` contract. It does not authorize deleting or silently redefining the existing Cliper raw asset semantics.
