---
schema: ingestion-source
schema_version: 1.0.0
source_id: example-web-source
display_name: Example Web Source
status: active
source_kind: web_url
adapter: web_url
seed_urls:
  - https://example.com/
allowed_domains:
  - example.com
discovery_mode: seed_urls
default_topics:
  - sample-topic
schedule:
  cadence: manual
  timezone: UTC
owner: hermes-core
validation_profile: strict
---

Example source used to demonstrate the Milestone 1A ingest path.

