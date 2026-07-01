# Golden Path: Local Review History

## Purpose

This fixture verifies Slice 21 local review attribution history. Chtest remains
a single-user local workbench, but successful review-gated evidence actions must
leave append-only local ReviewHistory records that explain who reviewed, what
changed, when it happened, and which evidence artifacts supported the decision.

## Input Flow

- Create a local `CICDRun` from a static diff.
- Generate a `UnitTestPatch` that only changes `tests/test_coupon.py`.
- Approve the `UnitTestPatch` with a local reviewer comment.
- Record new-test and regression evidence.
- Compute a `QualityGateDecision`.

## Expected ReviewHistory

`UnitTestPatch` approval history:

```json
{
  "entity_type": "UnitTestPatch",
  "action": "approve",
  "from_status": "scope_validated",
  "to_status": "approved",
  "reviewer": "Default User",
  "comment": "Golden review approves test-only patch",
  "related_entity_type": "CICDRun",
  "evidence_artifact_ids": []
}
```

`QualityGateDecision` compute history:

```json
{
  "entity_type": "QualityGateDecision",
  "action": "compute_quality_gate",
  "from_status": "pending",
  "to_status": "passed",
  "reviewer": "Default User",
  "related_entity_type": "CICDRun",
  "evidence_artifact_ids": ["regression_plan", "test evidence"]
}
```

## Non-goal Guardrails

- No login/session redesign, roles, permissions, tenants, or enterprise audit.
- No assignment workflow, notifications, team inbox, or comment threads.
- No generic public `POST /api/review-history`.
- No remote CI provider dependency, webhook, PR comment, deploy, or release
  control.
- No RAG runtime, MCP runtime, marketplace, or cloud sync.
