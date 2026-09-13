# Contract semantics

These schemas and examples are starting contracts, not an implementation or evidence of a completed run. Examples use synthetic IDs and a nonexistent base commit. The included stub exists only to check the sample blob/manifest hashes.

Validate JSON Schema Draft 2020-12, date-time formats, application-level relationships and permissions. `additionalProperties: false` rejects unsolicited command/authorization fields in recovery output. Schema validation alone is not security validation.

## Snapshot digest

`source.snapshotSha256` is SHA-256 over the canonical JSON encoding of `manifest` only, not the full checkpoint (which would create a circular dependency).

Dovet canonical-json/v1: object keys sorted lexicographically by Unicode code point; ASCII-escaped JSON strings; no insignificant whitespace; UTF-8 bytes; no floating-point or non-finite numbers in digest inputs. Arrays retain their order. Manifest files must first be sorted by their validated relative path and duplicate paths rejected. Path validation must not silently normalize two different OS paths to one file. Content hashes are over original bytes, not decoded text.

Use this exact test vector across Python/TypeScript. Policy/action digest inputs follow the same serialization rules and an explicit field whitelist. Never hash a mutable JSON document and assume the caller cannot change its fields afterward.

## Required semantic validators

Reject path traversal, symlink escape, duplicate or platform-colliding paths, mismatched byte sizes, unexpected file modes, missing blob bytes, inconsistent task/policy lineage and evidence IDs not present in the incident. Validate that `passed` criteria reference a verified result for the same snapshot. `writerStopped: true` is transported evidence, not a substitute for current process reconciliation.

Before a proposal executes, recompute hashes from authoritative records, recheck provider authorization/budget and consume any required approval atomically. A model's precondition list cannot remove a coordinator requirement. Reject unknown source versions rather than silently interpreting them as the current schema.

Payload sizes, output truncation and maximum recursion require runtime limits in addition to JSON Schema. The generic event envelope does not authorize arbitrary payload fields to reach a model or public UI; sanitize and validate each event type in implementation.
