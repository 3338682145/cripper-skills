---
schema: source-packet
schema_version: 0.1.0
packet_id: 32e710a4983a32fc
source_type: pdf_url
input_url: https://example.com/report.pdf
canonical_url: https://example.com/report.pdf
title: Source intake needs review
retrieved_at: '2026-04-13T09:23:19Z'
published_at: null
language: unknown
backend_used: mineru
backend_version: mineru
content_hash: bba5749d204db7906372aa2267ab0983a07bfab8c2d9b168594195fcc93ddaea
dedupe_key: b66fe2bbabf606188d08161c6d45267fd3e90dae87aaaa7785533002bf1309ad
signal_level: low
verdict: UNSUPPORTED
confidence: 0.15
provenance:
  fetch_method: requests.get
  fetch_url: https://example.com/report.pdf
  resolved_url: https://example.com/report.pdf
  extractor: mineru-wrapper
  extractor_version: mineru
reason_codes:
- pdf_direct_to_mineru
- mineru_missing_endpoint
routing:
  suggested_topic: null
  suggested_kind: null
refs:
  artifact_dir: E:\ai\harmess-website\cliper\.tmp_phase4_verify\archive3\32e710a4983a32fc
  raw_html: null
  raw_pdf: null
  extracted_json: null
  verifier_report: E:\ai\harmess-website\cliper\.tmp_phase4_verify\archive3\32e710a4983a32fc\verifier-report.json
  source_snapshot: null
---

# PDF intake unsupported

The configured intake backends did not produce a trusted extraction.

## Reason Codes
- pdf_direct_to_mineru
- mineru_missing_endpoint
