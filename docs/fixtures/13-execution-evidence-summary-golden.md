# Execution Evidence Summary Golden Fixture

This fixture proves Slice 25 execution evidence summary without changing report
generation or runner behavior.

## Scenario

1. A local `TestRun` owns a persisted stdout Artifact.
2. A summary row cites that Artifact as required evidence for a report claim.
3. A structured metric row cites parsed execution evidence without an Artifact
   file.
4. `environment_snapshot` is missing and remains explicit.
5. An imported external artifact reference remains inert.

## Expected Evidence

- The local Artifact summary row can be opened through
  `GET /api/artifacts/{artifact_id}/download`.
- Downloaded bytes match the Artifact row `sha256` and `size_bytes` metadata.
- Structured metric evidence is not downloadable.
- Missing evidence stays visible and is not treated as passing evidence.
- External imported artifact references fail with `ARTIFACT_NOT_LOCAL`.

## Non-Goals

- No report generation, FailureAnalysis, QualityGateDecision, runner,
  artifact mutation, upload, delete, cloud storage, external fetch, RBAC,
  tenants, permissions, RAG runtime, or MCP runtime behavior.
