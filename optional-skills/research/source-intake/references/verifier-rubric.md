# Verifier Rubric

The verifier is a quality gate, not a summarizer.

## Allowed Verdicts

| Verdict | Meaning | Route |
| --- | --- | --- |
| `AUTO_PASS` | Complete, low-noise, durable, and structurally usable | raw |
| `REVIEW_REQUIRED` | Mostly useful, but extraction quality or routing confidence is not stable enough | review |
| `LOW_SIGNAL` | Thin, noisy, or low-value source | review |
| `UNSUPPORTED` | Placeholder or unsupported source type, such as GitHub in v1 | review |

## Required Output Fields

- `verdict`
- `confidence`
- `signal_level`
- `reason_codes`
- `summary`
- `suggested_topic`
- `suggested_kind`

## Core Reason Code Families

- `verifier_*` for verifier-local quality decisions such as `verifier_structured_content`, `verifier_manual_review`, and `verifier_low_word_count`
- `native_*` for native extraction weaknesses such as `native_too_short` or `native_js_heavy_page`
- `firecrawl_*` for fallback triggers and backend failures such as `firecrawl_fallback_used` or `firecrawl_missing_api_key`
- `mineru_*` for PDF/backend failures such as `mineru_backend_used` or `mineru_missing_endpoint`
- `github_placeholder` for explicitly unsupported GitHub placeholder packets

## Guardrails

- do not write wiki pages
- do not generate publishing copy
- do not generate topic dossiers, summaries, or output prose
- do not invent unsupported verdict values
- do not bypass routing policy
