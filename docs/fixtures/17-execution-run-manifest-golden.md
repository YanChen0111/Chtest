# Execution Run Manifest Golden Fixture

This fixture proves Slice 29 execution run manifest inputs without changing
runner behavior or artifact storage.

## Scenario

1. A local pytest `TestRun` records the executed command, working directory,
   runner mode, run workspace, repository-readonly policy, network policy, and
   parsed result.
2. The run owns persisted local Artifact rows for `runtime_manifest`,
   `dependency_snapshot`, `stdout`, and `parsed_output`.
3. The run records an `environment_snapshot_artifact_id` that has no matching
   persisted local Artifact row.
4. The run also records a runtime artifact id that is not returned as a
   persisted local Artifact row.
5. The execution page can derive a read-only run manifest from the TestRun read
   model and Artifact metadata.

## Expected Evidence

- `GET /api/test-runs/{test_run_id}` returns command, working directory,
  `runner_mode`, `run_workspace`, `repository_readonly`, `network_enabled`,
  `parsed_result`, `runtime_artifact_ids`, snapshot ids, and Artifact metadata.
- Persisted local Artifact ids are openable through
  `GET /api/artifacts/{artifact_id}/download`.
- Runtime or snapshot ids without a matching persisted local Artifact row remain
  visible as unavailable evidence and are not given local open links.
- Missing snapshot ids remain visible as missing evidence.
- Output artifact availability is derived from existing Artifact rows such as
  `stdout`, `stderr`, `parsed_output`, `junit`, and `coverage`.

## Non-Goals

- No runner execution change, command assembly change, ToolDefinition change,
  allowlist expansion, report generation, FailureAnalysis,
  QualityGateDecision, AutomationRepairTask, AutomationDraft, new TestRun
  creation, artifact mutation, external provider fetch, remote CI provider
  behavior, RBAC, tenants, permissions, RAG runtime, or MCP runtime.
