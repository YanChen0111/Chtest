# Chtest Data Model Contract

## 1. Purpose

This document is the field-level data model contract for Chtest V1. ORM models, Pydantic schemas, API handlers, fixtures, and reports must follow this contract.

V1 uses PostgreSQL. All tables include these base fields unless explicitly stated otherwise:

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| id | uuid | yes | gen_random_uuid() | Primary key |
| created_at | timestamptz | yes | now() | Creation time |
| updated_at | timestamptz | yes | now() | Update time |
| created_by | uuid | no | default_user_id | V1 default user |
| updated_by | uuid | no | default_user_id | V1 default user |

V1 is single-user, but owner fields are kept for later extension.

## 2. Enums

### 2.1 General Enums

| Enum | Values |
|---|---|
| Priority | P0, P1, P2, P3 |
| TestType | functional, api, ui, performance, security, compatibility, regression, unit |
| SourceType | manual, ai, import, git |
| RiskLevel | low, medium, high, critical |
| ReviewStatus | pending_review, approved, approved_after_edit, rejected, needs_optimization, optimization_pending_review, unavailable |
| EntityStatus | active, archived, deleted |

### 2.2 AI And Execution Enums

| Enum | Values |
|---|---|
| AITaskStatus | created, pending, running, waiting_review, waiting_approval, succeeded, failed, cancelled |
| CandidateStatus | generated, under_review, approved, approved_after_edit, rejected, needs_optimization, optimization_pending_review, archived |
| AutomationDraftStatus | draft_generated, under_review, approved, edited, rejected, execution_pending, executed, execution_failed, promoted, archived |
| PatchStatus | generated, scope_validated, scope_rejected, awaiting_review, approved, rejected, edited, applied, apply_failed, replaced |
| ToolInvocationStatus | created, waiting_approval, approved, rejected, running, succeeded, failed, timeout, cancelled |
| TestRunStatus | created, queued, running, passed, failed, error, cancelled, timeout |
| TestResultStatus | passed, failed, skipped, error |
| ReportStatus | draft, generating, ready, failed, archived |
| PromptStatus | draft, active, deprecated |
| SkillStatus | draft, active, deprecated |
| ToolDefinitionStatus | active, disabled, archived |
| KnowledgeAdapterStatus | not_configured, disabled, configured_stub |
| FailureClassification | product_defect, test_script_issue, environment_issue, test_data_issue, dependency_issue, flaky_test, insufficient_evidence |
| ArtifactOwnerType | Project, AITask, Requirement, RequirementReview, CaseGenerationTask, AutomationDraft, TestRun, Report, CICDRun, ToolInvocation |
| LLMCallStatus | started, succeeded, failed, timeout, schema_invalid |
| AutomationRepairStatus | created, running, candidate_generated, waiting_review, approved, rejected, failed |
| ReviewHistoryAction | open_review, approve, approve_after_edit, reject, edit, request_optimization, compute_quality_gate, recompute_quality_gate |

## 3. Workspace

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| name | varchar(120) | yes | Personal Workspace | Unique |
| description | text | no | null | Description |
| status | EntityStatus | yes | active | Status |

Relationship: Workspace 1:N Project.

## 4. User

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| username | varchar(80) | yes | default | Unique |
| display_name | varchar(120) | yes | Default User | Display name |
| email | varchar(255) | no | null | Optional in V1 |
| status | EntityStatus | yes | active | Status |

## 5. Project

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| workspace_id | uuid | yes | default_workspace | FK Workspace |
| name | varchar(160) | yes | none | Unique inside workspace |
| description | text | no | null | Description |
| default_language | varchar(60) | no | python | python/javascript/java |
| default_test_type | TestType | no | functional | Default test type |
| status | EntityStatus | yes | active | Status |

Relationship: Project 1:N Module, Repository, Environment, TestCommand, Requirement, TestCase, AITask, Report.

## 6. Module

Five-level module tree.

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| parent_id | uuid | no | null | FK Module |
| name | varchar(160) | yes | none | Unique under same parent |
| level | int | yes | 1 | 1 to 5 |
| path | varchar(800) | yes | generated | Example `/checkout/coupon` |
| sort_order | int | yes | 0 | Sort order |
| status | EntityStatus | yes | active | Status |

Constraint: level between 1 and 5.

## 7. Repository

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| name | varchar(160) | yes | none | Unique inside project |
| local_path | text | yes | none | Must be under allowlisted root |
| default_base_branch | varchar(120) | no | main | Default base branch |
| language_hint | varchar(80) | no | null | python/javascript/java |
| status | EntityStatus | yes | active | Status |

## 8. Environment

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| name | varchar(120) | yes | dev | dev/test/local-prod |
| variables_json | jsonb | yes | {} | Variables; sensitive values stored as references |
| status | EntityStatus | yes | active | Status |

## 9. TestCommand

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| repository_id | uuid | no | null | FK Repository |
| environment_id | uuid | no | null | FK Environment |
| name | varchar(160) | yes | none | Example `pytest unit` |
| command | text | yes | none | Must match allowlist rules |
| working_directory | text | yes | none | Must be under repository path |
| command_type | varchar(40) | yes | pytest | pytest, npm, playwright, newman |
| timeout_seconds | int | yes | 600 | Max runtime |
| parse_junit | bool | yes | true | Parse JUnit output |
| parse_coverage | bool | yes | false | Parse coverage output |
| status | EntityStatus | yes | active | Status |

## 10. Requirement

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| module_id | uuid | no | null | FK Module |
| title | varchar(255) | yes | none | Requirement title |
| content | text | yes | none | Markdown or plain text |
| source_type | SourceType | yes | manual | Source |
| source_ref | text | no | null | File name, URL, or requirement id |
| status | EntityStatus | yes | active | Status |

## 11. RequirementReview

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| requirement_id | uuid | yes | none | FK Requirement |
| ai_task_id | uuid | yes | none | FK AITask |
| completeness_score | int | yes | 0 | 0-100 |
| clarity_score | int | yes | 0 | 0-100 |
| consistency_score | int | yes | 0 | 0-100 |
| testability_score | int | yes | 0 | 0-100 |
| feasibility_score | int | yes | 0 | 0-100 |
| logic_score | int | yes | 0 | 0-100 |
| overall_score | int | yes | 0 | 0-100 |
| issues_json | jsonb | yes | [] | Issue list |
| clarification_questions_json | jsonb | yes | [] | Clarification questions |
| test_design_notes_json | jsonb | yes | [] | Test design suggestions |
| status | varchar(40) | yes | draft | draft, reviewed, confirmed |

## 12. RiskItem

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| requirement_review_id | uuid | no | null | FK RequirementReview |
| title | varchar(255) | yes | none | Risk title |
| risk_level | RiskLevel | yes | medium | Risk level |
| category | varchar(80) | yes | business | business, technical, data, environment, regression |
| impact | text | yes | none | Impact |
| suggestion | text | yes | none | Test strategy suggestion |
| status | EntityStatus | yes | active | Status |

## 13. CaseGenerationTask

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| requirement_id | uuid | yes | none | FK Requirement |
| requirement_review_id | uuid | no | null | FK RequirementReview |
| ai_task_id | uuid | yes | none | FK AITask |
| target_test_types | text[] | yes | {} | Target test types |
| status | AITaskStatus | yes | created | Task status |
| generated_count | int | yes | 0 | Candidate count |

## 14. GeneratedCaseCandidate

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| generation_task_id | uuid | yes | none | FK CaseGenerationTask |
| project_id | uuid | yes | none | FK Project |
| module_id | uuid | no | null | FK Module |
| title | varchar(255) | yes | none | Title |
| priority | Priority | yes | P2 | Priority |
| test_type | TestType | yes | functional | Test type |
| precondition | text | no | null | Preconditions |
| steps_json | jsonb | yes | [] | Step array |
| expected_results_json | jsonb | yes | [] | Expected results |
| input_data_json | jsonb | yes | {} | Input data |
| tags | text[] | yes | {} | Tags |
| requirement_refs_json | jsonb | yes | [] | Requirement references |
| risk_refs_json | jsonb | yes | [] | Risk references |
| ai_reason | text | yes | none | AI generation reason |
| duplicate_of_case_id | uuid | no | null | Potential duplicate case |
| status | CandidateStatus | yes | generated | Candidate status |
| review_comment | text | no | null | Human review comment |

## 15. TestCase

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| module_id | uuid | no | null | FK Module |
| source_candidate_id | uuid | no | null | FK GeneratedCaseCandidate |
| title | varchar(255) | yes | none | Title |
| priority | Priority | yes | P2 | Priority |
| test_type | TestType | yes | functional | Test type |
| precondition | text | no | null | Preconditions |
| steps_json | jsonb | yes | [] | Steps |
| expected_results_json | jsonb | yes | [] | Expected results |
| input_data_json | jsonb | yes | {} | Test data |
| tags | text[] | yes | {} | Tags |
| source_type | SourceType | yes | ai | Source |
| review_status | ReviewStatus | yes | approved | Review status |
| status | EntityStatus | yes | active | Status |

## 16. AutomationDraft

AutomationDraft is a core V1 entity that connects reviewed cases and executable tests.

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| test_case_id | uuid | no | null | FK TestCase |
| requirement_id | uuid | no | null | FK Requirement |
| ai_task_id | uuid | yes | none | FK AITask |
| target_framework | varchar(60) | yes | pytest | pytest, playwright |
| title | varchar(255) | yes | none | Draft title |
| draft_code | text | yes | none | AI-generated code draft |
| draft_language | varchar(60) | yes | python | python/typescript |
| suggested_file_path | text | no | null | Suggested test path |
| execution_notes | text | no | null | How to run and prerequisites |
| risk_notes | text | no | null | Known risks and review focus |
| execution_strategy | varchar(60) | yes | artifact_runtime_copy | artifact_runtime_copy in V1 |
| approval_required | bool | yes | true | Must be approved in V1 |
| status | AutomationDraftStatus | yes | draft_generated | Status |
| review_comment | text | no | null | Review comment |
| runtime_artifact_id | uuid | no | null | Artifact for approved temporary runtime file |
| promoted_artifact_id | uuid | no | null | Promoted artifact |

V1 execution rule: an approved AutomationDraft is copied into a Chtest-managed artifact runtime directory before execution. It is not written directly into the target business repository.

V2 Newman rule: Newman API execution uses configured TestCommand records with
`command_type=newman`. It is not generated from AutomationDraft in Slice 18.
The command must match Newman allowlist rules and must not contain arbitrary
shell operators.

## 17. CICDRun

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| repository_id | uuid | no | null | FK Repository |
| source_type | varchar(40) | yes | local_diff | local_diff, uploaded_diff, manual_check, ci_import |
| trigger_type | varchar(40) | yes | manual | manual in V1; imported in Slice 20; webhook, pr, scheduled are future only |
| provider | varchar(40) | yes | local | local in V1; imported/github_actions/gitlab_ci/jenkins/circleci/buildkite/other labels are evidence only in Slice 20 |
| pipeline_name | varchar(160) | no | null | Optional local pipeline/check name |
| base_ref | varchar(160) | no | null | Base commit or branch |
| head_ref | varchar(160) | no | null | Head commit or branch |
| summary | text | no | null | Change summary |
| overall_risk | RiskLevel | yes | medium | Overall risk |
| quality_gate_status | varchar(40) | yes | pending | pending, passed, failed, needs_review |
| status | varchar(40) | yes | created | created, imported, import_failed, analyzed, patch_ready, tests_running, reported, archived |

V1 Slice 15 boundary:

- `source_type` supports `local_diff` and `manual_check`; `uploaded_diff` is
  accepted only as stored diff text, not as remote provider ingestion.
- `trigger_type` is `manual` only.
- `provider` is `local` only.
- `quality_gate_status` remains `pending` in Slice 15 because
  QualityGateDecision belongs to Slice 16.
- Slice 15 must not trigger merge, push, release, deployment, webhook handling,
  PR comments, or remote CI provider synchronization.

V2 Slice 20 import boundary:

- `source_type=ci_import` is allowed only for static CI metadata imported into
  Chtest as evidence.
- `trigger_type=imported` may be used to distinguish imported facts from local
  manual runs. It must not imply webhook, PR, scheduled, or remote-triggered
  execution.
- `provider` may store inert labels such as `imported`, `github_actions`,
  `gitlab_ci`, or `jenkins` only as source metadata. Provider labels must not
  enable provider APIs, credential lookup, webhook processing, pipeline
  triggering, reruns, PR comments, deployment, release, or remote status update.
- Imported CI metadata may include pipeline name, job name, inert run URL,
  commit SHA, base/head refs, conclusion, started/finished timestamps, duration,
  changed files, and artifact references. These values live in
  `ci_run_metadata.json` Artifact content and metadata unless a later contract
  explicitly promotes individual fields onto CICDRun. They are not remote
  integration configuration.
- Imported CI conclusion is evidence only. It must not automatically create a
  `QualityGateDecision` or change `quality_gate_status` to `passed`.

## 18. CICDChangedFile

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| cicd_run_id | uuid | yes | none | FK CICDRun |
| path | text | yes | none | File path |
| old_path | text | no | null | Rename source path |
| change_type | varchar(40) | yes | modified | added, modified, deleted, renamed |
| language | varchar(60) | no | null | Language |
| file_role | varchar(60) | yes | unknown | source, test, docs, config, migration, fixture, build, unknown |
| risk_level | RiskLevel | yes | medium | File risk |
| risk_reasons_json | jsonb | yes | [] | Risk reasons |
| lines_added | int | yes | 0 | Added lines |
| lines_deleted | int | yes | 0 | Deleted lines |

CICDChangedFile evidence rules:

- Rows are derived from local unified diff text, manual changed-file input, or
  Slice 20 static CI metadata imports.
- `file_role` is deterministic from path and extension.
- `risk_reasons_json` must explain why `risk_level` was assigned.
- Every changed file in `changed_files.json` should have a matching
  CICDChangedFile row.
- Imported changed files must preserve provider-supplied path/change metadata
  only as local evidence. They must not cause repository checkout, fetch, merge,
  pull, push, or remote comparison.

## 19. UnitTestPatch

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| cicd_run_id | uuid | yes | none | FK CICDRun |
| ai_task_id | uuid | yes | none | FK AITask |
| patch_text | text | yes | none | Unified diff |
| target_framework | varchar(60) | yes | pytest | pytest/jest/vitest |
| scope_gate_result_json | jsonb | yes | {} | Path gate result |
| test_intent | text | yes | none | Test intent |
| coverage_target_json | jsonb | yes | [] | Coverage target |
| status | PatchStatus | yes | generated | Status |
| review_comment | text | no | null | Review comment |

UnitTestPatch rules:

- UnitTestPatch is review-gated. Generated patches must not be applied until a
  user approves them.
- `scope_gate_result_json` must include `allowed`, `checked_paths`,
  `blocked_paths`, `forbidden_patterns`, `risk_level`, and `reason` when
  rejected.
- PatchScopeGate must reject any patch that modifies business source files,
  configuration, migrations, generated artifacts, or files outside allowed test
  directories.
- `scope_rejected` patches cannot transition to `approved`.
- Applied patches must preserve the original `patch_text` as evidence and write
  an applied patch artifact.

## 20. TestRun

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| cicd_run_id | uuid | no | null | FK CICDRun |
| automation_draft_id | uuid | no | null | FK AutomationDraft |
| test_command_id | uuid | no | null | FK TestCommand |
| tool_invocation_id | uuid | no | null | FK ToolInvocation |
| name | varchar(255) | yes | none | Run name |
| command | text | yes | none | Executed command |
| working_directory | text | yes | none | Working directory |
| runner_mode | varchar(40) | yes | local_subprocess | local_subprocess, playwright_local, newman_local, docker_runner |
| run_workspace | text | no | null | Isolated execution workspace |
| repository_readonly | bool | yes | true | Target repository mounted/read as readonly when possible |
| network_enabled | bool | yes | false | Network access during run |
| runtime_artifact_ids | uuid[] | yes | {} | Exact runtime files executed |
| dependency_snapshot_artifact_id | uuid | no | null | Python/Node/lockfile/image snapshot |
| environment_snapshot_artifact_id | uuid | no | null | Redacted environment snapshot |
| status | TestRunStatus | yes | created | Status |
| exit_code | int | no | null | Exit code |
| duration_ms | int | no | null | Duration |
| parsed_result_json | jsonb | yes | {} | Parsed aggregate result |

Newman TestRun rules:

- `runner_mode=newman_local` is used for approved local Newman API execution.
- Newman TestRuns must reference `test_command_id`; Slice 18 does not execute
  Newman from AutomationDraft.
- `parsed_result_json` must include aggregate request/assertion counts:
  `total`, `passed`, `failed`, `skipped`, `error`, `request_count`, and
  `assertion_count`.
- `failed` means Newman completed and one or more API assertions failed.
- `error` means Newman could not run, timed out, or produced unparseable output.
- `network_enabled` remains explicit. Local fixture tests should keep it false;
  any future live API collection must display the chosen network policy.

## 21. QualityGateDecision

QualityGateDecision records one computed CI/CD quality gate result for a CICDRun. V1 computes it from local diff risk, PatchScopeGate, new test results, regression results, and failure analysis evidence. It does not trigger merge, push, or deployment automatically. Recomputing the gate creates a new QualityGateDecision record and updates `CICDRun.quality_gate_status`; old decisions remain as evidence history.

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| cicd_run_id | uuid | yes | none | FK CICDRun |
| status | varchar(40) | yes | needs_review | passed, failed, needs_review |
| summary | text | yes | none | Human-readable gate conclusion |
| blocking_reasons_json | jsonb | yes | [] | Reasons blocking merge/release readiness |
| evidence_artifact_ids | uuid[] | yes | {} | Diff, patch, JUnit, logs, failure analysis |
| decided_by | varchar(40) | yes | system | system in V1; user_override is V2+ |
| status_detail_json | jsonb | yes | {} | Patch/test/regression/failure-analysis signals |

QualityGateDecision rules:

- `passed` requires passing PatchScopeGate evidence, approved/applied
  UnitTestPatch evidence when a patch is used, passing new-test evidence, and
  passing regression evidence or a documented low-risk regression waiver.
- `failed` requires at least one concrete blocking reason, such as scope
  rejection, failed tests, failed regression, or high-risk uncovered changes.
- `needs_review` is required when evidence is missing, ambiguous, or manually
  risky.
- Imported CI conclusion can be cited in `status_detail_json` and
  `evidence_artifact_ids`, but it is not sufficient by itself for `passed`.
  Existing local evidence requirements still apply unless a later contract
  explicitly changes them.
- QualityGateDecision never triggers merge, push, release, deployment, remote CI
  status updates, or PR comments.

## 21.1 ReviewHistory

ReviewHistory records local append-only review attribution events across the
existing review-gated evidence loop. It is evidence metadata, not an
authorization, login, RBAC, tenant, assignment, notification, or enterprise
audit model.

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| entity_type | varchar(80) | yes | none | GeneratedCaseCandidate, TestCase, AutomationDraft, UnitTestPatch, CICDRun, QualityGateDecision, AutomationRepairTask |
| entity_id | uuid | yes | none | Reviewed or decision entity id |
| related_entity_type | varchar(80) | no | null | Optional display/query relation, for example QualityGateDecision -> CICDRun |
| related_entity_id | uuid | no | null | Optional related entity id |
| action | varchar(80) | yes | none | ReviewHistoryAction or deterministic workflow action label |
| from_status | varchar(80) | no | null | Status before successful action |
| to_status | varchar(80) | no | null | Status after successful action or computed status |
| reviewer | varchar(120) | yes | Default User | Local display label, not an auth principal |
| comment | text | no | null | Human review comment or computed decision summary |
| evidence_artifact_ids | uuid[] | yes | {} | Existing Artifact ids supporting the event |
| metadata_json | jsonb | yes | {} | Safe workflow-specific metadata such as quality_gate_decision_id |
| created_at | timestamptz | yes | now() | Event time |

ReviewHistory rules:

- Records are append-only through the public service/API surface. Existing
  review actions may append records; clients must not overwrite or delete
  history records as part of Slice 21.
- `reviewer` is a local display label. The default is `Default User` and it
  must not be treated as an authenticated user id, role, permission, tenant, or
  session principal.
- ReviewHistory must not decide whether an action is allowed. Existing
  state-machine and service validation remains the authority.
- Record only successful review or decision events. Failed validation,
  forbidden transitions, and rejected API payloads must not append history.
- `evidence_artifact_ids` references persisted Artifact rows. ReviewHistory
  must not duplicate raw artifact content, secrets, tokens, or remote provider
  credentials in `comment` or `metadata_json`.
- Slice 21 covers local events for generated case review, AutomationDraft
  review/edit/approval where supported, UnitTestPatch approval/rejection, and
  QualityGateDecision compute/recompute.
- Generated case approval history should be written for the
  GeneratedCaseCandidate. The created TestCase may display that history through
  `source_candidate_id`; it should not duplicate an identical approval record
  unless a later contract defines a separate TestCase review action.
- QualityGateDecision compute history should record the created
  QualityGateDecision as `entity_type=QualityGateDecision` and may set
  `related_entity_type=CICDRun` so the CI/CD quality page can display the event
  from the run. `from_status` and `to_status` describe the
  `CICDRun.quality_gate_status` transition caused by the recompute.
- ReviewHistory must not introduce users, roles, permissions, tenants,
  departments, SSO, login/session flows, assignment workflow, notifications,
  team inboxes, PR comments, remote provider governance, or enterprise audit
  policy.

## 22. TestResult

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| test_run_id | uuid | yes | none | FK TestRun |
| test_name | text | yes | none | Case/test node id |
| test_file | text | no | null | Source test file |
| status | TestResultStatus | yes | passed | Result status |
| duration_ms | int | no | null | Duration |
| failure_message | text | no | null | Failure summary |
| failure_artifact_ids | uuid[] | yes | {} | Related artifacts |
| metadata_json | jsonb | yes | {} | Parser-specific metadata |

Newman TestResult metadata rules:

- Newman results are mapped at assertion granularity when available.
- `test_name` should be deterministic, for example
  `collection/folder/request::assertion`.
- `test_file` may be the collection path when known.
- `metadata_json` should include safe fields such as `collection_name`,
  `folder_name`, `request_name`, `assertion_name`, `method`, `url_template`,
  and `iteration`.
- `metadata_json` must not store secrets, bearer tokens, cookies, or raw
  environment values.

## 23. FailureAnalysis

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| test_run_id | uuid | no | null | FK TestRun |
| test_result_id | uuid | no | null | FK TestResult |
| ai_task_id | uuid | yes | none | FK AITask |
| classification | FailureClassification | yes | insufficient_evidence | Classification |
| confidence | numeric(4,3) | yes | 0 | Confidence score from 0.000 to 1.000 |
| evidence_artifact_ids | uuid[] | yes | {} | Evidence artifacts |
| summary | text | yes | none | Human-readable summary |
| root_cause | text | no | null | Evidence-based root cause |
| suggested_actions_json | jsonb | yes | [] | Suggested next actions |
| status | varchar(40) | yes | draft | draft, confirmed, rejected |

## 24. AutomationRepairTask

AutomationRepairTask records an evidence-driven attempt to improve an AutomationDraft after a failed execution. It does not overwrite the approved AutomationDraft silently.

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| automation_draft_id | uuid | yes | none | FK AutomationDraft |
| failed_test_run_id | uuid | yes | none | FK TestRun |
| failure_analysis_id | uuid | no | null | FK FailureAnalysis |
| ai_task_id | uuid | yes | none | FK AITask |
| attempt_index | int | yes | 1 | 1-based attempt count for this draft |
| max_attempts | int | yes | 2 | Default maximum repair attempts |
| repair_reason | text | yes | none | Evidence-based reason for repair |
| repaired_draft_code | text | no | null | Candidate repaired code |
| repaired_artifact_id | uuid | no | null | Artifact containing repaired draft candidate |
| evidence_artifact_ids | uuid[] | yes | {} | stdout/stderr/JUnit/trace/screenshots used |
| status | AutomationRepairStatus | yes | created | Status |
| review_comment | text | no | null | Human review comment |

Rules:

- Repair input must include the failed TestRun runtime manifest and available execution artifacts.
- Repair candidate cannot automatically replace or promote an approved AutomationDraft.
- Repair approval does not execute automatically; it creates or updates a review-gated AutomationDraft candidate.

## 25. Report

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| report_type | varchar(80) | yes | execution | requirement_review, case_quality, automation_execution, cicd_quality, ai_effectiveness |
| title | varchar(255) | yes | none | Report title |
| related_entity_type | varchar(80) | no | null | Related entity type |
| related_entity_id | uuid | no | null | Related entity id |
| status | ReportStatus | yes | draft | Status |
| conclusion | varchar(80) | no | null | passed, failed, needs_attention, insufficient_evidence |
| summary | text | no | null | Summary |
| metrics_json | jsonb | yes | {} | Metrics |
| artifact_ids | uuid[] | yes | {} | Report artifacts |

## 26. AITask

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| agent_name | varchar(120) | yes | none | Agent name |
| task_type | varchar(120) | yes | none | requirement_review, case_generation, automation_draft, failure_analysis |
| prompt_version_id | uuid | yes | none | FK PromptVersion |
| skill_version_id | uuid | yes | none | FK SkillVersion |
| model_provider | varchar(80) | yes | mock | mock/openai-compatible |
| model_name | varchar(120) | yes | mock-model | Model |
| status | AITaskStatus | yes | created | Status |
| input_json | jsonb | yes | {} | Input summary |
| output_json | jsonb | yes | {} | Structured output |
| error_json | jsonb | no | null | Error information |
| token_usage_json | jsonb | yes | {} | Token usage |
| context_artifact_ids | uuid[] | yes | {} | Context artifacts injected into the prompt |
| started_at | timestamptz | no | null | Start time |
| finished_at | timestamptz | no | null | Finish time |

Deterministic knowledge retrieval rules:

- V2 Slice 19 may store deterministic local retrieval summaries in
  `input_json` and `output_json`.
- `input_json` may include `use_knowledge=true`, `knowledge_query_text`,
  `knowledge_query_terms`, and requested retrieval limits.
- `output_json` must include `used_knowledge=true` only when retrieved snippets
  were actually injected into the AI task prompt.
- `output_json.used_context_artifact_ids` must list the exact ContextArtifact
  ids used by deterministic retrieval.
- `output_json.retrieval_evidence_artifact_id` may reference an Artifact with
  `artifact_type=knowledge_retrieval`.
- Retrieval evidence must not be inferred from model text alone; it must cite
  persisted ContextArtifact ids and artifact evidence.

## 27. LLMCallLog

LLMCallLog records each provider call made inside an AITask. AITask is the workflow-level task; LLMCallLog is the per-model-call audit log.

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| ai_task_id | uuid | yes | none | FK AITask |
| prompt_version_id | uuid | yes | none | FK PromptVersion |
| skill_version_id | uuid | yes | none | FK SkillVersion |
| provider | varchar(80) | yes | mock | mock/openai-compatible |
| model_name | varchar(120) | yes | mock-model | Model |
| call_index | int | yes | 1 | 1-based order inside AITask |
| status | LLMCallStatus | yes | started | Call status |
| request_artifact_id | uuid | no | null | Artifact containing provider request |
| response_artifact_id | uuid | no | null | Artifact containing raw provider response |
| parsed_artifact_id | uuid | no | null | Artifact containing parsed structured output |
| schema_validation_artifact_id | uuid | no | null | Artifact containing schema validation result |
| input_summary_json | jsonb | yes | {} | Safe input summary for UI |
| output_summary_json | jsonb | yes | {} | Safe output summary for UI |
| token_usage_json | jsonb | yes | {} | Provider token usage |
| latency_ms | int | no | null | Provider call latency |
| error_json | jsonb | no | null | Safe error summary |
| started_at | timestamptz | no | null | Start time |
| finished_at | timestamptz | no | null | Finish time |

Relationship: AITask 1:N LLMCallLog.

## 28. PromptVersion

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| name | varchar(160) | yes | none | Name |
| version | varchar(40) | yes | v1 | Version |
| hash | varchar(128) | yes | none | Content hash |
| agent_name | varchar(120) | yes | none | Agent |
| content | text | yes | none | Prompt content |
| input_schema_json | jsonb | yes | {} | Input schema |
| output_schema_json | jsonb | yes | {} | Output schema |
| status | PromptStatus | yes | active | Status |

Unique constraint: name + version.

## 29. SkillVersion

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| name | varchar(160) | yes | none | Name |
| version | varchar(40) | yes | v1 | Version |
| hash | varchar(128) | yes | none | Content hash |
| applicable_agents | text[] | yes | {} | Applicable agents |
| content | text | yes | none | Skill markdown |
| quality_gates_json | jsonb | yes | [] | Quality gates |
| forbidden_actions_json | jsonb | yes | [] | Forbidden actions |
| tool_permissions_json | jsonb | yes | [] | Tool permissions |
| status | SkillStatus | yes | active | Status |

Unique constraint: name + version.

## 30. ToolDefinition

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | no | null | Null means global built-in tool |
| name | varchar(120) | yes | none | Unique tool name |
| description | text | no | null | Description |
| tool_type | varchar(80) | yes | test_runner | test_runner, playwright, git, patch, report, artifact, mcp_proxy |
| input_schema_json | jsonb | yes | {} | Tool input schema |
| output_schema_json | jsonb | yes | {} | Tool output schema |
| risk_level | RiskLevel | yes | medium | Default risk |
| approval_required | bool | yes | false | Whether approval is required |
| timeout_seconds | int | yes | 600 | Default timeout |
| command_allowlist_json | jsonb | yes | [] | Allowed command templates |
| allowed_working_directories_json | jsonb | yes | [] | Directory allowlist |
| forbidden_shell_operators_json | jsonb | yes | [";", "&&", "||", "|", ">", ">>", "<", "$(", "`"] | Operators rejected in command strings |
| max_stdout_bytes | int | yes | 1048576 | Captured stdout limit |
| max_stderr_bytes | int | yes | 1048576 | Captured stderr limit |
| artifact_policy_json | jsonb | yes | {} | Artifact capture rules |
| is_mcp_ready | bool | yes | false | Schema can be exposed through future MCP layer |
| mcp_metadata_json | jsonb | yes | {} | MCP-ready metadata, not runtime config |
| status | ToolDefinitionStatus | yes | active | Status |

Unique constraint: project_id + name, treating null project_id as built-in scope.

MCP-ready ToolDefinition rules:

- `is_mcp_ready=true` means the tool has stable name, description,
  input/output schema, risk, approval, timeout, allowlist, and artifact policy
  metadata suitable for future MCP exposure.
- V1 execution still goes through ToolInvocation and internal Tool Adapter
  allowlist rules.
- `mcp_metadata_json` may store `schema_version`, `capability_name`,
  `safe_description`, and `exposure_notes`.
- `mcp_metadata_json` must not store MCP server URLs, tokens, OAuth state, remote
  transport settings, or plugin marketplace references.
- `tool_type=mcp_proxy` is schema intent only in V1 and must not trigger an MCP
  runtime dependency.

Newman ToolDefinition rules:

- Built-in Newman execution uses a ToolDefinition such as
  `newman_collection_run`.
- `tool_type` remains `test_runner`.
- `command_allowlist_json` must constrain commands to backend-approved Newman
  templates, for example `npx newman run <collection> --reporters json,junit`.
- `allowed_working_directories_json` must keep execution under the repository
  path or Chtest-managed runtime workspace.
- `artifact_policy_json` must name stdout, stderr, `newman_json`, optional
  `junit`, runtime manifest, dependency snapshot, environment snapshot, and
  parsed result artifacts.
- Forbidden shell operators remain rejected. A Newman command cannot use shell
  chaining, redirection, command substitution, or pipes.

## 31. KnowledgeAdapterConfig

KnowledgeAdapterConfig records the V1 empty KnowledgeAdapter surface. It is
configuration state only; it does not perform retrieval.

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| adapter_name | varchar(120) | yes | default | Name inside project |
| status | KnowledgeAdapterStatus | yes | not_configured | Empty adapter state |
| provider_type | varchar(80) | yes | none | none, stub, deterministic_local |
| config_json | jsonb | yes | {} | Non-secret display/config state |
| safety_policy_json | jsonb | yes | {} | Prompt eligibility and safety notes |
| last_checked_at | timestamptz | no | null | Last local validation time |
| notes | text | no | null | Human-readable notes |

Unique constraint: project_id + adapter_name.

V1 KnowledgeAdapter rules:

- KnowledgeAdapterConfig is optional; missing config means `not_configured`.
- `provider_type` must be `none` or `stub` in V1.
- `config_json` must not contain API keys, provider credentials, vector database
  settings, embedding model settings, remote URLs, OAuth state, or MCP transport
  details.
- KnowledgeAdapterConfig must not create vector indexes, chunk documents, embed
  content, rank search results, or call external providers.
- AI task responses must keep `used_knowledge=false` unless a future version
  implements a real KnowledgeAdapter runtime.

V2 deterministic KnowledgeAdapter rules:

- Slice 19 may set `provider_type=deterministic_local` with
  `status=configured_stub` to enable the deterministic local retrieval stub.
- `config_json` may include non-secret values such as `match_mode`,
  `max_results`, `max_snippet_chars`, `min_score`, and `case_sensitive=false`.
- Retrieval may read only same-project ContextArtifact rows that are safe to
  show and allowed for prompt use.
- Retrieval must return deterministic scores, matched terms, bounded snippets,
  and exact ContextArtifact ids.
- `used_knowledge=true` is allowed only when this local deterministic stub
  contributes retrieved snippets to an AI task.
- Slice 19 still must not create vector indexes, chunking pipelines,
  embeddings, reranking jobs, external provider calls, MCP runtime calls, RBAC,
  tenant, permission, marketplace, cloud sync, release, or remote CI/CD
  behavior.

## 32. ToolInvocation

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| tool_definition_id | uuid | no | null | FK ToolDefinition |
| tool_name | varchar(120) | yes | none | ToolDefinition.name snapshot |
| ai_task_id | uuid | no | null | FK AITask |
| input_json | jsonb | yes | {} | Input |
| status | ToolInvocationStatus | yes | created | Status |
| risk_level | RiskLevel | yes | medium | Risk |
| approval_required | bool | yes | false | Approval required |
| approval_status | varchar(40) | yes | not_required | not_required, pending, approved, rejected |
| working_directory | text | no | null | Canonical working directory snapshot |
| command_snapshot | text | no | null | Executed allowlisted command snapshot |
| exit_code | int | no | null | Exit code |
| output_json | jsonb | yes | {} | Structured output |
| stdout_artifact_id | uuid | no | null | Captured stdout artifact |
| stderr_artifact_id | uuid | no | null | Captured stderr artifact |
| started_at | timestamptz | no | null | Start time |
| finished_at | timestamptz | no | null | Finish time |

## 33. Artifact

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| owner_entity_type | varchar(80) | yes | none | ArtifactOwnerType |
| owner_entity_id | uuid | yes | none | Related entity |
| artifact_type | varchar(80) | yes | json | raw_llm_output, stdout, stderr, junit, coverage, trace, screenshot, patch, report_md, report_html, report_json, automation_draft_code, runtime_manifest, dependency_snapshot, environment_snapshot, context_markdown, context_text, context_json, context_yaml, context_openapi, diff_patch, changed_files, risk_analysis, unit_test_patch, patch_scope_gate, regression_plan, quality_gate, ci_run_metadata, knowledge_retrieval |
| file_path | text | yes | none | Artifact-relative path |
| mime_type | varchar(120) | yes | application/json | MIME |
| size_bytes | bigint | yes | 0 | File size |
| sha256 | varchar(128) | yes | none | Content hash |
| metadata_json | jsonb | yes | {} | Metadata |

V1 ContextArtifact rule:

- ContextArtifact is not a separate table in V1.
- ContextArtifact reuses the Artifact table.
- For project-level context documents, set `owner_entity_type=Project` and `owner_entity_id=project_id`.
- AITask rows that use context must copy the selected ids into `context_artifact_ids`.
- A prompt input artifact must include `context_manifest.json` with the exact context artifact ids, hashes, titles, MIME types, and redaction flags used for that AI task.
- Artifact owner fields must never be null for ContextArtifact.

Deterministic retrieval Artifact rule:

- Slice 19 retrieval evidence uses `artifact_type=knowledge_retrieval`.
- `owner_entity_type=AITask` and `owner_entity_id=ai_task_id`.
- `metadata_json` must include `created_by_component=DeterministicKnowledgeAdapter`,
  `retrieval_mode=deterministic_local`, `query_terms`, `result_count`,
  `used_context_artifact_ids`, and redaction status.

CI import Artifact rule:

- Slice 20 CI metadata import uses `artifact_type=ci_run_metadata`.
- `owner_entity_type=CICDRun` and `owner_entity_id=cicd_run_id`.
- `metadata_json` must include `created_by_component=CICDRunMetadataImport`,
  `source_type=ci_import`, `provider`, `provider_is_inert_label=true`,
  `import_mode`, `changed_file_count`, `artifact_reference_count`,
  `remote_fetch_performed=false`, and `quality_gate_auto_decision=false`.

## 34. AutomationQualityMetric

AutomationQualityMetric stores batch-level AutomationDraft generation, execution, and repair quality. Ratio fields use `0.00-1.00`; UI may render percentages.

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| automation_draft_id | uuid | no | null | Optional FK AutomationDraft |
| prompt_version_id | uuid | yes | none | FK PromptVersion |
| skill_version_id | uuid | yes | none | FK SkillVersion |
| model_provider | varchar(80) | yes | mock | Provider |
| model_name | varchar(120) | yes | mock-model | Model |
| draft_generated_count | int | yes | 0 | Generated draft count |
| schema_valid_count | int | yes | 0 | Draft outputs passing schema |
| approved_count | int | yes | 0 | Approved drafts |
| rejected_count | int | yes | 0 | Rejected drafts |
| manual_edit_count | int | yes | 0 | Drafts edited before approval |
| first_run_pass_count | int | yes | 0 | Approved drafts passing first execution |
| first_run_fail_count | int | yes | 0 | Approved drafts failing first execution |
| repair_attempt_count | int | yes | 0 | Repair attempts |
| repair_success_count | int | yes | 0 | Repairs that pass a follow-up TestRun |
| evidence_complete_count | int | yes | 0 | Failed runs with complete required evidence |
| schema_valid_rate | numeric(3,2) | yes | 0.00 | schema_valid_count / draft_generated_count |
| approval_rate | numeric(3,2) | yes | 0.00 | approved_count / draft_generated_count |
| manual_edit_rate | numeric(3,2) | yes | 0.00 | manual_edit_count / draft_generated_count |
| first_run_pass_rate | numeric(3,2) | yes | 0.00 | first_run_pass_count / approved_count |
| repair_success_rate | numeric(3,2) | yes | 0.00 | repair_success_count / repair_attempt_count |
| evidence_complete_rate | numeric(3,2) | yes | 0.00 | evidence_complete_count / first_run_fail_count |

## 34. Relationship Summary

```text
Workspace -> Project
Project -> Module / Repository / Environment / TestCommand
Project -> Artifact (ContextArtifact)
Project -> KnowledgeAdapterConfig
Project -> Requirement -> RequirementReview -> RiskItem
Requirement -> CaseGenerationTask -> GeneratedCaseCandidate -> TestCase
TestCase/Requirement -> AutomationDraft -> TestRun -> TestResult -> Report
TestRun/TestResult -> FailureAnalysis -> AutomationRepairTask -> Report
Repository -> CICDRun -> CICDChangedFile -> UnitTestPatch -> TestRun -> QualityGateDecision -> Report
Project -> ReviewHistory -> GeneratedCaseCandidate/TestCase/AutomationDraft/UnitTestPatch/CICDRun/QualityGateDecision
AITask -> LLMCallLog
AITask -> Artifact / ContextArtifact references
AutomationDraft -> AutomationRepairTask -> AutomationQualityMetric
ToolDefinition -> ToolInvocation -> Artifact
Report -> Artifact
PromptVersion + SkillVersion -> AITask
```
