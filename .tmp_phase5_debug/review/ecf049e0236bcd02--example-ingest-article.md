---
schema: source-packet
schema_version: 0.1.0
packet_id: ecf049e0236bcd02
source_type: blog_article
input_url: https://example.com/article
canonical_url: https://example.com/article
title: Example Ingest Article
retrieved_at: '2026-04-13T09:41:05Z'
published_at: '2026-04-13T10:00:00Z'
language: en
backend_used: native
backend_version: 0.1.0
content_hash: 70a61ecc659bc042f0fda3ae7321ccf8c5fb4163d9e0ea21813d0f7c8e3477f7
dedupe_key: 632538290468e7a39c06323c9e3ae98f31072d641cbb37ea37917f56bbeb5539
signal_level: low
verdict: REVIEW_REQUIRED
confidence: 0.2
provenance:
  fetch_method: requests.get
  fetch_url: https://example.com/article
  resolved_url: https://example.com/article
  extractor: native-wrapper
  extractor_version: 0.1.0
reason_codes:
- native_too_short
- firecrawl_missing_api_key
- verifier_low_word_count
routing:
  suggested_topic: example-ingest-article
  suggested_kind: blog
refs:
  artifact_dir: E:\ai\harmess-website\cliper\.tmp_phase5_debug\archive\ecf049e0236bcd02
  raw_html: E:\ai\harmess-website\cliper\.tmp_phase5_debug\archive\ecf049e0236bcd02\source.html
  raw_pdf: null
  extracted_json: null
  verifier_report: E:\ai\harmess-website\cliper\.tmp_phase5_debug\archive\ecf049e0236bcd02\verifier-report.json
  source_snapshot: E:\ai\harmess-website\cliper\.tmp_phase5_debug\archive\ecf049e0236bcd02\source.html
---

# Example Ingest Article

This is the first paragraph of the article.

This is the second paragraph with more detail.
