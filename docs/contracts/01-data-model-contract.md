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
| ArtifactOwnerType | Project, AITask, Requirement, RequirementReview, CaseGenerationTask, GeneratedCaseCandidate, TestKnowledgeCard, AutomationDraft, TestRun, Report, CICDRun, ToolInvocation |
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
| command_type | varchar(40) | yes | pytest | pytest, npm, playwright, newman, jmeter |
| timeout_seconds | int | yes | 600 | Max runtime |
| parse_junit | bool | yes | true | Parse JUnit output |
| parse_coverage | bool | yes | false | Parse coverage output |
| status | EntityStatus | yes | active | Status |

JMeter TestCommand rules:

- `command_type=jmeter` is used only for approved local JMeter non-GUI
  execution in Slice 22.
- The command must pass the JMeter ToolDefinition allowlist and must not carry
  arbitrary shell text from the client.
- JMX plan paths and JTL output paths must stay under the repository path or a
  Chtest-managed runtime workspace.

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
| source_knowledge_evidence_ids | text[] | yes | {} | KnowledgeEvidence ids cited by this candidate |
| knowledge_evidence_refs_json | jsonb | yes | [] | Display refs: evidence id, card id, snippet, score |
| covered_risk_ids | uuid[] | yes | {} | RiskItem ids intentionally covered |
| generation_reason | text | no | null | Human-readable reason beyond raw model text |
| automation_readiness | varchar(40) | yes | unknown | unknown, not_suitable, suitable_for_pytest, suitable_for_playwright, suitable_for_newman, suitable_for_jmeter |
| quality_score | int | no | null | 0-100 agent review score when available |
| review_findings_json | jsonb | yes | [] | CaseReviewAgent or human review findings |
| coverage_gap_notes | text | no | null | Known uncovered requirement/risk notes |
| duplicate_of_case_id | uuid | no | null | Potential duplicate case |
| status | CandidateStatus | yes | generated | Candidate status |
| review_comment | text | no | null | Human review comment |

Slice 30 generated-case evidence rules:

- `source_knowledge_evidence_ids` references normalized KnowledgeEvidence items
  produced from same-project TestKnowledgeCards, ContextArtifacts, reviewed
  cases, review findings, execution evidence, failure analysis, or reports.
- `knowledge_evidence_refs_json` is a display cache only. It must not replace
  persisted TestKnowledgeCard or Artifact evidence.
- `generation_reason` must explain why the case exists in testing terms, not
  merely repeat model prose.
- `quality_score` is review evidence only. It must not auto-approve a
  candidate or create a TestCase.
- `review_findings_json` may include missing requirement coverage, weak
  expected results, duplicate risk, hallucination risk, or automation
  readiness concerns.
- Missing evidence must keep the candidate reviewable as `generated` or
  `under_review`; it must not silently become approved.

Slice 31 persistence rules:

- When validated CaseGenerationAgent output contains these fields, the
  generated_case_candidates row must persist them with the field names in this
  table.
- When AI output omits these fields, persistence must use the defaults in this
  contract and remain backward-compatible with older mock/provider outputs.
- `knowledge_evidence_refs_json` and `review_findings_json` must stay bounded
  JSON display data. They must not store raw provider payloads, unbounded
  document text, secrets, credentials, cookies, or tokens.
- Persisting these fields is not evidence approval. It must not create
  TestCase, TestRun, Report, retrieval job, vector index, embedding job, graph
  job, provider call, or Artifact mutation side effects.

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
| runner_mode | varchar(40) | yes | local_subprocess | local_subprocess, playwright_local, newman_local, jmeter_local, docker_runner |
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

JMeter TestRun rules:

- `runner_mode=jmeter_local` is used for approved local JMeter non-GUI
  execution.
- JMeter TestRuns must reference `test_command_id`; Slice 22 does not execute
  JMeter from AutomationDraft.
- `parsed_result_json` must include aggregate sampler/assertion counts:
  `total`, `passed`, `failed`, `skipped`, `error`, `sampler_count`,
  `assertion_count`, `duration_ms`, and `average_latency_ms` when available.
- `failed` means JMeter completed and one or more samplers/assertions failed.
- `error` means JMeter could not run, timed out, or produced unparseable JTL
  output.
- Local fixture tests must not require a real JMeter installation; they may use
  deterministic JTL files or a fake executable.

Slice 29 execution run manifest rules:

- Execution run manifest is read-only presentation derived from existing
  TestRun fields and Artifact metadata. It does not add a new table.
- Manifest identity fields are `id`, `name`, `status`, `automation_draft_id`,
  `test_command_id`, and `tool_invocation_id`.
- Manifest command fields are `command`, `working_directory`, `runner_mode`,
  and `run_workspace`.
- Manifest safety fields are `repository_readonly` and `network_enabled`.
  `network_enabled=false` is the default local safety policy;
  `network_enabled=true` must remain visible and must not be hidden behind a
  passed status.
- Manifest snapshot fields are `runtime_artifact_ids`,
  `dependency_snapshot_artifact_id`, and `environment_snapshot_artifact_id`.
  Missing snapshot ids remain meaningful unavailable evidence and must not be
  treated as passing evidence.
- Manifest result fields are `exit_code`, `duration_ms`, and
  `parsed_result_json`.
- Manifest artifact rows are existing Artifact rows owned by the TestRun or
  cited by these snapshot fields. The manifest does not create, rewrite, or
  delete Artifact rows.
- Execution run manifest must not mutate TestRun, TestResult, Artifact, Report,
  FailureAnalysis, QualityGateDecision, AutomationDraft, ToolDefinition,
  ToolInvocation, CI metadata, or review history.

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
- ToolDefinition safety requires `input_schema_json` and `output_schema_json`
  to be strict JSON schemas with bounded object shapes. Unknown free-form
  command strings, arbitrary shell fragments, transport handles, credentials,
  and provider-specific payloads are not valid schema fields.
- `risk_level`, `approval_required`, `timeout_seconds`, and
  `artifact_policy_json` are part of the safety contract. Medium/high risk
  tools must either require approval or be explicitly documented as safe with
  non-mutating behavior, bounded artifacts, and no external side effects.
- `artifact_policy_json` must name expected artifact types, size limits,
  redaction expectations, and whether stdout/stderr/raw output are safe to
  persist. It must not authorize artifact upload, mutation, deletion, signed
  URLs, cloud storage, or broad artifact browsing.
- `mcp_metadata_json.provider_state` may be used as display metadata with
  values such as `disabled`, `configured`, or `unhealthy`, but it is not a
  runtime transport state and must not start or stop an MCP server.
- V1 execution still goes through ToolInvocation and internal Tool Adapter
  allowlist rules.
- `mcp_metadata_json` may store `schema_version`, `capability_name`,
  `safe_description`, `exposure_notes`, `provider_state`, and
  `last_health_check_status`.
- `mcp_metadata_json` must not store MCP server URLs, tokens, OAuth state, remote
  transport settings, or plugin marketplace references.
- `tool_type=mcp_proxy` is schema intent only in V1 and must not trigger an MCP
  runtime dependency.
- ToolDefinition safety must not bypass GeneratedCaseCandidate review,
  AutomationDraft approval, ToolInvocation approval, Artifact persistence,
  Report evidence requirements, PromptVersion/SkillVersion traceability, or
  human review gates.

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

JMeter ToolDefinition rules:

- Built-in JMeter execution uses a ToolDefinition such as
  `jmeter_non_gui_run`.
- `tool_type` remains `test_runner`.
- `command_allowlist_json` must constrain commands to backend-approved JMeter
  non-GUI templates equivalent to `jmeter -n -t <plan.jmx> -l <result.jtl>`.
- `allowed_working_directories_json` must keep execution under the repository
  path or Chtest-managed runtime workspace.
- `artifact_policy_json` must name stdout, stderr, `jmeter_jtl`, runtime
  manifest, dependency snapshot, environment snapshot, and parsed result
  artifacts.
- Forbidden shell operators remain rejected. A JMeter command cannot use shell
  chaining, redirection, command substitution, pipes, remote agents, or cloud
  load testing controls.

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

KnowledgeAdapter safety rules:

- `status` remains the persisted lifecycle state. `provider_state` may appear
  only inside `config_json` or `safety_policy_json` as display/health metadata
  with values such as `disabled`, `configured`, or `unhealthy`.
- `provider_state=disabled` and `status=disabled` force `used_knowledge=false`
  and require local/no-knowledge fallback unless the caller explicitly blocks
  on knowledge evidence.
- `provider_state=unhealthy` means future provider health checks failed. Core
  requirement review, case generation, and human review workflows must degrade
  to local/no-knowledge behavior and record fallback evidence instead of
  failing the product workflow by default.
- Future provider outputs must normalize into Chtest `KnowledgeEvidence` and
  Artifact metadata before prompts, generated cases, or reviews cite them.
  Provider-specific schemas must not be persisted as business truth.
- `config_json` and `safety_policy_json` must not contain credentials, tokens,
  OAuth state, API keys, provider SDK settings, remote URLs, MCP transport
  settings, vector database settings, embedding model settings, reranker
  settings, or graph runtime settings.
- KnowledgeAdapter safety must not create TestKnowledgeCard rows, mutate
  Artifact rows, approve GeneratedCaseCandidate rows, promote TestCase rows,
  execute ToolInvocation rows, generate Reports, or update CI/CD state.

## 31.1 TestKnowledgeCard

TestKnowledgeCard records structured testing knowledge that can later support
case generation and review. It is a local evidence contract, not a generic chat
knowledge chunk and not a provider-owned schema.

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| module_id | uuid | no | null | Optional FK Module |
| title | varchar(255) | yes | none | Human-readable card title |
| knowledge_type | varchar(80) | yes | requirement_point | requirement_point, business_rule, api_contract, boundary_condition, exception_scenario, risk_point, bug_pattern, existing_test_case_pattern, anti_pattern, test_strategy_note |
| summary | text | yes | none | Concise testing knowledge |
| body | text | no | null | Optional normalized detail |
| source_type | varchar(80) | yes | context_artifact | context_artifact, requirement, reviewed_case, rejected_case, execution, failure_analysis, report, manual |
| source_artifact_id | uuid | no | null | Primary source Artifact/ContextArtifact id |
| source_artifact_ids | uuid[] | yes | {} | Additional same-project source Artifact ids |
| source_document_version | varchar(120) | no | null | Version/hash label when known |
| source_section | varchar(255) | no | null | Heading, path, endpoint, or section label |
| source_quote_or_hash | text | no | null | Short safe quote or hash pointer |
| related_requirement_ids | uuid[] | yes | {} | Requirement ids linked to the card |
| related_risk_ids | uuid[] | yes | {} | RiskItem ids linked to the card |
| related_test_case_ids | uuid[] | yes | {} | Reviewed TestCase ids linked to the card |
| tags | text[] | yes | {} | Search/filter tags |
| test_type | TestType | no | null | Suggested test type |
| risk_level | RiskLevel | no | null | Risk severity when applicable |
| module_key | varchar(160) | no | null | Optional module/API/business key |
| api_endpoint | varchar(255) | no | null | Optional API endpoint |
| risk_type | varchar(80) | no | null | business, data, environment, regression, technical |
| case_type_hint | varchar(80) | no | null | boundary, exception, regression, security, happy_path |
| applicability | varchar(80) | yes | project | project, module, requirement, api, regression |
| confidence | int | yes | 0 | 0-100 extraction confidence |
| safe_to_show | bool | yes | false | Server-computed display safety |
| redaction_applied | bool | yes | false | Whether content was redacted |
| allowed_for_prompt | bool | yes | false | Prompt eligibility |
| redaction_report_artifact_id | uuid | no | null | Artifact with redaction details |
| evidence_artifact_ids | uuid[] | yes | {} | Same-project Artifact evidence ids |
| last_verified_at | timestamptz | no | null | Last human/system verification time |
| status | EntityStatus | yes | active | Status |

TestKnowledgeCard rules:

- Source artifacts must belong to the same project.
- Large or sensitive source content stays in Artifact files. The card stores a
  normalized summary and safe references.
- `safe_to_show` and `allowed_for_prompt` are server-side decisions and must
  not rely only on client input.
- Cards may be manually curated or extracted later by a KnowledgeIngestionAgent,
  but Slice 30 does not implement extraction.
- Card creation or status updates must not trigger retrieval, indexing,
  embeddings, reranking, graph extraction, external provider calls, MCP runtime
  calls, or generated-case promotion.

TestKnowledgeCard handoff candidate rules:

- A TestKnowledgeCard handoff starts from an `approved_by_human`
  KnowledgeFeedbackDraft and its `handoff_payload_json`. The handoff payload is
  a candidate contract only; it is not CRUD and must not create, approve,
  archive, delete, or mutate TestKnowledgeCard rows.
- The handoff payload must carry `source_feedback_id`, `review_history_id`,
  `review_artifact_id`, `source_entity_type`, `source_entity_id`,
  `source_artifact_ids`, `source_quote_or_hash`, `source_span`,
  `draft_knowledge_type`, and mapped `knowledge_type` before any future card
  workflow can use it.
- Candidate card fields may include title, summary, body, source_type,
  source_section, related_requirement_ids, related_risk_ids,
  related_test_case_ids, tags, confidence, `safe_to_show`,
  `redaction_applied`, `evidence_artifact_ids`, and `allowed_for_prompt=false`.
- `allowed_for_prompt=false` is mandatory for handoff candidates. A later
  human review must approve the TestKnowledgeCard itself before
  `allowed_for_prompt=true` is possible.
- `duplicate_knowledge_card_ids`, `merge_hint`, and `review_required=true`
  preserve duplicate/merge uncertainty. They must not silently replace,
  archive, or merge existing TestKnowledgeCard rows.
- Unsupported claims remain attached to the handoff and must not become card
  body facts, prompt context, or positive knowledge unless a human reviewer
  supplies source evidence in a later scoped workflow.
- Unsafe, missing, cross-project, or untraceable source evidence must reject
  the handoff or request revision. It must not fabricate a source Artifact,
  source hash, ReviewHistory, KnowledgeEvidence, or card id.

TestKnowledgeCard Candidate Review rules:

- TestKnowledgeCard Candidate Review starts from a TestKnowledgeCard handoff
  candidate, `test_knowledge_card_handoff.json`, and a human reviewer action.
  It is a candidate review contract only; it must not create, approve, archive,
  delete, merge, relabel, or mutate TestKnowledgeCard rows.
- Candidate review actions are `approve_candidate_for_creation`,
  `reject_candidate`, `request_candidate_revision`, `flag_duplicate`,
  `request_merge_review`, and `defer_prompt_eligibility`.
- Candidate review input must preserve `source_feedback_id`,
  `source_handoff_artifact_id`, `candidate_card_json`, `source_artifact_ids`,
  `source_quote_or_hash`, `source_span`, `duplicate_knowledge_card_ids`,
  `merge_hint`, unsupported claims, and any prior `review_history_id` or
  `review_artifact_id`.
- Candidate review output may include `candidate_review_action`,
  `candidate_review_decision`, reviewer label/comment, `review_history_id`,
  `candidate_review_artifact_id`, `evidence_artifact_ids`,
  `duplicate_review_required`, `merge_review_required`,
  `prompt_eligibility_decision=deferred`, failure code, and
  `allowed_for_prompt=false`.
- `approve_candidate_for_creation` means the candidate may be routed to a
  future explicitly scoped card-creation workflow. It is not TestKnowledgeCard
  CRUD and must not produce a `test_knowledge_card_id` in this contract.
- `flag_duplicate` and `request_merge_review` are review-routing decisions.
  They must not merge, archive, replace, delete, relabel, or create
  TestKnowledgeCard rows.
- `defer_prompt_eligibility` is the default prompt eligibility decision for
  reviewed candidates. Candidate review must not set `allowed_for_prompt=true`.
- Rejected or revision-requested candidates remain auditable with source
  evidence and unsupported claims. They must not become positive knowledge,
  card body facts, or prompt context.

Reviewed TestKnowledgeCard Creation rules:

- Reviewed TestKnowledgeCard Creation starts from an approved candidate review:
  `candidate_approved_for_future_creation`, a candidate review artifact,
  `test_knowledge_card_handoff.json`, `candidate_card_json`, and ReviewHistory
  evidence. It is a reviewed creation contract only; it must not add broad
  CRUD, list, update, delete, merge, archive, or relabel behavior.
- The future scoped action is `create_reviewed_test_knowledge_card`. It must
  require same-project source artifacts, source quote/hash, source span,
  candidate review evidence, duplicate/merge precondition results, safe-to-show
  evidence, and visible unsupported claims.
- The approved candidate must map into TestKnowledgeCard fields: project_id,
  optional module_id, title, knowledge_type, summary, body, source_type,
  source_artifact_id, source_artifact_ids, source_document_version,
  source_section, source_quote_or_hash, related requirement/risk/test case ids,
  tags, test_type, risk_level, module_key, api_endpoint, applicability,
  confidence, `safe_to_show`, `redaction_applied`, redaction report artifact
  id, `evidence_artifact_ids`, last_verified_at, and status.
- Reviewed creation defaults to `allowed_for_prompt=false`. Creation approval
  is not prompt eligibility, and prompt eligibility must remain a later
  explicitly scoped workflow.
- Duplicate and merge preconditions must be resolved before creation. Unresolved
  `duplicate_knowledge_card_ids`, stale `merge_hint`, or pending merge review
  must block creation instead of merging, archiving, replacing, deleting,
  relabeling, or creating conflicting TestKnowledgeCard rows.
- Reviewed creation must produce or reference a source manifest and creation
  artifact in a future scoped implementation. The source manifest records
  source artifacts, source hashes, source spans, ReviewHistory ids, candidate
  review artifact id, and duplicate/merge precondition result.
- Stale, rejected, revision-requested, cross-project, unsafe, unbounded, or
  unsupported source evidence must reject creation with a failure code. It must
  not fabricate fallback cards, source artifacts, ReviewHistory, or
  KnowledgeEvidence.

TestKnowledgeCard Prompt Eligibility rules:

- TestKnowledgeCard Prompt Eligibility starts from an existing reviewed
  TestKnowledgeCard record and a human reviewer action. It is not card
  creation, broad CRUD, retrieval runtime, vector indexing, or prompt assembly.
- Prompt eligibility actions are `mark_card_prompt_eligible`,
  `deny_card_prompt_eligibility`, `request_prompt_eligibility_revision`, and
  `revoke_card_prompt_eligibility`.
- Eligibility input must preserve TestKnowledgeCard id, creation artifact id,
  source manifest, same-project source artifact ids, source quote/hash,
  source span, ReviewHistory ids, redaction report artifact id, `safe_to_show`
  status, unsupported claims, and prior prompt eligibility decision when
  present.
- `mark_card_prompt_eligible` requires `safe_to_show=true`, reviewed redaction
  status, reviewed source citations, a non-empty prompt eligibility reason,
  ReviewHistory, and prompt eligibility artifact evidence.
- `allowed_for_prompt=true` may be set only by a successful human review
  action. It must not be inferred from card creation, model confidence, schema
  validity, source presence, duplicate/merge resolution, or `safe_to_show=true`
  alone.
- `deny_card_prompt_eligibility` and
  `request_prompt_eligibility_revision` keep `allowed_for_prompt=false` and
  preserve reviewer reason, failure code, source evidence, and unsupported
  claims.
- `revoke_card_prompt_eligibility` changes prompt eligibility evidence for the
  card and must record revocation reason, reviewer label, ReviewHistory, and a
  prompt eligibility artifact. It must not delete or mutate source artifacts.
- Unsafe, stale, cross-project, missing, unbounded, unsupported, or redaction
  failed evidence must deny eligibility, request revision, or revoke existing
  eligibility. Denied or revoked cards must not enter prompt context.

TestKnowledgeCard Retrieval Boundary rules:

- TestKnowledgeCard Retrieval Boundary starts from a future prompt-context
  selection request and existing reviewed TestKnowledgeCard records. It is
  read-only and is not prompt runtime retrieval, prompt assembly, card
  creation, broad CRUD, vector indexing, embedding, reranking, graph runtime,
  MCP runtime, or provider behavior.
- The contract-only selection action is `select_prompt_eligible_cards`.
  It may evaluate card evidence for future prompt context, but it must not
  mutate TestKnowledgeCard rows, source Artifacts, prompt eligibility
  artifacts, ReviewHistory, KnowledgeEvidence, or historical evidence.
- Selection input must preserve project id, future prompt/request id when
  available, candidate TestKnowledgeCard ids, prompt eligibility artifact ids,
  creation artifact ids, source manifest, same-project source artifact ids,
  source quote/hash, source span, ReviewHistory ids, redaction report artifact
  id, `safe_to_show` status, `prompt_eligible` state, `allowed_for_prompt`
  status, unsupported claims, and failure code when present.
- A card is selectable only when `allowed_for_prompt=true`, the current prompt
  eligibility state is `prompt_eligible`, `safe_to_show=true`, reviewed
  redaction status, same-project source evidence, source manifest, reviewed
  source citations, ReviewHistory, and prompt eligibility artifact evidence
  are all present. `allowed_for_prompt=true` is necessary but not sufficient
  for prompt-context selection.
- `allowed_for_prompt=false`, `prompt_eligibility_denied`,
  `prompt_eligibility_revision_requested`, `prompt_eligibility_revoked`,
  stale evidence, cross-project evidence, unsafe evidence, missing source
  evidence, unbounded source evidence, unsupported claims, redaction failure,
  source manifest mismatch, missing ReviewHistory, or missing prompt
  eligibility artifact evidence must exclude the card.
- Excluded cards must record an `excluded_card_reason` or failure code in
  future retrieval evidence. Exclusion must not revoke prompt eligibility,
  delete cards, mutate artifacts, rewrite source evidence, or rewrite
  ReviewHistory.
- Retrieval boundary outputs are evidence only: selected TestKnowledgeCard ids,
  excluded TestKnowledgeCard ids, `excluded_card_reason`, source evidence ids,
  source manifest artifact id, source quote/hash, ReviewHistory ids,
  safe_to_show/redaction status, selection reason, and bounded snippet or
  source hash. They must not include raw large source text or provider payloads.

TestKnowledgeCard Prompt Context Evidence rules:

- TestKnowledgeCard Prompt Context Evidence starts from a retrieval boundary
  artifact and selected TestKnowledgeCard ids. It is contract-only evidence for
  future prompt input and is not prompt assembly implementation, prompt runtime
  execution, provider behavior, retrieval ranking, card creation, broad CRUD,
  vector indexing, embedding, reranking, graph runtime, or MCP runtime.
- The contract-only evidence action is `build_prompt_context_evidence`. It may
  describe safe context entries for a future prompt, but it must not write a
  runtime `prompt_input.json`, call providers, run AITasks, mutate
  TestKnowledgeCard rows, mutate retrieval boundary artifacts, mutate prompt
  eligibility artifacts, mutate ReviewHistory, or mutate historical evidence.
- Prompt context evidence input must preserve prompt request id or AITask id
  when available, PromptVersion id, SkillVersion id, retrieval boundary
  artifact id, selected TestKnowledgeCard ids, source evidence ids, source
  manifest artifact ids, prompt eligibility artifact ids, ReviewHistory ids,
  `safe_to_show=true`, reviewed redaction status, unsupported claims, and
  prior exclusion summaries.
- A prompt context entry may include TestKnowledgeCard id, knowledge_type,
  title, summary, a safe bounded snippet, source hash or source quote/hash
  pointer, source artifact ids, source section, retrieval boundary artifact id,
  prompt eligibility artifact id, ReviewHistory id, selection reason, source
  trace label, and omission reason when a selected card cannot be included.
- Card text can enter prompt context only when `safe_to_show=true`, reviewed
  redaction, same-project source evidence, retrieval boundary evidence, and
  prompt eligibility artifact evidence are present. A source hash or source
  quote/hash pointer must replace text when snippet bounds, redaction, or
  display safety cannot be proven.
- Prompt context evidence outputs must include prompt context evidence artifact
  id, selected context entries, omitted card summaries, omission reason, source
  manifest ids, source hashes, PromptVersion/SkillVersion trace, context
  manifest links, and failure code for stale, unsafe, cross-project, revoked,
  unsupported, missing, unbounded, redaction-failed, or evidence-mismatched
  input.
- Prompt context evidence must not contain raw large source text, unsafe
  provider payloads, vector store payloads, embedding vectors, reranker traces,
  graph runtime payloads, secrets, credentials, tokens, OAuth material, or
  executable prompt assembly payloads.

TestKnowledgeCard Prompt Context Consumption rules:

- TestKnowledgeCard Prompt Context Consumption starts from an existing prompt
  context evidence artifact and a future agent input that explicitly references
  it. It is contract-only citation evidence for future AI outputs and is not
  prompt assembly implementation, prompt runtime execution, provider behavior,
  retrieval ranking, card creation, broad CRUD, vector indexing, embedding,
  reranking, graph runtime, or MCP runtime.
- The contract-only consumption action is `consume_prompt_context_evidence`.
  It may describe which prompt context entries a future agent consumed and how
  an output cites them, but it must not write a runtime `prompt_input.json`,
  call providers, run AITasks, mutate TestKnowledgeCard rows, mutate prompt
  context evidence artifacts, mutate source artifacts, mutate ReviewHistory,
  set `used_knowledge=true` automatically, or mutate historical evidence.
- Prompt context consumption input must preserve prompt request id or AITask id
  when available, consuming agent step name, intended output artifact type,
  PromptVersion id/name/version, SkillVersion id/name/version, prompt context
  evidence artifact id, context manifest artifact id, selected
  TestKnowledgeCard ids, consumed context entry ids, source manifest ids,
  source artifact ids, source sections, source hashes, retrieval boundary
  artifact id, prompt eligibility artifact ids, ReviewHistory ids, omission
  summaries, and unsupported claims when present.
- `used_knowledge=false` is required when no valid prompt context evidence is
  consumed. `used_knowledge=true` is allowed only when at least one consumed
  citation points back to a valid prompt context evidence entry, source hash or
  source quote/hash pointer, same-project source artifact, PromptVersion,
  SkillVersion, and ReviewHistory trace.
- Output citations may include output artifact id, agent step name, cited
  TestKnowledgeCard id, cited prompt context evidence artifact id, cited
  context entry id, cited source hash or source quote/hash pointer, source
  artifact id, source section, PromptVersion/SkillVersion trace,
  ReviewHistory id, citation status, and unsupported claim marker when output
  text cannot be traced to consumed evidence.
- Prompt context consumption outputs must include a consumption artifact id when
  a later scoped workflow defines one, `used_knowledge` decision, consumed
  knowledge citations, skipped evidence summaries and skip reasons, source
  manifest ids, source hashes, PromptVersion/SkillVersion trace, context
  manifest references, and failure code for missing, stale, unsafe,
  cross-project, revoked, unsupported, unbounded, citation-mismatched,
  context-mismatched, prompt-version-mismatched, skill-version-mismatched,
  redaction-failed, or evidence-mismatched input.
- Prompt context consumption must not cite raw large source text, unsafe
  provider payloads, vector store payloads, embedding vectors, reranker traces,
  graph runtime payloads, secrets, credentials, tokens, OAuth material, or
  executable prompt assembly payloads.

TestKnowledgeCard Prompt Context Audit Summary rules:

- TestKnowledgeCard Prompt Context Audit Summary starts from existing prompt
  context consumption evidence. It is a read-only summary contract for future
  review/report surfaces and is not a frontend page, report generation behavior
  change, prompt assembly implementation, prompt runtime execution, provider
  behavior, retrieval ranking, card creation, broad CRUD, vector indexing,
  embedding, reranking, graph runtime, or MCP runtime.
- The contract-only summary action is `summarize_prompt_context_consumption`.
  It may describe `prompt_context_audit_summary` evidence, usage status,
  cited entries, skipped entries, unsupported claim summaries, and failure
  reasons, but it must not write a runtime `prompt_input.json`, call
  providers, run AITasks, mutate TestKnowledgeCard rows, mutate prompt context
  consumption artifacts, mutate prompt context evidence artifacts, mutate
  source artifacts, rewrite `used_knowledge`, invent citations, or mutate
  historical evidence.
- Audit summary input must preserve prompt request id or AITask id when
  available, consuming agent step name, intended output artifact type, prompt
  context consumption artifact id, prompt context evidence artifact id, context
  manifest artifact id, `used_knowledge` decision, output citation ids, cited
  TestKnowledgeCard ids, cited context entry ids, cited source hashes or source
  quote/hash pointers, skipped evidence ids and skip reasons, unsupported
  claims, PromptVersion id/name/version, SkillVersion id/name/version,
  ReviewHistory ids, and failure code when applicable.
- Audit summary outputs may include audit summary id or artifact id, knowledge
  usage status, cited evidence summaries, skipped evidence summaries,
  unsupported claim summaries, source hash/context entry references,
  PromptVersion/SkillVersion trace, context manifest links, ReviewHistory
  links, review flags, and failure reasons.
- Audit summaries must preserve `used_knowledge` and citation evidence as
  recorded by prompt context consumption. They must not promote unsupported
  claims, turn skipped evidence into cited evidence, or mark knowledge used
  when prompt context consumption kept `used_knowledge=false`.
- Missing, stale, unsafe, cross-project, revoked, unsupported, unbounded,
  citation-mismatched, context-mismatched, prompt-version-mismatched,
  skill-version-mismatched, redaction-failed, or evidence-mismatched input must
  produce failure flags or skipped summary rows without mutating historical
  evidence.
- Prompt context audit summaries must not copy raw large source text, unsafe
  provider payloads, vector store payloads, embedding vectors, reranker traces,
  graph runtime payloads, secrets, credentials, tokens, OAuth material, or
  executable prompt assembly payloads.

TestKnowledgeCard Prompt Context Audit Review Decision rules:

- TestKnowledgeCard Prompt Context Audit Review Decision starts from an
  existing prompt context audit summary. It is a human review decision contract
  for future review workflows and is not a frontend page, report generation
  behavior change, prompt assembly implementation, prompt runtime execution,
  provider behavior, retrieval ranking, card creation, broad CRUD, vector
  indexing, embedding, reranking, graph runtime, or MCP runtime.
- The contract-only review decision action is
  `review_prompt_context_audit_summary`. It may record whether a reviewer
  accepted, questioned, or rejected the audit summary evidence, but it must not
  write a runtime `prompt_input.json`, call providers, run AITasks, mutate
  TestKnowledgeCard rows, mutate audit summary artifacts, mutate prompt context
  consumption artifacts, mutate prompt context evidence artifacts, mutate
  source artifacts, rewrite `used_knowledge`, invent citations, or mutate
  historical evidence.
- Review decision input must preserve prompt request id or AITask id when
  available, audit summary artifact id, prompt context consumption artifact
  id, prompt context evidence artifact id, context manifest artifact id,
  `used_knowledge` decision, usage status, output citation ids, cited
  TestKnowledgeCard ids, cited context entry ids, cited source hash or source
  quote/hash pointers, skipped evidence ids and skip reasons, unsupported
  claims, review flags, failure reasons, PromptVersion id/name/version,
  SkillVersion id/name/version, and prior ReviewHistory ids when present.
- Review decision outputs may include review decision id or artifact id,
  reviewer label or local reviewer id, review action, reviewer comment,
  accepted citation ids, questioned citation ids, rejected citation ids,
  follow-up flags, requested clarification fields, ReviewHistory id for the
  decision evidence, source hashes, context manifest references,
  PromptVersion/SkillVersion trace, and failure code when applicable.
- Allowed review actions are `accepted`, `needs_clarification`,
  `rejected_for_missing_evidence`, `rejected_for_unsupported_claim`,
  `rejected_for_citation_mismatch`, `rejected_for_stale_evidence`, and
  `rejected_for_cross_project_evidence`.
- Review decisions are evidence about an audit summary. `accepted` must not
  create prompt eligibility, approve TestKnowledgeCard content, approve
  generated cases, alter `used_knowledge`, or mark skipped evidence as cited.
  `needs_clarification` and rejected decisions must preserve cited evidence,
  skipped evidence, unsupported claims, source hashes, context manifest links,
  PromptVersion/SkillVersion trace, and ReviewHistory links.
- Missing, stale, unsafe, cross-project, revoked, unsupported, unbounded,
  citation-mismatched, context-mismatched, prompt-version-mismatched,
  skill-version-mismatched, redaction-failed, evidence-mismatched, or audit
  summary-mismatched input must produce a failure code and must not append a
  successful ReviewHistory decision.
- Prompt context audit review decisions must not copy raw large source text,
  unsafe provider payloads, vector store payloads, embedding vectors, reranker
  traces, graph runtime payloads, secrets, credentials, tokens, OAuth material,
  executable prompt assembly payloads, frontend-rendered markup, or
  report-rendered payloads.

TestKnowledgeCard Prompt Context Audit Review Summary Export rules:

- TestKnowledgeCard Prompt Context Audit Review Summary Export starts from an
  existing prompt context audit review decision. It is a contract for future
  exportable evidence packages and is not a frontend page, report generation
  behavior change, export/download endpoint, prompt assembly implementation,
  prompt runtime execution, provider behavior, retrieval ranking, card
  creation, broad CRUD, vector indexing, embedding, reranking, graph runtime,
  or MCP runtime.
- The contract-only summary export action is
  `export_prompt_context_audit_review_summary`. It may package review outcome
  summaries, accepted citation groups, questioned citation groups, rejected
  citation groups, unresolved follow-up flags, unsupported claim references,
  and source hash/context manifest references, but it must not write a runtime
  `prompt_input.json`, expose a download endpoint, render a report, call
  providers, run AITasks, mutate TestKnowledgeCard rows, mutate audit review
  decision artifacts, mutate audit summary artifacts, mutate prompt context
  consumption artifacts, mutate prompt context evidence artifacts, mutate
  source artifacts, rewrite `used_knowledge`, invent citations, or mutate
  historical evidence.
- Summary export input must preserve prompt request id or AITask id when
  available, audit review decision artifact id, audit summary artifact id,
  prompt context consumption artifact id, prompt context evidence artifact id,
  context manifest artifact id, `used_knowledge` decision, usage status, review
  action, review outcome summary, accepted citation ids, questioned citation
  ids, rejected citation ids, output citation ids, cited TestKnowledgeCard ids,
  cited context entry ids, cited source hash or source quote/hash pointers,
  skipped evidence ids and skip reasons, unsupported claims, unresolved
  follow-up flags, failure reasons, PromptVersion id/name/version,
  SkillVersion id/name/version, ReviewHistory ids, and review decision
  ReviewHistory id.
- Summary export outputs may include summary export id or artifact id, export
  action, review outcome summary, accepted citation group, questioned citation
  group, rejected citation group, unresolved follow-up flag group, unsupported
  claim references, reviewer comment summary, source manifest ids, source
  hashes, context manifest references, PromptVersion/SkillVersion trace,
  ReviewHistory links, and failure code when applicable.
- Summary exports are evidence packages about review decisions. Accepted
  citation groups must not create prompt eligibility, approve TestKnowledgeCard
  content, approve generated cases, alter `used_knowledge`, or mark skipped
  evidence as cited. Questioned/rejected citation groups and unresolved
  follow-up flags must remain visible.
- Missing, stale, unsafe, cross-project, revoked, unsupported, unbounded,
  citation-mismatched, context-mismatched, prompt-version-mismatched,
  skill-version-mismatched, redaction-failed, evidence-mismatched, audit
  summary-mismatched, or review-decision-mismatched input must produce a
  failure code and must not append a successful summary export.
- Prompt context audit review summary exports must not copy raw large source
  text, unsafe provider payloads, vector store payloads, embedding vectors,
  reranker traces, graph runtime payloads, secrets, credentials, tokens, OAuth
  material, executable prompt assembly payloads, frontend-rendered markup,
  report-rendered payloads, or downloadable provider payloads.

## 31.2 KnowledgeEvidence

KnowledgeEvidence is the normalized citation object used by agents, generated
cases, review findings, and fixtures. It may be stored inside AI task output,
case generation artifacts, generated candidate fields, or future dedicated
tables, but provider-specific payloads must be normalized before Chtest uses
them as evidence.

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| evidence_id | varchar(120) | yes | none | Stable id inside the owning artifact/task |
| project_id | uuid | yes | none | FK Project |
| provider_name | varchar(120) | yes | chtest_local | chtest_local, deterministic_local, future provider label |
| retrieval_mode | varchar(80) | yes | structured_card | structured_card, deterministic_local, future_hybrid |
| source_artifact_id | uuid | no | null | Source Artifact/ContextArtifact id |
| knowledge_card_id | uuid | no | null | TestKnowledgeCard id when available |
| source_section | varchar(255) | no | null | Source section/path |
| snippet | text | yes | none | Bounded safe evidence snippet |
| score | numeric | no | null | Deterministic/provider-normalized score |
| matched_terms | text[] | yes | {} | Terms supporting retrieval/match |
| query_terms | text[] | yes | {} | Query terms used when applicable |
| retrieval_reason | text | no | null | Why this evidence supports the case |
| safe_to_show | bool | yes | false | Display safety |
| allowed_for_prompt | bool | yes | false | Prompt eligibility |
| created_by_component | varchar(120) | yes | TestKnowledgeContract | Producer label |

KnowledgeEvidence rules:

- `snippet` must be bounded, safe to show, and traceable to a same-project
  source Artifact or TestKnowledgeCard.
- Free-floating model text is not valid KnowledgeEvidence unless it is attached
  to persisted input/output Artifact evidence and clearly labeled as model
  analysis, not source truth.
- Provider payloads from future Haystack, LlamaIndex, GraphRAG, or other tools
  must be normalized into this shape before generated cases cite them.
- KnowledgeEvidence does not grant approval. GeneratedCaseCandidate review
  still follows the existing state machine and human review gates.
- Slice 30 must not add vector indexes, embeddings, reranking jobs, graph jobs,
  external provider calls, MCP runtime calls, RBAC, tenants, permissions,
  marketplace, cloud sync, release, or remote CI/CD behavior.

## 31.3 KnowledgeFeedbackDraft

KnowledgeFeedbackDraft is the draft-only output contract for
KnowledgeFeedbackAgent. It may be represented inside AITask output or a future
artifact/table, but Slice 34 does not implement a new table.

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| feedback_id | varchar(120) | yes | none | Stable id inside the owning artifact/task |
| project_id | uuid | yes | none | FK Project |
| feedback_type | varchar(80) | yes | none | positive_example, negative_example, bug_pattern, coverage_gap, test_strategy_note, regression_reminder |
| draft_knowledge_type | varchar(80) | yes | none | Target TestKnowledgeCard knowledge_type candidate |
| source_entity_type | varchar(80) | yes | none | GeneratedCaseCandidate, TestCase, ReviewHistory, FailureAnalysis, Report, TestRun, TestResult, KnowledgeEvidence |
| source_entity_id | uuid | no | null | Source entity id when available |
| source_artifact_ids | uuid[] | yes | {} | Same-project source Artifact ids |
| source_quote_or_hash | text | yes | none | Bounded quote or hash pointer |
| source_span | varchar(255) | no | null | Section, step, log span, report section, or review note pointer |
| recommendation | text | yes | none | Draft knowledge recommendation |
| confidence | int | yes | 0 | 0-100 model confidence, not approval |
| used_knowledge_evidence_ids | text[] | yes | {} | KnowledgeEvidence ids cited by feedback |
| unsupported_claims_json | jsonb | yes | [] | Claims rejected for insufficient evidence |
| review_findings_json | jsonb | yes | [] | Reviewer-facing quality notes |
| prompt_eligible | bool | yes | false | Always false until human review approves |
| status | varchar(40) | yes | draft | draft, needs_review, rejected, approved_by_human |
| review_action | varchar(80) | no | null | approve_feedback, reject_feedback, request_revision, mark_prompt_eligible |
| review_history_id | uuid | no | null | ReviewHistory id when a human review event is recorded |
| review_artifact_id | uuid | no | null | feedback review artifact id when available |
| prompt_eligibility_reason | text | no | null | Human-entered reason when prompt eligibility is approved or denied |
| handoff_payload_json | jsonb | yes | {} | Future TestKnowledgeCard handoff payload, not CRUD |

KnowledgeFeedbackDraft rules:

- KnowledgeFeedbackAgent may propose draft feedback only. It must not create,
  approve, archive, or mutate TestKnowledgeCard rows.
- `prompt_eligible=false` is mandatory for agent-created drafts. Prompt
  eligibility must be granted only by a later explicit human review workflow.
- Every draft must cite a reviewed source entity, same-project Artifact, or
  normalized KnowledgeEvidence. Free-floating model text is not valid source
  evidence.
- Accepted and rejected examples must remain distinct through
  `feedback_type`; rejected examples must not be converted into positive
  knowledge without human review.
- Failure- and report-derived bug patterns or coverage gaps must cite
  FailureAnalysis, Report, TestRun/TestResult, or evidence artifact ids.
- `confidence` is advisory and must not approve feedback, make it
  prompt-eligible, promote GeneratedCaseCandidate, or mutate historical
  ReviewHistory, FailureAnalysis, Report, TestRun, TestCase, or Artifact rows.
- Failure output uses `UNABLE_TO_CREATE_KNOWLEDGE_FEEDBACK` with
  `unsupported_claims_json` when source evidence is insufficient.
- Slice 34 must not add KnowledgeFeedbackAgent runtime, TestKnowledgeCard CRUD,
  automatic knowledge ingestion, vector indexes, embeddings, reranking, graph
  runtime, external provider calls, MCP runtime calls, RBAC, tenants,
  permissions, marketplace, cloud sync, release, or remote CI/CD behavior.

KnowledgeFeedbackDraft review gate rules:

- `approve_feedback`, `reject_feedback`, `request_revision`, and
  `mark_prompt_eligible` are human review actions only. Model confidence,
  review_findings, or schema validity must not apply those actions by itself.
- `approve_feedback` may move a draft to `approved_by_human` and may prepare a
  future `handoff_payload_json`, but it must not create TestKnowledgeCard rows
  in this contract.
- `reject_feedback` keeps the draft auditable with reviewer rationale and must
  not convert rejected feedback into positive knowledge.
- `request_revision` keeps source evidence, unsupported claims, and reviewer
  notes visible for a later draft; it must not mutate the historical source
  entities.
- `mark_prompt_eligible` requires an existing human approval, safe-to-show
  source evidence, reviewed source citations, and a
  `prompt_eligibility_reason`. It must not be inferred from `confidence`.
- A successful human review action appends or references ReviewHistory and may
  cite a `review_artifact_id`; invalid transitions must not append successful
  ReviewHistory.
- Feedback review must not mutate ReviewHistory, FailureAnalysis, Report,
  TestRun, TestResult, TestCase, GeneratedCaseCandidate, Artifact, or
  TestKnowledgeCard rows except for a future explicitly scoped review workflow
  owning the KnowledgeFeedbackDraft itself.
- Slice 35 must not add a feedback review runtime API, frontend review page,
  TestKnowledgeCard CRUD, automatic prompt eligibility, provider calls, MCP
  runtime, vector/graph runtime, artifact mutation, RBAC, tenants,
  permissions, or remote CI/CD behavior.

KnowledgeFeedbackDraft TestKnowledgeCard handoff payload rules:

- `handoff_payload_json` may contain a TestKnowledgeCard handoff candidate only
  after `approve_feedback` moves the draft to `approved_by_human`.
- The payload must include `source_feedback_id`, `review_history_id`,
  `review_artifact_id`, `source_entity_type`, `source_entity_id`,
  `source_artifact_ids`, `source_quote_or_hash`, `source_span`,
  `draft_knowledge_type`, `knowledge_type`, candidate title/summary/body,
  `safe_to_show`, `redaction_applied`, `allowed_for_prompt=false`,
  `duplicate_knowledge_card_ids`, `merge_hint`, `review_required=true`, and
  visible unsupported claims when they exist.
- `source_artifact_ids` must reference same-project Artifact rows.
  `source_quote_or_hash` must be a bounded safe quote or stable hash pointer;
  free-floating model text is not valid source evidence.
- `confidence` and schema validity are advisory. They must not create a card,
  approve a card, mark a card safe to show, set `allowed_for_prompt=true`, or
  merge duplicates.
- A prompt-eligible KnowledgeFeedbackDraft still does not make a
  TestKnowledgeCard prompt-eligible. The card candidate must keep
  `allowed_for_prompt=false` until a future explicit card review workflow
  grants prompt eligibility.
- Invalid handoff payloads must remain auditable with a failure code and must
  not append successful ReviewHistory, mutate historical source entities, or
  create fallback knowledge.
- A later TestKnowledgeCard Candidate Review may evaluate the handoff payload,
  but candidate review still must not mutate the KnowledgeFeedbackDraft source,
  create TestKnowledgeCard rows, or grant prompt eligibility.

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

ToolInvocation safety rules:

- A ToolInvocation must snapshot `tool_name`, `risk_level`,
  `approval_required`, `working_directory`, `command_snapshot`, and expected
  artifact policy from its ToolDefinition before execution.
- `approval_status=pending` is required before running any medium/high-risk
  invocation when `approval_required=true`. `approval_status=rejected` must
  transition only to `rejected` or a terminal failed state and must not run.
- `status=running` is valid only after allowlist validation, working-directory
  validation, approval validation, timeout validation, and artifact policy
  validation pass.
- Failed, timed-out, rejected, or cancelled invocations must preserve bounded
  stdout/stderr/error artifacts when available and must not rewrite prior
  successful artifacts.
- ToolInvocation output is execution evidence only. It must not approve cases,
  promote TestCase rows, conclude Reports, bypass AutomationDraft approval,
  bypass QualityGateDecision evidence, mutate Artifact rows outside its own
  declared outputs, call MCP runtime, or call external providers unless a later
  explicit runtime slice authorizes that behavior.

## 33. Artifact

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| owner_entity_type | varchar(80) | yes | none | ArtifactOwnerType |
| owner_entity_id | uuid | yes | none | Related entity |
| artifact_type | varchar(80) | yes | json | raw_llm_output, stdout, stderr, junit, coverage, trace, screenshot, patch, report_md, report_html, report_json, automation_draft_code, runtime_manifest, dependency_snapshot, environment_snapshot, context_markdown, context_text, context_json, context_yaml, context_openapi, diff_patch, changed_files, risk_analysis, unit_test_patch, patch_scope_gate, regression_plan, quality_gate, ci_run_metadata, knowledge_retrieval, test_knowledge_card_retrieval_boundary, test_knowledge_card_prompt_context_evidence, test_knowledge_card_prompt_context_consumption, test_knowledge_card_prompt_context_audit_summary, test_knowledge_card_prompt_context_audit_review_decision, test_knowledge_card_prompt_context_audit_review_summary_export |
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

TestKnowledgeCard prompt context evidence Artifact rule:

- Slice 41 prompt context evidence uses
  `artifact_type=test_knowledge_card_prompt_context_evidence`.
- `owner_entity_type=AITask` or `owner_entity_type=Project` until a later
  scoped prompt workflow owns a dedicated prompt request entity.
- `metadata_json` must include `created_by_component=TestKnowledgeCardPromptContextEvidence`,
  `prompt_context_evidence_action=build_prompt_context_evidence`,
  PromptVersion id, SkillVersion id, retrieval boundary artifact id, selected
  TestKnowledgeCard ids, omitted card ids, context manifest artifact id when
  available, source hashes, and omission reason values when applicable.
- This artifact is evidence only. It must not be treated as permission to run
  an AITask, assemble prompt text for a provider, or mark `used_knowledge=true`
  without a later explicit runtime contract.

TestKnowledgeCard prompt context consumption Artifact rule:

- Slice 42 prompt context consumption may use
  `artifact_type=test_knowledge_card_prompt_context_consumption` in a later
  scoped implementation.
- `owner_entity_type=AITask` or `owner_entity_type=Project` until a later
  scoped prompt workflow owns a dedicated prompt request entity.
- `metadata_json` must include `created_by_component=TestKnowledgeCardPromptContextConsumption`,
  `prompt_context_consumption_action=consume_prompt_context_evidence`, prompt
  context evidence artifact id, context manifest artifact id, consumed
  TestKnowledgeCard ids, consumed context entry ids, consumed source hashes,
  skipped evidence ids and skip reasons, output citation ids, `used_knowledge`
  decision, PromptVersion id, SkillVersion id, ReviewHistory ids, and failure
  code when applicable.
- This artifact is citation evidence only. It must not assemble prompt text,
  call providers, run an AITask, mutate prompt context evidence, mutate source
  artifacts, mutate TestKnowledgeCard rows, or mark `used_knowledge=true`
  without valid consumed citations.

TestKnowledgeCard prompt context audit summary Artifact rule:

- Slice 43 prompt context audit summary may use
  `artifact_type=test_knowledge_card_prompt_context_audit_summary` in a later
  scoped implementation.
- `owner_entity_type=AITask` or `owner_entity_type=Project` until a later
  scoped review/report workflow owns a dedicated summary entity.
- `metadata_json` must include `created_by_component=TestKnowledgeCardPromptContextAuditSummary`,
  `prompt_context_audit_summary_action=summarize_prompt_context_consumption`,
  prompt context consumption artifact id, prompt context evidence artifact id,
  context manifest artifact id, `used_knowledge` decision, cited
  TestKnowledgeCard ids, output citation ids, skipped evidence ids and skip
  reasons, unsupported claim count, source hashes, PromptVersion id,
  SkillVersion id, ReviewHistory ids, usage status, and failure code when
  applicable.
- This artifact is read-only audit evidence only. It must not render frontend
  pages, change report generation behavior, assemble prompt text, call
  providers, run an AITask, mutate prompt context consumption evidence, mutate
  prompt context evidence, mutate source artifacts, rewrite `used_knowledge`,
  invent citations, or mutate TestKnowledgeCard rows.

TestKnowledgeCard prompt context audit review decision Artifact rule:

- Slice 44 prompt context audit review decision may use
  `artifact_type=test_knowledge_card_prompt_context_audit_review_decision` in
  a later scoped implementation.
- `owner_entity_type=AITask` or `owner_entity_type=Project` until a later
  scoped review workflow owns a dedicated review decision entity.
- `metadata_json` must include `created_by_component=TestKnowledgeCardPromptContextAuditReviewDecision`,
  `prompt_context_audit_review_decision_action=review_prompt_context_audit_summary`,
  audit summary artifact id, prompt context consumption artifact id, prompt
  context evidence artifact id, context manifest artifact id, `used_knowledge`
  decision, usage status, review action, reviewer label when available,
  accepted citation ids, questioned citation ids, rejected citation ids,
  follow-up flags, requested clarification fields, source hashes,
  PromptVersion id, SkillVersion id, ReviewHistory id, and failure code when
  applicable.
- This artifact is human review decision evidence only. It must not render
  frontend pages, change report generation behavior, assemble prompt text, call
  providers, run an AITask, mutate audit summary evidence, mutate prompt
  context consumption evidence, mutate prompt context evidence, mutate source
  artifacts, rewrite `used_knowledge`, invent citations, create prompt
  eligibility, approve TestKnowledgeCard content, approve generated cases, or
  mutate TestKnowledgeCard rows.

TestKnowledgeCard prompt context audit review summary export Artifact rule:

- Slice 45 prompt context audit review summary export may use
  `artifact_type=test_knowledge_card_prompt_context_audit_review_summary_export`
  in a later scoped implementation.
- `owner_entity_type=AITask` or `owner_entity_type=Project` until a later
  scoped export workflow owns a dedicated summary export entity.
- `metadata_json` must include `created_by_component=TestKnowledgeCardPromptContextAuditReviewSummaryExport`,
  `prompt_context_audit_review_summary_export_action=export_prompt_context_audit_review_summary`,
  audit review decision artifact id, audit summary artifact id, prompt context
  consumption artifact id, prompt context evidence artifact id, context
  manifest artifact id, `used_knowledge` decision, usage status, review action,
  review outcome summary, accepted citation group, questioned citation group,
  rejected citation group, unresolved follow-up flags, unsupported claim
  references, source hashes, PromptVersion id, SkillVersion id, ReviewHistory
  links, and failure code when applicable.
- This artifact is summary export evidence only. It must not render frontend
  pages, change report generation behavior, expose an export/download endpoint,
  assemble prompt text, call providers, run an AITask, mutate audit review
  decision evidence, mutate audit summary evidence, mutate prompt context
  consumption evidence, mutate prompt context evidence, mutate source
  artifacts, rewrite `used_knowledge`, invent citations, create prompt
  eligibility, approve TestKnowledgeCard content, approve generated cases, or
  mutate TestKnowledgeCard rows.

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
