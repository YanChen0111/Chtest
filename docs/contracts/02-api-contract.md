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
  "use_knowledge": false
}
```

Response 202:

```json
{
  "ai_task_id": "00000000-0000-0000-0000-000000000501",
  "requirement_id": "00000000-0000-0000-0000-000000000401",
  "status": "pending",
  "next_poll_url": "/api/ai-tasks/00000000-0000-0000-0000-000000000501"
}
```

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
  "model_name": "mock-case-generator"
}
```

Response 202:

```json
{
  "case_generation_task_id": "00000000-0000-0000-0000-000000000701",
  "ai_task_id": "00000000-0000-0000-0000-000000000702",
  "status": "pending"
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

Response 200 returns AutomationDraft read model with `draft_code`, `target_framework`, `suggested_file_path`, `execution_strategy`, `runtime_artifact_id`, `execution_notes`, `risk_notes`, and artifacts.

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
  "status": "approved",
  "execution_strategy": "artifact_runtime_copy"
}
```

AutomationDraft uses `edit -> edited -> approve -> approved`. It does not use `approve_after_edit`.

Approval does not write generated code into the target business repository. When a TestRun is created from an approved AutomationDraft, the backend copies `draft_code` into a Chtest-managed artifact runtime path and stores the copied file as `runtime_artifact_id`.

## 5. Git Quality APIs

### 5.1 Create Change Set

`POST /api/git/change-sets`

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "repository_id": "00000000-0000-0000-0000-000000000301",
  "source_type": "local_diff",
  "base_ref": "main",
  "head_ref": "HEAD"
}
```

Response 202:

```json
{
  "change_set_id": "00000000-0000-0000-0000-000000001101",
  "status": "created"
}
```

### 5.2 Analyze Change Set

`POST /api/git/change-sets/{id}/analyze`

Request:

```json
{
  "prompt_version": "git_diff_analysis:v1",
  "skill_version": "regression-selection-skill:v1",
  "model_provider": "mock",
  "model_name": "mock-git-analysis"
}
```

Response 202 returns AITask reference.

### 5.3 Generate Unit Test Patch

`POST /api/git/change-sets/{id}/unit-test-patches`

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

### 5.4 Approve Unit Test Patch

`POST /api/git/unit-test-patches/{id}/approve`

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

## 6. Test Run APIs

### 6.1 Create Test Run

`POST /api/test-runs`

Request:

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "test_command_id": "00000000-0000-0000-0000-000000000302",
  "automation_draft_id": "00000000-0000-0000-0000-000000001001",
  "change_set_id": null,
  "reason": "run approved automation draft"
}
```

Response 202:

```json
{
  "test_run_id": "00000000-0000-0000-0000-000000001301",
  "tool_invocation_id": "00000000-0000-0000-0000-000000001302",
  "status": "queued"
}
```

### 6.2 Get Test Run

`GET /api/test-runs/{id}`

Response 200:

```json
{
  "id": "00000000-0000-0000-0000-000000001301",
  "status": "passed",
  "exit_code": 0,
  "duration_ms": 3560,
  "parsed_result": {
    "total": 3,
    "passed": 3,
    "failed": 0,
    "skipped": 0,
    "error": 0
  },
  "test_results": [],
  "artifacts": [
    {"artifact_type": "stdout", "file_path": "projects/00000000-0000-0000-0000-000000000101/test-runs/00000000-0000-0000-0000-000000001301/stdout.log"}
  ]
}
```

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

Response 202:

```json
{
  "ai_task_id": "00000000-0000-0000-0000-000000001501",
  "status": "pending"
}
```

### 7.2 Get Failure Analysis

`GET /api/test-runs/{id}/failure-analysis`

Response 200:

```json
{
  "id": "00000000-0000-0000-0000-000000001502",
  "classification": "test_script_issue",
  "confidence": 0.82,
  "summary": "The test failed because fixture coupon_client is not defined.",
  "root_cause": "pytest fixture lookup failed before business assertion ran.",
  "evidence_artifact_ids": ["00000000-0000-0000-0000-000000001601"],
  "suggested_actions": ["Add fixture coupon_client or update the test to use existing fixture api_client"]
}
```

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

Response 202:

```json
{
  "report_id": "00000000-0000-0000-0000-000000001401",
  "status": "generating"
}
```

### 8.2 Get Report

`GET /api/reports/{id}`

Response 200:

```json
{
  "id": "00000000-0000-0000-0000-000000001401",
  "report_type": "automation_execution",
  "status": "ready",
  "conclusion": "passed",
  "summary": "3 pytest tests passed.",
  "metrics": {"total": 3, "passed": 3, "failed": 0},
  "artifacts": [
    {"artifact_type": "report_md", "file_path": "projects/00000000-0000-0000-0000-000000000101/reports/00000000-0000-0000-0000-000000001401/report.md"}
  ]
}
```

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
  "artifacts": [
    {"artifact_type": "raw_llm_output", "file_path": "projects/00000000-0000-0000-0000-000000000101/ai-tasks/00000000-0000-0000-0000-000000000501/raw.json"}
  ]
}
```
