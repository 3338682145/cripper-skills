# Examples

## Blog or Docs Page -> Native -> AUTO_PASS

1. classify URL as `blog_article` or `docs_page`
2. run `native`
3. normalize to `source-packet`
4. verifier returns `AUTO_PASS`
5. route to raw

## Weak Web Page -> Firecrawl -> REVIEW_REQUIRED

1. classify URL as `unknown`
2. native extraction is too short and noisy with reason codes like `native_too_short` or `native_noise_ratio_high`
3. escalate to `Firecrawl` and record `firecrawl_fallback_used`
4. verifier returns `REVIEW_REQUIRED`
5. route to review

## JS-Heavy Page -> Firecrawl Failure -> REVIEW_REQUIRED

1. classify URL as `docs_page` or `unknown`
2. native extraction trips `native_js_heavy_page`
3. Firecrawl is attempted but returns `firecrawl_missing_api_key` or another explicit fallback failure code
4. write a review packet instead of silently passing
5. route to review

## PDF -> MinerU

1. classify URL as `pdf_url`
2. record `pdf_direct_to_mineru`
3. run `MinerU`
4. store `raw_pdf`, `extracted_json`, and markdown `source_snapshot` refs
5. verifier returns `AUTO_PASS` or `REVIEW_REQUIRED`

## Firecrawl PDF Failure -> MinerU

1. previous extraction reports a PDF-specific weakness such as `firecrawl_pdf_multi_column`
2. escalate the packet to `MinerU`
3. preserve `raw_pdf` and `extracted_json` inside the archive
4. verifier returns `AUTO_PASS` or `REVIEW_REQUIRED`

## GitHub Placeholder -> UNSUPPORTED

1. classify URL as `github_repo`
2. bypass native, Firecrawl, and MinerU content extraction entirely
3. normalize a placeholder packet with `backend_used: github_placeholder`
4. add reason codes such as `github_placeholder` and `github_v1_deferred`
5. verifier returns `UNSUPPORTED`
6. route to review

Example placeholder fields:

```yaml
backend_used: github_placeholder
verdict: UNSUPPORTED
reason_codes:
  - github_placeholder
  - github_v1_deferred
```
