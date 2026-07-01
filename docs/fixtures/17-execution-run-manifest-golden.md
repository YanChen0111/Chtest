# Execution Run Manifest Golden Fixture

This fixture proves Slice 29 execution run manifest inputs without changing
TestRun or runner behavior.

## Scenario

1. A passed TestRun already exists with command, working directory, runner mode,
   run workspace, repository policy, network policy, parsed result, and local
   Artifact metadata.
2. Runtime manifest and stdout artifacts are persisted as local Artifact rows.
3. Dependency and environment snapshot ids are intentionally missing.
4. `GET /api/test-runs/{id}` returns the existing data needed for manifest
   display.
5. Local artifact access opens the runtime manifest by Artifact id.

## Expected Evidence

- TestRun read data keeps command, working directory, runner mode, run
  workspace, repository-readonly policy, network policy, parsed result, and
  artifact metadata available.
- Runtime artifact ids can point to persisted local Artifact rows.
- Missing dependency and environment snapshot ids remain visible as unavailable
  evidence for the frontend manifest.
- Persisted local Artifact ids remain openable through
  `GET /api/artifacts/{artifact_id}/download`.
- Manifest display inputs create no Report, FailureAnalysis,
  QualityGateDecision, AutomationRepairTask, new TestRun, artifact mutation,
  remote provider behavior, RAG runtime, or MCP runtime.

## Non-Goals

- No runner execution change, command assembly change, allowlist change,
  TestRun state-machine change, report generation, failure analysis, quality
  gate computation, repair workflow, artifact upload/mutation/delete, remote
  provider integration, PR comment, deploy/release control, RBAC, tenants,
  permissions, RAG runtime, MCP runtime, or marketplace behavior.
