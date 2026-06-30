# Chtest API Contract

## 1. Purpose

This document defines the Chtest V1 API contract. FastAPI routers, Pydantic schemas, frontend API clients, fixtures, and acceptance tests must follow this contract.

Common rules:

- Base path: `/api`.
- Content-Type: `application/json`.
- Time format: ISO 8601.
- id format: UUID string.
- Error response: `{"error_code": "string", "message": "string", "details": {}}`.
- V1 is single-user; API uses default user/workspace internally.

Context rules:

- V1 ContextArtifact is an API concept backed by the Artifact table, not a separate data table.
- `use_knowledge=false` only means external RAG/KnowledgeAdapter is not used.
- `context_artifact_ids` are still injected into prompts when provided, even when `use_knowledge=false`.
- AI responses that used local context must return `used_context_artifact_ids`.
- AI responses that used external RAG/KnowledgeAdapter must return `used_knowledge=true`; otherwise return `used_knowledge=false`.

## 2. Project Settings APIs

### 2.1 Create Project

`POST /api/projects`

Request:

```json
{
  "name": "Checkout System",
  "description": "personal testing project",
  "default_language": "python",
  "default_test_type": "functional"
}
```

Response 201:

```json
{
  "id": "00000000-0000-0000-0000-000000000101",
  "name": "Checkout System",
  "default_language": "python",
  "default_test_type": "functional",
  "status": "active",
  "created_at": "2026-06-18T10:00:00Z"
}
```

### 2.2 Create Module

`POST /api/projects/{project_id}/modules`

Request:

```json
{
  "parent_id": null,
  "name": "Checkout",
  "sort_order": 10
}
```

Response 201 returns Module read model.

### 2.3 Create Repository

`POST /api/repositories`

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "name": "sample-app",
  "local_path": "/Users/yanchen/VscodeProject/sample-app",
  "default_base_branch": "main",
  "language_hint": "python"
}
```

Response 201:

```json
{
  "id": "00000000-0000-0000-0000-000000000301",
  "project_id": "00000000-0000-0000-0000-000000000101",
  "name": "sample-app",
  "local_path": "/Users/yanchen/VscodeProject/sample-app",
  "default_base_branch": "main",
  "language_hint": "python",
  "status": "active"
}
```

Validation rules:

- `local_path` must exist.
- `local_path` must be under configured allowlisted roots.
- `local_path` must contain `.git` when Git workflows are enabled.

### 2.4 Update Repository

`PATCH /api/repositories/{id}`

Request:

```json
{
  "name": "sample-app",
  "default_base_branch": "main",
  "language_hint": "python",
  "status": "active"
}
```

Response 200 returns Repository read model.

### 2.5 Create Environment

`POST /api/environments`

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "name": "local",
  "variables_json": {
    "APP_ENV": "test",
    "BASE_URL": "http://127.0.0.1:8000"
  }
}
```

Response 201 returns Environment read model.

### 2.6 Update Environment

`PATCH /api/environments/{id}`

Request:

```json
{
  "name": "local",
  "variables_json": {
    "APP_ENV": "test",
    "BASE_URL": "http://127.0.0.1:8000"
  },
  "status": "active"
}
```

Response 200 returns Environment read model.

### 2.7 Create Test Command

`POST /api/test-commands`

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "repository_id": "00000000-0000-0000-0000-000000000301",
  "environment_id": "00000000-0000-0000-0000-000000000351",
  "name": "pytest unit",
  "command": "pytest tests/unit -q --junitxml=artifacts/junit.xml",
  "working_directory": "/Users/yanchen/VscodeProject/sample-app",
  "command_type": "pytest",
  "timeout_seconds": 600,
  "parse_junit": true,
  "parse_coverage": false
}
```

Response 201 returns TestCommand read model.

### 2.8 Validate Test Command

`POST /api/test-commands/{id}/validate`

Request:

```json
{
  "dry_run": true
}
```

Response 200:

```json
{
  "test_command_id": "00000000-0000-0000-0000-000000000302",
  "valid": true,
  "allowlist_passed": true,
  "working_directory_passed": true,
  "messages": []
}
```

### 2.9 Get Project Settings

`GET /api/projects/{id}/settings`

Response 200:

```json
{
  "project": {
    "id": "00000000-0000-0000-0000-000000000101",
    "name": "Checkout System",
    "default_language": "python",
    "default_test_type": "functional"
  },
  "modules": [],
  "repositories": [],
  "environments": [],
  "test_commands": [],
  "tool_definitions": []
}
```

This endpoint powers the Project Settings page and gives the frontend one stable bootstrap contract.

### 2.10 Create Context Artifact

`POST /api/context-artifacts`

ContextArtifact is the V1 lightweight context mechanism before external RAG exists. It stores small requirement notes, API notes, OpenAPI snippets, logs, fixtures, or Markdown references that can be injected into AI prompts.

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "title": "coupon-api-notes.md",
  "artifact_type": "context_markdown",
  "mime_type": "text/markdown",
  "content": "# Coupon API Notes\nPOST /api/coupons/validate validates coupon availability.",
  "source_ref": "manual:coupon-api-notes.md"
}
```

Response 201:

```json
{
  "id": "00000000-0000-0000-0000-000000000371",
  "project_id": "00000000-0000-0000-0000-000000000101",
  "owner_entity_type": "Project",
  "owner_entity_id": "00000000-0000-0000-0000-000000000101",
  "artifact_type": "context_markdown",
  "mime_type": "text/markdown",
  "file_path": "projects/00000000-0000-0000-0000-000000000101/context-artifacts/00000000-0000-0000-0000-000000000371/content.md",
  "sha256": "sha256:example",
  "metadata": {
    "title": "coupon-api-notes.md",
    "source_ref": "manual:coupon-api-notes.md",
    "safe_to_show": true,
    "redaction_applied": false
  }
}
```

Hard rules:

- The server must set `owner_entity_type=Project` and `owner_entity_id=project_id`.
- The client must not send or override owner fields.
- The server must run secret scan and redaction before saving and before display.
- `safe_to_show` is server-computed; a client-provided value is ignored.
- Allowed MIME types and size limits follow `docs/contracts/04-artifact-contract.md`.
- Unsafe MIME returns `CONTEXT_ARTIFACT_NOT_ALLOWED`.
- Size limit violations return `CONTEXT_ARTIFACT_TOO_LARGE`.
- High-risk secret detection returns `CONTEXT_ARTIFACT_SECRET_DETECTED`.

### 2.11 List Context Artifacts

`GET /api/projects/{project_id}/context-artifacts`

Response 200:

```json
{
  "items": [
    {
      "id": "00000000-0000-0000-0000-000000000371",
      "title": "coupon-api-notes.md",
      "artifact_type": "context_markdown",
      "mime_type": "text/markdown",
      "safe_to_show": true,
      "redaction_applied": false
    }
  ],
  "total": 1
}
```

## 3. Requirement To Case APIs

### 3.1 Create Requirement

`POST /api/requirements`

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "module_id": "00000000-0000-0000-0000-000000000201",
  "title": "Coupon checkout rules",
  "content": "User can select one available coupon during checkout. Coupon cannot be used with points. Expired coupons cannot be used.",
  "source_type": "manual",
  "source_ref": "REQ-COUPON-001"
}
```

Response 201 returns Requirement read model.

### 3.2 Start Requirement Review

`POST /api/requirements/{id}/review`

Request:

```json
{
  "prompt_version": "requirement_review:v1",
  "skill_version": "requirement-review-skill:v1",
  "model_provider": "mock",
  "model_name": "mock-requirement-review",
  "use_knowledge": false,
  "context_artifact_ids": ["00000000-0000-0000-0000-000000000371"]
}
```

Response 202:

```json
{
  "ai_task_id": "00000000-0000-0000-0000-000000000501",
  "requirement_id": "00000000-0000-0000-0000-000000000401",
  "status": "pending",
  "next_poll_url": "/api/ai-tasks/00000000-0000-0000-0000-000000000501",
  "used_knowledge": false,
  "used_context_artifact_ids": ["00000000-0000-0000-0000-000000000371"]
}
```

`use_knowledge=false` disables only external RAG/KnowledgeAdapter. The listed `context_artifact_ids` are still included in the prompt input and recorded on AITask.

### 3.3 Get Requirement Review

`GET /api/requirements/{id}/review`

Response 200:

```json
{
  "id": "00000000-0000-0000-0000-000000000601",
  "requirement_id": "00000000-0000-0000-0000-000000000401",
  "overall_score": 82,
  "scores": {
    "completeness": 78,
    "clarity": 85,
    "consistency": 88,
    "testability": 80,
    "feasibility": 84,
    "logic": 77
  },
  "issues": [
    {"type": "missing_boundary", "text": "Coupon minimum amount is not specified", "severity": "medium"}
  ],
  "clarification_questions": ["Can coupons be combined with campaign discounts?"],
  "risk_items": [
    {"title": "Coupon and points conflict", "risk_level": "high", "suggestion": "Cover the conflict path"}
  ],
  "used_knowledge": false,
  "used_context_artifact_ids": ["00000000-0000-0000-0000-000000000371"],
  "context_manifest_artifact_id": "00000000-0000-0000-0000-000000000372",
  "status": "reviewed"
}
```

### 3.4 Create Case Generation Task

`POST /api/case-generation/tasks`

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "requirement_id": "00000000-0000-0000-0000-000000000401",
  "requirement_review_id": "00000000-0000-0000-0000-000000000601",
  "target_test_types": ["functional", "ui"],
  "prompt_version": "case_generation:v1",
  "skill_version": "test-case-generation-skill:v1",
  "model_provider": "mock",
  "model_name": "mock-case-generator",
  "use_knowledge": false,
  "context_artifact_ids": ["00000000-0000-0000-0000-000000000371"]
}
```

Response 202:

```json
{
  "case_generation_task_id": "00000000-0000-0000-0000-000000000701",
  "ai_task_id": "00000000-0000-0000-0000-000000000702",
  "status": "pending",
  "used_knowledge": false,
  "used_context_artifact_ids": ["00000000-0000-0000-0000-000000000371"]
}
```

### 3.5 List Candidate Cases

`GET /api/case-generation/tasks/{id}/candidates`

Response 200:

```json
{
  "items": [
    {
      "id": "00000000-0000-0000-0000-000000000801",
      "title": "Expired coupon cannot be used during checkout",
      "priority": "P0",
      "test_type": "functional",
      "steps": ["Login", "Open checkout", "Select expired coupon", "Submit order"],
      "expected_results": ["Submission is blocked", "Expired coupon message is shown"],
      "requirement_refs": ["Expired coupons cannot be used"],
      "ai_reason": "Covers coupon expiration boundary",
      "status": "generated"
    }
  ],
  "total": 1
}
```

### 3.6 Review Candidate Case

`POST /api/case-review/items/{id}/approve`

Request:

```json
{
  "action": "approve_after_edit",
  "edited_case": {
    "title": "Expired coupon cannot submit order",
    "priority": "P0",
    "steps": ["Prepare expired coupon", "Login", "Open checkout", "Select expired coupon", "Submit order"],
    "expected_results": ["Coupon is unavailable or submit fails", "Clear error message is shown"]
  },
  "review_comment": "Added test data preparation step"
}
```

Response 200:

```json
{
  "candidate_id": "00000000-0000-0000-0000-000000000801",
  "status": "approved_after_edit",
  "test_case_id": "00000000-0000-0000-0000-000000000901"
}
```

### 3.7 Test Case Library

`GET /api/test-cases`

Query filters:

| Name | Required | Notes |
|---|---:|---|
| project_id | yes | Limit library results to one project |
| module_id | no | Limit results to one module |
| status | no | TestCase entity status, default includes active records |
| test_type | no | Filter by functional, ui, api, etc. |
| priority | no | Filter by P0/P1/P2/P3 |
| keyword | no | Case-insensitive match against title, steps, expected results, tags, or requirement refs where available |

Response model: `TestCaseListRead`.

Response 200:

```json
{
  "items": [
    {
      "id": "00000000-0000-0000-0000-000000000901",
      "project_id": "00000000-0000-0000-0000-000000000101",
      "module_id": "00000000-0000-0000-0000-000000000201",
      "source_candidate_id": "00000000-0000-0000-0000-000000000801",
      "title": "Expired coupon cannot submit order",
      "priority": "P0",
      "test_type": "functional",
      "precondition": "User has an expired coupon",
      "steps": ["Prepare expired coupon", "Login", "Open checkout", "Select expired coupon", "Submit order"],
      "expected_results": ["Coupon is unavailable or submit fails", "Clear error message is shown"],
      "input_data": {"coupon_state": "expired"},
      "tags": ["coupon", "boundary"],
      "source_type": "ai",
      "review_status": "approved_after_edit",
      "status": "active"
    }
  ],
  "total": 1
}
```

Contract boundary:

- The library lists reviewed TestCase records only. It does not list generated
  candidates that have not been approved.
- V1 does not create or mutate TestCase records through this endpoint.
- AutomationDraft creation, execution, reports, CI/CD quality, RAG runtime, MCP
  runtime, RBAC, tenants, and permissions are outside this API.

## 4. Automation Draft APIs

### 4.1 Create Automation Draft

`POST /api/automation/drafts`

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "test_case_id": "00000000-0000-0000-0000-000000000901",
  "requirement_id": null,
  "target_framework": "pytest",
  "prompt_version": "automation_draft_generation:v1",
  "skill_version": "automation-draft-skill:v1",
  "model_provider": "mock",
  "model_name": "mock-automation-draft"
}
```

Response 202:

```json
{
  "automation_draft_id": "00000000-0000-0000-0000-000000001001",
  "ai_task_id": "00000000-0000-0000-0000-000000001002",
  "status": "pending"
}
```

### 4.2 Get Automation Draft

`GET /api/automation/drafts/{id}`

Response 200 returns AutomationDraft read model with `draft_code`, `target_framework`, `suggested_file_path`, `execution_notes`, `risk_notes`, and artifacts.

### 4.3 Edit Automation Draft

`PATCH /api/automation/drafts/{id}`

Request:

```json
{
  "draft_code": "def test_coupon_rule():
    assert True
",
  "suggested_file_path": "tests/test_coupon_rule.py",
  "review_comment": "Adjusted fixture name"
}
```

Response 200:

```json
{
  "automation_draft_id": "00000000-0000-0000-0000-000000001001",
  "status": "edited"
}
```

### 4.4 Approve Automation Draft

`POST /api/automation/drafts/{id}/approve`

Request:

```json
{
  "action": "approve",
  "review_comment": "Draft is safe to execute"
}
```

Response 200:

```json
{
  "automation_draft_id": "00000000-0000-0000-0000-000000001001",
  "status": "approved"
}
```

AutomationDraft uses `edit -> edited -> approve -> approved`. It does not use `approve_after_edit`.

## 5. CI/CD Quality APIs

CI/CD Quality APIs are the page-level workflow contract for `CI/CD 质量中心`.
They may create or return generic `AITask`, `TestRun`, `FailureAnalysis`, and
`Report` records, but the endpoint names stay under `/api/cicd` so the frontend
can drive the CI/CD quality workflow without guessing cross-module orchestration.

Slice 15 foundation boundary:

- Slice 15 implements only local-first CI/CD evidence setup:
  `POST /api/cicd/runs`, `GET /api/cicd/runs`,
  `GET /api/cicd/runs/{id}`, and `POST /api/cicd/runs/{id}/analyze`.
- Slice 15 supports `source_type=local_diff` and manual local inputs only,
  `trigger_type=manual`, and `provider=local`.
- Slice 15 may create `CICDRun`, `CICDChangedFile`, `AITask`, `Artifact`, and
  risk analysis evidence.
- Slice 15 must not create `UnitTestPatch`, `TestRun`, `QualityGateDecision`,
  `FailureAnalysis`, or `Report` records.
- Endpoints in sections 5.5-5.13 are Slice 16+ unless a later task explicitly
  narrows and activates them.
- V1 does not integrate remote CI providers, webhooks, PR comments, merge,
  push, release, deployment, RAG runtime, MCP runtime, RBAC, tenants, or
  permissions in Slice 15.

### 5.1 Create CI/CD Run

`POST /api/cicd/runs`

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "repository_id": "00000000-0000-0000-0000-000000000301",
  "source_type": "local_diff",
  "diff_text": "diff --git a/app/coupon.py b/app/coupon.py\n...",
  "base_ref": "main",
  "head_ref": "HEAD"
}
```

Rules:

- `diff_text` is optional but recommended in Slice 15. When supplied, the API
  persists CICDChangedFile rows and a `changed_files.json` artifact.
- If `diff_text` is omitted, the run remains `created` with no changed files
  until manual changed-file evidence is supplied by a later task.
- `source_type` must be `local_diff` or `manual_check`.
- `trigger_type` is implicitly `manual`; `provider` is implicitly `local`.
- Requests for `github_actions`, `gitlab_ci`, `jenkins`, webhook, PR, scheduled,
  merge, release, or deployment behavior must be rejected or ignored as
  out-of-scope for Slice 15.

Response 202:

```json
{
  "cicd_run_id": "00000000-0000-0000-0000-000000001101",
  "status": "created"
}
```

### 5.2 List CI/CD Runs

`GET /api/cicd/runs`

Query parameters:

```text
project_id optional uuid
repository_id optional uuid
status optional string
quality_gate_status optional pending|passed|failed|needs_review
```

Response 200:

```json
{
  "items": [
    {
      "id": "00000000-0000-0000-0000-000000001101",
      "project_id": "00000000-0000-0000-0000-000000000101",
      "repository_id": "00000000-0000-0000-0000-000000000301",
      "source_type": "local_diff",
      "trigger_type": "manual",
      "provider": "local",
      "base_ref": "main",
      "head_ref": "HEAD",
      "overall_risk": "medium",
      "quality_gate_status": "pending",
      "status": "created"
    }
  ],
  "total": 1
}
```

### 5.3 Get CI/CD Run

`GET /api/cicd/runs/{id}`

Response 200:

```json
{
  "id": "00000000-0000-0000-0000-000000001101",
  "project_id": "00000000-0000-0000-0000-000000000101",
  "repository_id": "00000000-0000-0000-0000-000000000301",
  "summary": "Coupon amount boundary change",
  "overall_risk": "medium",
  "quality_gate_status": "pending",
  "status": "analyzed",
  "changed_files": [
    {
      "path": "app/coupon.py",
      "old_path": null,
      "change_type": "modified",
      "language": "python",
      "file_role": "source",
      "risk_level": "medium",
      "risk_reasons": ["source file changed"],
      "lines_added": 12,
      "lines_deleted": 4
    }
  ],
  "analysis_artifacts": [
    {
      "artifact_type": "risk_analysis",
      "file_path": "artifacts/projects/00000000-0000-0000-0000-000000000101/cicd-quality/00000000-0000-0000-0000-000000001101/risk_analysis.json"
    }
  ],
  "unit_test_patches": [],
  "test_runs": [],
  "quality_gate_decision": null,
  "reports": []
}
```

### 5.4 Analyze CI/CD Run

`POST /api/cicd/runs/{id}/analyze`

Request:

```json
{
  "prompt_version": "cicd_change_analysis:v1",
  "skill_version": "regression-selection-skill:v1",
  "model_provider": "mock",
  "model_name": "mock-cicd-analysis"
}
```

Response 202 returns AITask reference.

Rules:

- Analyze uses deterministic mock output in V1.
- Analyze creates a succeeded AITask and a `risk_analysis.json` artifact owned by
  the CICDRun.
- Analyze updates `CICDRun.status` to `analyzed`.
- Analyze may update `CICDRun.overall_risk` from changed file risks.
- Analyze does not create UnitTestPatch, TestRun, QualityGateDecision,
  FailureAnalysis, or Report records in Slice 15.

### 5.5+ Slice 16 And Later Endpoints

The endpoints below are contract placeholders for Slice 16+ work:

- `POST /api/cicd/runs/{id}/unit-test-patches`
- `POST /api/cicd/unit-test-patches/{id}/approve`
- `POST /api/cicd/unit-test-patches/{id}/reject`
- `POST /api/cicd/unit-test-patches/{id}/apply`
- `POST /api/cicd/runs/{id}/run-new-tests`
- `POST /api/cicd/runs/{id}/select-regression`
- `POST /api/cicd/runs/{id}/run-regression`
- `POST /api/cicd/runs/{id}/quality-gate`
- `POST /api/cicd/runs/{id}/generate-report`

Do not implement these endpoints in Slice 15.

### 5.5 Generate Unit Test Patch

`POST /api/cicd/runs/{id}/unit-test-patches`

Request:

```json
{
  "target_framework": "pytest",
  "prompt_version": "unit_test_generation:v1",
  "skill_version": "unit-test-generation-skill:v1",
  "model_provider": "mock",
  "model_name": "mock-unit-test-generator"
}
```

Response 202:

```json
{
  "unit_test_patch_id": "00000000-0000-0000-0000-000000001201",
  "status": "generated"
}
```

### 5.6 Approve Unit Test Patch

`POST /api/cicd/unit-test-patches/{id}/approve`

Request:

```json
{
  "action": "approve",
  "review_comment": "Only tests/ is modified"
}
```

Response 200:

```json
{
  "unit_test_patch_id": "00000000-0000-0000-0000-000000001201",
  "status": "approved"
}
```

### 5.7 Reject Unit Test Patch

`POST /api/cicd/unit-test-patches/{id}/reject`

Request:

```json
{
  "review_comment": "Patch does not cover the changed branch."
}
```

Response 200:

```json
{
  "unit_test_patch_id": "00000000-0000-0000-0000-000000001201",
  "status": "rejected"
}
```

### 5.8 Apply Unit Test Patch

`POST /api/cicd/unit-test-patches/{id}/apply`

Request:

```json
{
  "confirm_scope_gate_result": true
}
```

Response 200:

```json
{
  "unit_test_patch_id": "00000000-0000-0000-0000-000000001201",
  "status": "applied",
  "applied_artifact_id": "00000000-0000-0000-0000-000000001211"
}
```

Rules:

- Only `approved` UnitTestPatch records can be applied.
- PatchScopeGate must pass before application.
- Application must fail with `PATCH_SCOPE_REJECTED` when the patch modifies paths outside allowed test directories.

### 5.9 Run New Tests

`POST /api/cicd/runs/{id}/run-new-tests`

Request:

```json
{
  "unit_test_patch_id": "00000000-0000-0000-0000-000000001201",
  "test_command_id": "00000000-0000-0000-0000-000000000302"
}
```

Response 202:

```json
{
  "test_run_id": "00000000-0000-0000-0000-000000001301",
  "cicd_run_id": "00000000-0000-0000-0000-000000001101",
  "status": "queued"
}
```

Rules:

- The endpoint creates a generic TestRun with `cicd_run_id` set.
- The endpoint requires an applied UnitTestPatch when `unit_test_patch_id` is provided.

### 5.10 Select Regression

`POST /api/cicd/runs/{id}/select-regression`

Request:

```json
{
  "skill_version": "regression-selection-skill:v1",
  "candidate_test_command_ids": ["00000000-0000-0000-0000-000000000302"]
}
```

Response 200:

```json
{
  "cicd_run_id": "00000000-0000-0000-0000-000000001101",
  "regression_plan_artifact_id": "00000000-0000-0000-0000-000000001221",
  "recommended_test_command_ids": ["00000000-0000-0000-0000-000000000302"],
  "reasons": ["Changed source branch is covered by pytest unit command."]
}
```

RegressionPlan is stored as `regression_plan.json` artifact in V1, not as a separate database table.

### 5.11 Run Regression

`POST /api/cicd/runs/{id}/run-regression`

Request:

```json
{
  "regression_plan_artifact_id": "00000000-0000-0000-0000-000000001221",
  "test_command_ids": ["00000000-0000-0000-0000-000000000302"]
}
```

Response 202:

```json
{
  "cicd_run_id": "00000000-0000-0000-0000-000000001101",
  "test_run_ids": ["00000000-0000-0000-0000-000000001302"],
  "status": "tests_running"
}
```

Rules:

- Each regression command creates a generic TestRun with `cicd_run_id` set.
- V1 regression execution must use allowed TestCommand records.

### 5.12 Compute Quality Gate

`POST /api/cicd/runs/{id}/quality-gate`

Request:

```json
{
  "include_failure_analysis": true
}
```

Response 200:

```json
{
  "quality_gate_decision_id": "00000000-0000-0000-0000-000000001401",
  "cicd_run_id": "00000000-0000-0000-0000-000000001101",
  "status": "passed",
  "summary": "Patch scope, new tests, and regression passed with evidence.",
  "blocking_reasons": []
}
```

Rules:

- A recompute always creates a new QualityGateDecision record and updates `CICDRun.quality_gate_status`.
- Missing required evidence returns `needs_review`, not `passed`.

### 5.13 Generate CI/CD Quality Report

`POST /api/cicd/runs/{id}/generate-report`

Request:

```json
{
  "report_format": ["markdown", "html", "json"]
}
```

Response 202:

```json
{
  "report_id": "00000000-0000-0000-0000-000000001501",
  "cicd_run_id": "00000000-0000-0000-0000-000000001101",
  "status": "generating"
}
```

Rules:

- The endpoint creates a generic Report with `report_type=cicd_quality`.
- The report conclusion must cite QualityGateDecision and evidence artifacts.

## 6. Test Run APIs

Test Run APIs execute V1 approved pytest or minimal Playwright work and return
evidence records. They are local-first and allowlisted: the backend assembles or
validates commands from an approved AutomationDraft or configured TestCommand.
Clients must not submit arbitrary shell strings.

### 6.1 Create Test Run

`POST /api/test-runs`

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "test_command_id": "00000000-0000-0000-0000-000000000302",
  "automation_draft_id": "00000000-0000-0000-0000-000000001001",
  "reason": "run approved automation draft",
  "runner_mode": "local_subprocess"
}
```

Request rules:

- Exactly one execution source is required: approved `automation_draft_id` or
  configured `test_command_id`.
- `automation_draft_id` must reference an AutomationDraft with
  `status=approved` and `target_framework` matching the requested runner:
  `pytest` for `local_subprocess`, `playwright` for `playwright_local`.
- `test_command_id` must reference a configured TestCommand with
  `command_type=pytest` or `command_type=playwright` and passing allowlist
  validation.
- `runner_mode` is optional and defaults to `local_subprocess` for pytest.
  Playwright minimal execution uses `runner_mode=playwright_local`.
- V1 does not expose Docker runner or browser grid selection through this
  endpoint.
- `cicd_run_id` is not accepted by this workbench endpoint. CI/CD
  orchestration stays under `/api/cicd`.

Response 202:

```json
{
  "id": "00000000-0000-0000-0000-000000001301",
  "project_id": "00000000-0000-0000-0000-000000000101",
  "automation_draft_id": "00000000-0000-0000-0000-000000001001",
  "test_command_id": null,
  "tool_invocation_id": "00000000-0000-0000-0000-000000001302",
  "status": "queued",
  "name": "pytest approved draft",
  "command": "python -m pytest tests/test_coupon_rule.py -q --junitxml=artifacts/junit.xml",
  "working_directory": "/Users/yanchen/VscodeProject/sample-app",
  "runner_mode": "local_subprocess",
  "run_workspace": "artifacts/projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001301/workspace",
  "repository_readonly": true,
  "network_enabled": false,
  "runtime_artifact_ids": ["00000000-0000-0000-0000-000000001201"],
  "dependency_snapshot_artifact_id": "00000000-0000-0000-0000-000000001202",
  "environment_snapshot_artifact_id": "00000000-0000-0000-0000-000000001203",
  "exit_code": null,
  "duration_ms": null,
  "parsed_result": {},
  "test_results": [],
  "artifacts": []
}
```

The created TestRun must record runner sandbox metadata: `runner_mode`,
`run_workspace`, `repository_readonly`, `network_enabled`,
`runtime_artifact_ids`, `dependency_snapshot_artifact_id`, and
`environment_snapshot_artifact_id`.

### 6.2 Get Test Run

`GET /api/test-runs/{id}`

Response 200:

```json
{
  "id": "00000000-0000-0000-0000-000000001301",
  "project_id": "00000000-0000-0000-0000-000000000101",
  "automation_draft_id": "00000000-0000-0000-0000-000000001001",
  "test_command_id": null,
  "tool_invocation_id": "00000000-0000-0000-0000-000000001302",
  "status": "passed",
  "name": "pytest approved draft",
  "command": "python -m pytest tests/test_coupon_rule.py -q --junitxml=artifacts/junit.xml",
  "working_directory": "/Users/yanchen/VscodeProject/sample-app",
  "runner_mode": "local_subprocess",
  "run_workspace": "artifacts/projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001301/workspace",
  "repository_readonly": true,
  "network_enabled": false,
  "runtime_artifact_ids": ["00000000-0000-0000-0000-000000001201"],
  "dependency_snapshot_artifact_id": "00000000-0000-0000-0000-000000001202",
  "environment_snapshot_artifact_id": "00000000-0000-0000-0000-000000001203",
  "exit_code": 0,
  "duration_ms": 3560,
  "parsed_result": {
    "total": 3,
    "passed": 3,
    "failed": 0,
    "skipped": 0,
    "error": 0
  },
  "test_results": [
    {
      "id": "00000000-0000-0000-0000-000000001331",
      "project_id": "00000000-0000-0000-0000-000000000101",
      "test_run_id": "00000000-0000-0000-0000-000000001301",
      "test_name": "tests/test_coupon.py::test_expired_coupon",
      "test_file": "tests/test_coupon.py",
      "status": "passed",
      "duration_ms": 123,
      "failure_message": null,
      "failure_artifact_ids": [],
      "metadata": {"classname": "tests.test_coupon"}
    }
  ],
  "artifacts": [
    {"artifact_type": "runtime_manifest", "file_path": "projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001301/runtime_manifest.json"},
    {"artifact_type": "dependency_snapshot", "file_path": "projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001301/dependency_snapshot.json"},
    {"artifact_type": "environment_snapshot", "file_path": "projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001301/environment_snapshot.json"},
    {"artifact_type": "stdout", "file_path": "projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001301/stdout.log"}
  ]
}
```

Response model: `TestRunRead` with embedded `TestResultRead` items.

### 6.3 List Test Results

`GET /api/test-runs/{id}/results`

Response 200:

```json
{
  "items": [
    {
      "id": "00000000-0000-0000-0000-000000001331",
      "test_name": "tests/test_coupon.py::test_expired_coupon",
      "test_file": "tests/test_coupon.py",
      "status": "passed",
      "duration_ms": 123,
      "failure_message": null
    }
  ],
  "total": 1
}
```

Contract boundary:

- V1 Test Run APIs execute pytest and minimal Playwright work only through
  backend-controlled command assembly or configured TestCommand allowlists.
- The target repository is readonly when possible; generated AutomationDraft
  code is copied to a Chtest-managed runtime artifact/workspace before
  execution.
- Network access is disabled by default and must be represented in
  `network_enabled`.
- Runtime manifest, dependency snapshot, environment snapshot, stdout, stderr,
  and JUnit files are represented as artifact metadata when available.
- Playwright minimal execution may additionally return `playwright_trace` and
  `screenshot` artifacts.
- This API does not create reports, QualityGateDecision records, CI/CD workflow
  state, FailureAnalysis records, RAG runtime calls, MCP runtime dependencies,
  RBAC, tenants, or permissions.

### 6.4 Playwright Minimal Execution

Playwright minimal execution reuses `POST /api/test-runs` and
`GET /api/test-runs/{id}`. It does not introduce a separate
`POST /api/playwright-runs` endpoint in V1.

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "automation_draft_id": "00000000-0000-0000-0000-000000001011",
  "test_command_id": null,
  "reason": "run approved Playwright smoke draft",
  "runner_mode": "playwright_local"
}
```

Request rules:

- Exactly one execution source is required: approved Playwright
  `automation_draft_id` or configured Playwright `test_command_id`.
- `automation_draft_id` must reference an AutomationDraft with
  `status=approved` and `target_framework=playwright`.
- `test_command_id` must reference a configured TestCommand with
  `command_type=playwright` and passing allowlist validation.
- Playwright commands are backend assembled or validated from allowlisted
  `npx playwright test ...` style commands.
- V1 supports local Playwright smoke execution only. It does not expose
  browser grid, device matrix, or low-code step editing.

Response model: `TestRunRead` with embedded `TestResultRead` items and
Playwright artifact metadata.

Response artifact examples:

```json
[
  {
    "artifact_type": "stdout",
    "file_path": "projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001311/stdout.log"
  },
  {
    "artifact_type": "stderr",
    "file_path": "projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001311/stderr.log"
  },
  {
    "artifact_type": "playwright_trace",
    "file_path": "projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001311/trace.zip"
  },
  {
    "artifact_type": "screenshot",
    "file_path": "projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001311/screenshot.png"
  }
]
```

Contract boundary:

- Playwright minimal execution records TestRun, TestResult, stdout/stderr,
  trace, screenshot, and runtime artifact metadata.
- It does not create reports, FailureAnalysis, QualityGateDecision, CI/CD
  workflow state, RAG runtime calls, MCP runtime dependencies, RBAC, tenants, or
  permissions.

## 7. Failure Analysis APIs

### 7.1 Start Failure Analysis

`POST /api/test-runs/{id}/failure-analysis`

Request:

```json
{
  "prompt_version": "failure_analysis:v1",
  "skill_version": "failure-analysis-skill:v1",
  "model_provider": "mock",
  "model_name": "mock-failure-analysis"
}
```

Rules:

- The TestRun must exist and belong to the default V1 workspace.
- FailureAnalysis is evidence-first. It must inspect TestRun parsed_result,
  TestResult rows, stdout/stderr/JUnit/trace/screenshot artifacts when
  available.
- Missing or weak evidence must produce
  `classification=insufficient_evidence` and low confidence.
- V1 uses deterministic mock provider output unless a later task explicitly
  enables a real provider.
- This endpoint does not create AutomationRepairTask or Report records.

Response 202:

```json
{
  "ai_task_id": "00000000-0000-0000-0000-000000001501",
  "failure_analysis_id": "00000000-0000-0000-0000-000000001502",
  "status": "draft"
}
```

### 7.2 Get Failure Analysis

`GET /api/test-runs/{id}/failure-analysis`

Response 200:

```json
{
  "id": "00000000-0000-0000-0000-000000001502",
  "project_id": "00000000-0000-0000-0000-000000000101",
  "test_run_id": "00000000-0000-0000-0000-000000001301",
  "test_result_id": null,
  "ai_task_id": "00000000-0000-0000-0000-000000001501",
  "classification": "test_script_issue",
  "confidence": 0.82,
  "summary": "The test failed because fixture coupon_client is not defined.",
  "root_cause": "pytest fixture lookup failed before business assertion ran.",
  "evidence_artifact_ids": ["00000000-0000-0000-0000-000000001601"],
  "suggested_actions": ["Add fixture coupon_client or update the test to use existing fixture api_client"],
  "status": "draft"
}
```

Response model: `FailureAnalysisRead`.

### 7.3 Create Automation Repair Task

`POST /api/automation-repair-tasks`

Request:

```json
{
  "automation_draft_id": "00000000-0000-0000-0000-000000001001",
  "failed_test_run_id": "00000000-0000-0000-0000-000000001301",
  "failure_analysis_id": "00000000-0000-0000-0000-000000001501",
  "prompt_version": "automation_draft_generation:v1",
  "skill_version": "automation-draft-skill:v1",
  "model_provider": "mock",
  "model_name": "mock-automation-repair"
}
```

Response 202:

```json
{
  "automation_repair_task_id": "00000000-0000-0000-0000-000000001701",
  "ai_task_id": "00000000-0000-0000-0000-000000001702",
  "status": "running"
}
```

Repair tasks cannot automatically overwrite an approved AutomationDraft. Any repaired draft candidate remains review-gated.

## 8. Report APIs

### 8.1 Create Report

`POST /api/reports`

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "report_type": "automation_execution",
  "related_entity_type": "TestRun",
  "related_entity_id": "00000000-0000-0000-0000-000000001301"
}
```

Rules:

- Slice 14 supports `report_type=automation_execution` only.
- `related_entity_type` must be `TestRun`.
- The related TestRun must have TestResult rows or execution artifacts.
- Report generation must create `evidence_manifest.json` artifact metadata.
- Report conclusion must be derived from TestRun parsed_result, TestResult
  rows, FailureAnalysis when available, and artifact evidence.
- If required evidence is missing, conclusion must be
  `insufficient_evidence`; reports must not mark execution as passed without
  evidence.
- This endpoint does not create CI/CD quality reports or QualityGateDecision
  records.

Response 202:

```json
{
  "report_id": "00000000-0000-0000-0000-000000001401",
  "status": "generating",
  "evidence_manifest_artifact_id": "00000000-0000-0000-0000-000000001402"
}
```

### 8.2 Get Report

`GET /api/reports/{id}`

Response 200:

```json
{
  "id": "00000000-0000-0000-0000-000000001401",
  "project_id": "00000000-0000-0000-0000-000000000101",
  "report_type": "automation_execution",
  "title": "Automation execution report",
  "related_entity_type": "TestRun",
  "related_entity_id": "00000000-0000-0000-0000-000000001301",
  "status": "ready",
  "conclusion": "passed",
  "summary": "3 pytest tests passed.",
  "metrics": {"total": 3, "passed": 3, "failed": 0},
  "artifact_ids": [
    "00000000-0000-0000-0000-000000001402",
    "00000000-0000-0000-0000-000000001403"
  ],
  "evidence_manifest": {
    "report_id": "00000000-0000-0000-0000-000000001401",
    "conclusion": "passed",
    "evidence": [
      {
        "artifact_id": "00000000-0000-0000-0000-000000001601",
        "artifact_type": "stdout",
        "supports_claim": "pytest command completed successfully",
        "required": true
      }
    ],
    "missing_evidence": []
  },
  "artifacts": [
    {"artifact_type": "report_md", "file_path": "projects/00000000-0000-0000-0000-000000000101/reports/00000000-0000-0000-0000-000000001401/report.md"},
    {"artifact_type": "report_json", "file_path": "projects/00000000-0000-0000-0000-000000000101/reports/00000000-0000-0000-0000-000000001401/report.json"},
    {"artifact_type": "report_json", "file_path": "projects/00000000-0000-0000-0000-000000000101/reports/00000000-0000-0000-0000-000000001401/evidence_manifest.json"}
  ]
}
```

Response model: `ReportRead`.

## 9. AI Task API

`GET /api/ai-tasks/{id}`

Response 200:

```json
{
  "id": "00000000-0000-0000-0000-000000000501",
  "agent_name": "RequirementReviewAgent",
  "task_type": "requirement_review",
  "status": "succeeded",
  "prompt_version": "requirement_review:v1",
  "skill_version": "requirement-review-skill:v1",
  "model_provider": "mock",
  "model_name": "mock-requirement-review",
  "token_usage": {"input_tokens": 1200, "output_tokens": 800},
  "used_knowledge": false,
  "used_context_artifact_ids": ["00000000-0000-0000-0000-000000000371"],
  "context_manifest_artifact_id": "00000000-0000-0000-0000-000000000372",
  "artifacts": [
    {"artifact_type": "raw_llm_output", "file_path": "projects/00000000-0000-0000-0000-000000000101/ai-tasks/00000000-0000-0000-0000-000000000501/raw.json"}
  ]
}
```
