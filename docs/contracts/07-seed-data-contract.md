# Chtest Seed Data Contract

## 1. Purpose

This document defines the minimum seed data required for Chtest V1 local development, tests, and the V1 Minimum Demo Golden Path.

Seed data must be deterministic so tests, mock providers, and demo flows are repeatable.

## 2. Required Seed Data

### 2.1 Default Workspace

| Field | Value |
|---|---|
| name | Personal Workspace |
| status | active |

### 2.2 Default User

| Field | Value |
|---|---|
| username | default |
| display_name | Default User |
| status | active |

### 2.3 Built-In PromptVersion

Minimum built-in prompts:

- `requirement_review:v1`
- `risk_matrix:v1`
- `case_generation:v1`
- `case_review:v1`
- `automation_draft_generation:v1`
- `failure_analysis:v1`
- `report_generation:v1`
- `git_diff_analysis:v1`
- `unit_test_generation:v1`
- `regression_selection:v1`

### 2.4 Built-In SkillVersion

Minimum built-in skills:

- `requirement-review-skill:v1`
- `test-case-generation-skill:v1`
- `testcase-review-skill:v1`
- `automation-draft-skill:v1`
- `tool-execution-skill:v1`
- `failure-analysis-skill:v1`
- `report-generation-skill:v1`
- `unit-test-generation-skill:v1`
- `regression-selection-skill:v1`

### 2.5 Built-In ToolDefinition

Minimum built-in tools:

| Tool | Type | Risk | Approval | V1 Use |
|---|---|---|---|---|
| TestRunnerTool | test_runner | medium | true by default | pytest execution |
| PlaywrightTool | playwright | medium | true by default | Playwright minimal loop |
| ChangeSetTool | git | low/medium | depends on action | local diff and status |
| ArtifactTool | artifact | low | false | artifact read/write |
| ReportTool | report | low | false | report generation |

### 2.6 Mock Provider

Mock Provider must be enabled by default in local development and tests.

| Field | Value |
|---|---|
| provider | mock |
| default_model | mock-model |
| enabled | true |

### 2.7 V1 Demo ContextArtifact

Minimum demo seed must include one deterministic ContextArtifact:

| Field | Value |
|---|---|
| title | coupon-api-notes.md |
| artifact_type | context_markdown |
| mime_type | text/markdown |
| owner_entity_type | Project |
| owner_entity_id | demo project id |
| source_ref | seed:coupon-api-notes.md |
| safe_to_show | server-computed true after scan |
| redaction_applied | false unless scan finds sensitive content |

Content:

```markdown
# Coupon API Notes

POST /api/coupons/validate checks coupon availability.
Expired coupons return COUPON_EXPIRED.
Coupons cannot be combined with points.
```

## 3. Rules

- Seed data must be idempotent.
- Seed data must not contain real secrets.
- Seed data must not require external network.
- Built-in Prompt/Skill content must be versioned and hashable.
- Built-in ToolDefinition must follow `docs/contracts/01-data-model-contract.md`.
- If seed data changes, update `docs/fixtures/00-v1-demo-path.md` when relevant.
- Seed ContextArtifact must pass the same secret scan and redaction rules as user-created ContextArtifact.
