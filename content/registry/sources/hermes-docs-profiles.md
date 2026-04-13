---
schema: ingestion-source
schema_version: 1.0.0
source_id: hermes-docs-profiles
display_name: Hermes Docs Profiles Page
status: active
source_kind: web_url
adapter: web_url
seed_urls:
  - https://hermes-agent.nousresearch.com/docs/user-guide/profiles
allowed_domains:
  - hermes-agent.nousresearch.com
discovery_mode: seed_urls
default_topics:
  - hermes
  - user-guide
schedule:
  cadence: manual
  timezone: UTC
owner: hermes-core
validation_profile: strict
---

Manual test source for the Hermes profiles documentation page.
