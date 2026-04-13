# Schema Migration Notes

Whenever a file in `contracts/schemas/` changes its `schema_version` or meaningfully changes required fields, add a migration note in this directory before merging.

Suggested filename: `YYYY-MM-DD-<contract>-vX-to-vY.md`

Include:

- what changed
- why it changed
- which fields need backfill or rename handling
- how validation behavior changes

Milestone 1A starts all contracts at `1.0.0`, so no migration note is needed yet.
