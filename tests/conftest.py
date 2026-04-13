from __future__ import annotations

import sys
import shutil
import uuid
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.fixture
def tmp_path() -> Path:
    base = ROOT / ".tmp-tests"
    base.mkdir(parents=True, exist_ok=True)
    path = base / f"case-{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=True)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


@pytest.fixture
def workspace_factory(tmp_path: Path):
    def factory(*, source_url: str = "https://example.com/article") -> Path:
        for rel in [
            "content/registry/sources",
            "content/registry/jobs",
            "content/raw",
            "state/runs",
            "state/indexes",
        ]:
            (tmp_path / rel).mkdir(parents=True, exist_ok=True)

        _write(
            tmp_path / "content/registry/sources/example-web-source.md",
            f"""---
schema: ingestion-source
schema_version: 1.0.0
source_id: example-web-source
display_name: Example Web Source
status: active
source_kind: web_url
adapter: web_url
seed_urls:
  - {source_url}
allowed_domains:
  - example.com
discovery_mode: seed_urls
default_topics:
  - sample-topic
schedule:
  cadence: manual
owner: tests
validation_profile: strict
---

Example source.
""",
        )
        _write(
            tmp_path / "content/registry/jobs/example-web-job.md",
            """---
schema: ingestion-job
schema_version: 1.0.0
job_id: example-web-job
source_id: example-web-source
trigger: manual
cadence: on-demand
max_items: 1
fetch_budget: 1
retry_policy:
  max_attempts: 2
write_targets:
  - raw-assets
  - run-manifest
dossier_policy: contract-only
---

Example job.
""",
        )
        return tmp_path

    return factory
