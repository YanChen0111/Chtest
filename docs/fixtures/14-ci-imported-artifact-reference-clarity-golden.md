# CI Imported Artifact Reference Clarity Golden Fixture

This fixture proves Slice 26 imported artifact reference clarity without remote
provider behavior.

## Scenario

1. A `CICDRun` is imported from static CI metadata.
2. `ci_run_metadata.json` stores an external artifact reference as inert
   metadata.
3. The external reference includes name, kind, external URL, sha256, size, and
   `inert_reference=true`.
4. The owning metadata records `remote_fetch_performed=false`.

## Expected Evidence

- The external artifact reference is display-only metadata.
- Local artifact access rejects the external reference with
  `ARTIFACT_NOT_LOCAL`.
- The local `ci_run_metadata.json` Artifact remains readable as local evidence.
- No TestRun, Report, FailureAnalysis, QualityGateDecision, UnitTestPatch, or
  AutomationDraft is created by imported reference metadata.

## Non-Goals

- No remote fetch, proxy, artifact download, provider authentication, OAuth,
  credential storage, webhook, rerun, PR comment, commit status, deploy,
  release, artifact mutation, upload, delete, RBAC, tenants, permissions, RAG
  runtime, or MCP runtime behavior.
