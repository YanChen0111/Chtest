# Local Artifact Access Golden Fixture

This fixture proves Slice 24 local artifact access without changing runner
behavior.

## Scenario

1. A local pytest `TestRun` has already completed with `status=passed`.
2. The run owns a persisted `stdout` Artifact row whose file lives under the
   configured local artifact root.
3. The Artifact row stores `size_bytes`, `sha256`, MIME type, and safe metadata.
4. A separate imported CI artifact reference stores an external URL as an inert
   label.

## Expected Evidence

- `GET /api/artifacts/{stdout_artifact_id}/download` returns the exact persisted
  stdout bytes.
- The downloaded content hashes to the Artifact row `sha256` and has the same
  byte length as `size_bytes`.
- The response uses the Artifact MIME type and exposes only a safe basename in
  `Content-Disposition`.
- Reading the artifact does not mutate the Artifact row metadata or TestRun
  runtime artifact reference.
- `GET /api/artifacts/{external_reference_id}/download` fails with
  `ARTIFACT_NOT_LOCAL`.

## Non-Goals

- No artifact upload, mutation, deletion, sharing, signed URL, cloud storage, or
  external provider fetch.
- No runner behavior, report generation, failure analysis, QualityGateDecision,
  RAG runtime, MCP runtime, RBAC, tenants, or permissions behavior.
