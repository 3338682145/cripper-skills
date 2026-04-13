# Backend Matrix

This document defines which backend the `source-intake` skill should use for each source class and when escalation is allowed.

## Official Dependency References

- Firecrawl official site: <https://www.firecrawl.dev/>
- MinerU official repository: <https://github.com/opendatalab/mineru>

## Operator Setup Notes

### Firecrawl

- Requires `FIRECRAWL_API_KEY`
- The official Firecrawl site describes it as a service to search, scrape, crawl, and extract websites into LLM-ready markdown or structured data
- Treat Firecrawl as a fallback backend, not the default path
- Phase 3 should wire the wrapper to the official Firecrawl API path and keep credential failures explicit

### MinerU

- Official project describes MinerU as a document parsing engine that converts PDF, Word, PPT, images, and web pages into structured Markdown or JSON
- The official MinerU repository also documents CLI, REST API, Docker, and WebUI paths, plus local parsing support for PDF, image, and DOCX inputs
- Official quick-start examples include `mineru -p <input_path> -o <output_path>` and `mineru -p <input_path> -o <output_path> -b pipeline` for pure CPU runs
- Plan on a local CLI or service install before Phase 4
- Keep MinerU behind the PDF and complex-document path only

## Default Source Routing

| Source type | Default backend | Notes |
| --- | --- | --- |
| `blog_article` | `native` | Use current Cliper extraction first |
| `docs_page` | `native` | Prefer docs-aware DOM extraction |
| `paper_page` | `native` | Start from landing page, escalate later if needed |
| `pdf_url` | `mineru` | PDF is a MinerU-first path in v1 |
| `github_repo` | `github_placeholder` | Placeholder only |
| `unknown` | `native` | Try native first, route to review if quality is weak |

## Escalation Rules

### Native -> Firecrawl

Escalate from `native` to `Firecrawl` when one or more of these are true:

- extracted body is too short to be trusted: `native_too_short`
- heading structure is incomplete: `native_heading_structure_incomplete`
- noise ratio is high: `native_noise_ratio_high`
- the page is JS-heavy: `native_js_heavy_page`
- native extraction fails outright: `native_fetch_failed`

If Firecrawl itself fails, surface one of these explicit fallback reasons and route to review:

- `firecrawl_missing_api_key`
- `firecrawl_unauthorized`
- `firecrawl_rate_limited`
- `firecrawl_request_failed`
- `firecrawl_invalid_response`
- `firecrawl_empty_content`

### Firecrawl -> MinerU

Escalate from `Firecrawl` to `MinerU` when one or more of these are true:

- the source is a PDF: `pdf_direct_to_mineru`
- Firecrawl PDF output is too weak to normalize confidently: `firecrawl_pdf_too_weak`
- the document is scan-heavy: `firecrawl_pdf_scan_heavy`
- the layout is multi-column: `firecrawl_pdf_multi_column`
- the document is table-heavy: `firecrawl_pdf_table_heavy`
- the document is formula-heavy: `firecrawl_pdf_formula_heavy`

If MinerU itself is unavailable or fails, surface one of these reasons and route to review:

- `mineru_missing_endpoint`
- `mineru_request_failed`
- `mineru_invalid_response`
- `mineru_empty_content`
- `mineru_cli_failed`

## GitHub Boundary

GitHub URLs never escalate into crawling or repo ingestion in v1. They always route through the `github_placeholder` path.
