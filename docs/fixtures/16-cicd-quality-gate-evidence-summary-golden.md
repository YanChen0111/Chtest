# CI/CD Quality Gate Evidence Summary Golden Fixture

This fixture proves Slice 28 quality gate evidence summary inputs without
changing CI/CD quality gate behavior.

## Scenario

1. A local diff creates a CI/CD run.
2. A reviewed UnitTestPatch is approved and applied.
3. New-test and regression TestRuns are created and marked succeeded.
4. QualityGateDecision is computed without generating a CI/CD quality report.
5. A second CI/CD run computes QualityGateDecision with missing required
   evidence.

## Expected Evidence

- Complete evidence produces a `passed` QualityGateDecision.
- `status_detail` preserves UnitTestPatch/PatchScopeGate, new-test, regression,
  and failure-analysis-not-available summary inputs.
- `blocking_reasons` remains visible and empty for the passed path.
- `evidence_artifact_ids` contains only the persisted UnitTestPatch Artifact id.
- Missing UnitTestPatch, new-test, and regression evidence produces
  `needs_review`, not `passed`.
- Missing evidence keeps explicit blocking reasons and unavailable status detail.
- Computing QualityGateDecision exposes summary inputs while creating no Report,
  FailureAnalysis, AutomationDraft, remote provider side effects, new Artifact,
  or mutation to existing Artifact rows.

## Non-Goals

- No quality gate scoring change, report generation, failure analysis,
  TestRunner execution change, remote CI provider integration, PR comment,
  commit status, deployment, release control, artifact upload/mutation/delete,
  cloud storage, RBAC, tenants, permissions, RAG runtime, or MCP runtime.
