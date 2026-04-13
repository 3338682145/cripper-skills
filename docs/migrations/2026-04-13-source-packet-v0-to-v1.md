# Source Packet Contract Introduction

## What changed

Added a new additive `source-packet` contract for the optional `source-intake` skill.

## Why it changed

The existing `raw-asset` contract is tied to the current Cliper-native workflow. The `source-intake` skill needs richer routing and archive metadata without breaking the current raw asset semantics.

## Backfill or rename handling

- No existing `raw-asset` file must be renamed.
- No current registry, run-manifest, or raw-asset field is removed.
- New packet writers can coexist with the current raw-asset workflow.

## Validation impact

- `raw-asset` validation rules remain unchanged.
- Future packet validation should enforce `schema: source-packet`, `backend_used`, `verdict`, provenance metadata, routing metadata, and archive refs.
