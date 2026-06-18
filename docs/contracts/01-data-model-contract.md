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
| LLMCallStatus | started, succeeded, failed, timeout, schema_failed |
| MCPServerStatus | active, disabled, archived |
| FailureClassification | product_defect, test_script_issue, environment_issue, test_data_issue, dependency_issue, flaky_test, insufficient_evidence |

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

Relationship: Project 1:N Module, Repository, Environment, TestCommand, Requirement, TestCase, AITask, LLMCallLog, Report.

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
| command_type | varchar(40) | yes | pytest | pytest, npm, playwright |
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
| execution_strategy | varchar(60) | yes | artifact_runtime_copy | artifact_runtime_copy in V1; manual_export is future |
| approval_required | bool | yes | true | Must be approved in V1 |
| status | AutomationDraftStatus | yes | draft_generated | Status |
| review_comment | text | no | null | Review comment |
| runtime_artifact_id | uuid | no | null | Artifact for approved temporary runtime file |
| promoted_artifact_id | uuid | no | null | Promoted artifact |

V1 execution rule: an approved AutomationDraft is copied into a Chtest-managed artifact runtime directory before execution. It is not written directly into the target business repository. The copied runtime file is stored as an Artifact and referenced by `runtime_artifact_id`.

## 17. GitChangeSet

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| repository_id | uuid | no | null | FK Repository |
| source_type | varchar(40) | yes | local_diff | local_diff, uploaded_diff |
| base_ref | varchar(160) | no | null | Base commit or branch |
| head_ref | varchar(160) | no | null | Head commit or branch |
| summary | text | no | null | Change summary |
| overall_risk | RiskLevel | yes | medium | Overall risk |
| status | varchar(40) | yes | created | created, analyzed, reported, archived |

## 18. GitChangedFile

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| change_set_id | uuid | yes | none | FK GitChangeSet |
| path | text | yes | none | File path |
| old_path | text | no | null | Rename source path |
| change_type | varchar(40) | yes | modified | added, modified, deleted, renamed |
| language | varchar(60) | no | null | Language |
| file_role | varchar(60) | yes | unknown | source, test, docs, config, migration, fixture, build, unknown |
| risk_level | RiskLevel | yes | medium | File risk |
| risk_reasons_json | jsonb | yes | [] | Risk reasons |
| lines_added | int | yes | 0 | Added lines |
| lines_deleted | int | yes | 0 | Deleted lines |

## 19. UnitTestPatch

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| change_set_id | uuid | yes | none | FK GitChangeSet |
| ai_task_id | uuid | yes | none | FK AITask |
| patch_text | text | yes | none | Unified diff |
| target_framework | varchar(60) | yes | pytest | pytest/jest/vitest |
| scope_gate_result_json | jsonb | yes | {} | Path gate result |
| test_intent | text | yes | none | Test intent |
| coverage_target_json | jsonb | yes | [] | Coverage target |
| status | PatchStatus | yes | generated | Status |
| review_comment | text | no | null | Review comment |

## 20. GitRiskAnalysis

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| change_set_id | uuid | yes | none | FK GitChangeSet |
| ai_task_id | uuid | yes | none | FK AITask |
| summary | text | yes | none | Change risk summary |
| overall_risk | RiskLevel | yes | medium | Overall risk |
| impacted_modules_json | jsonb | yes | [] | Impacted module names or paths |
| high_risk_files_json | jsonb | yes | [] | High-risk file explanations |
| test_recommendations_json | jsonb | yes | [] | Recommended tests and reasons |
| status | varchar(40) | yes | analyzed | analyzed, confirmed, archived |

Relationship: GitChangeSet 1:1 GitRiskAnalysis in V1.

## 21. RegressionPlan

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| change_set_id | uuid | yes | none | FK GitChangeSet |
| ai_task_id | uuid | no | null | FK AITask when generated by RegressionAgent |
| strategy | varchar(80) | yes | targeted_regression | targeted_regression, full_regression, manual_selection, no_run |
| recommended_commands_json | jsonb | yes | [] | TestCommand ids, command snapshots, and reasons |
| recommended_suites_json | jsonb | yes | [] | Future TestSuite recommendations |
| manual_attention_json | jsonb | yes | [] | Items requiring human decision |
| status | varchar(40) | yes | draft | draft, approved, executed, replaced, archived |

## 22. TestRun

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| change_set_id | uuid | no | null | FK GitChangeSet |
| automation_draft_id | uuid | no | null | FK AutomationDraft |
| test_command_id | uuid | no | null | FK TestCommand |
| tool_invocation_id | uuid | no | null | FK ToolInvocation |
| name | varchar(255) | yes | none | Run name |
| command | text | yes | none | Executed command |
| working_directory | text | yes | none | Working directory |
| status | TestRunStatus | yes | created | Status |
| exit_code | int | no | null | Exit code |
| duration_ms | int | no | null | Duration |
| parsed_result_json | jsonb | yes | {} | Parsed aggregate result |

## 23. TestResult

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

## 24. FailureAnalysis

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| test_run_id | uuid | no | null | FK TestRun |
| test_result_id | uuid | no | null | FK TestResult |
| ai_task_id | uuid | yes | none | FK AITask |
| classification | FailureClassification | yes | insufficient_evidence | Classification |
| confidence | numeric(3,2) | yes | 0.00 | 0.00-1.00 confidence score |
| evidence_artifact_ids | uuid[] | yes | {} | Evidence artifacts |
| summary | text | yes | none | Human-readable summary |
| root_cause | text | no | null | Evidence-based root cause |
| suggested_actions_json | jsonb | yes | [] | Suggested next actions |
| status | varchar(40) | yes | draft | draft, confirmed, rejected |

## 25. Report

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| report_type | varchar(80) | yes | execution | requirement_review, case_quality, automation_execution, git_quality, ai_effectiveness |
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
| started_at | timestamptz | no | null | Start time |
| finished_at | timestamptz | no | null | Finish time |

## 27. LLMCallLog

LLMCallLog records each provider call made inside an AITask. AITask is the workflow-level task; LLMCallLog is the per-model-call audit log. V1 may create one LLMCallLog per AITask, but the model supports retries, schema-repair calls, and future model comparison.

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
| status | ToolDefinitionStatus | yes | active | Status |

Unique constraint: project_id + name, treating null project_id as built-in scope.

## 31. ToolInvocation

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

## 32. Artifact

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| owner_entity_type | varchar(80) | yes | none | AITask/TestRun/Report/etc. |
| owner_entity_id | uuid | yes | none | Related entity |
| artifact_type | varchar(80) | yes | json | raw_llm_output, stdout, stderr, junit, coverage, trace, screenshot, patch, report_md, report_html, report_json |
| file_path | text | yes | none | Artifact-relative path |
| mime_type | varchar(120) | yes | application/json | MIME |
| size_bytes | bigint | yes | 0 | File size |
| sha256 | varchar(128) | yes | none | Content hash |
| metadata_json | jsonb | yes | {} | Metadata |

## 33. CaseQualityMetric

CaseQualityMetric stores batch-level AI case-generation quality. Ratio fields use `0.00-1.00`; UI may render percentages.

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| generation_task_id | uuid | yes | none | FK CaseGenerationTask |
| requirement_id | uuid | yes | none | FK Requirement |
| prompt_version_id | uuid | yes | none | FK PromptVersion |
| skill_version_id | uuid | yes | none | FK SkillVersion |
| model_provider | varchar(80) | yes | mock | Provider |
| model_name | varchar(120) | yes | mock-model | Model |
| generated_count | int | yes | 0 | Candidate count |
| approved_count | int | yes | 0 | Directly approved count |
| approved_after_edit_count | int | yes | 0 | Edited then approved count |
| rejected_count | int | yes | 0 | Rejected count |
| optimization_count | int | yes | 0 | Optimization requested count |
| unavailable_count | int | yes | 0 | Marked unavailable count |
| duplicate_count | int | yes | 0 | Potential duplicate count |
| field_complete_rate | numeric(3,2) | yes | 0.00 | Required-field completeness, 0.00-1.00 |
| acceptance_rate | numeric(3,2) | yes | 0.00 | approved / generated_count |
| edited_acceptance_rate | numeric(3,2) | yes | 0.00 | approved_after_edit / generated_count |
| rejection_rate | numeric(3,2) | yes | 0.00 | rejected / generated_count |
| duplicate_rate | numeric(3,2) | yes | 0.00 | duplicate_count / generated_count |
| review_progress_rate | numeric(3,2) | yes | 0.00 | reviewed candidates / generated_count |

Relationship: CaseGenerationTask 1:1 CaseQualityMetric in V1.

## 34. KnowledgeProviderConfig

KnowledgeProviderConfig is the V1 configuration shell for future RAG integration. The default provider returns no evidence and does not block AI workflows.

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| name | varchar(160) | yes | default-empty-knowledge | Provider name |
| provider_type | varchar(80) | yes | empty | empty, http, mcp, custom |
| enabled | bool | yes | false | Disabled by default |
| config_json | jsonb | yes | {} | Non-secret config |
| secret_ref_json | jsonb | yes | {} | Secret references only |
| status | EntityStatus | yes | active | Status |

## 35. KnowledgeEvidence

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | yes | none | FK Project |
| ai_task_id | uuid | yes | none | FK AITask |
| provider_config_id | uuid | no | null | FK KnowledgeProviderConfig |
| title | varchar(255) | yes | none | Evidence title |
| source_uri | text | no | null | Source URL/path/id |
| content_excerpt | text | no | null | Safe short excerpt |
| relevance_score | numeric(3,2) | no | null | 0.00-1.00 when provider supplies it |
| metadata_json | jsonb | yes | {} | Provider metadata |

## 36. McpServerConfig

McpServerConfig is a placeholder for V2 MCP integration. V1 stores it only as disabled configuration and does not depend on MCP for core workflows.

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| project_id | uuid | no | null | Null means global config |
| name | varchar(160) | yes | none | Server name |
| server_type | varchar(80) | yes | external | external, local |
| endpoint | text | no | null | URL, command id, or local adapter name |
| tool_mapping_json | jsonb | yes | {} | MCP tool to ToolDefinition mapping |
| secret_ref_json | jsonb | yes | {} | Secret references only |
| status | MCPServerStatus | yes | disabled | Disabled in V1 by default |

## 37. Relationship Summary

```text
Workspace -> Project
Project -> Module / Repository / Environment / TestCommand
Project -> Requirement -> RequirementReview -> RiskItem
Requirement -> CaseGenerationTask -> GeneratedCaseCandidate -> TestCase
CaseGenerationTask -> CaseQualityMetric
TestCase/Requirement -> AutomationDraft -> TestRun -> TestResult -> Report
TestRun/TestResult -> FailureAnalysis -> Report
Repository -> GitChangeSet -> GitChangedFile -> GitRiskAnalysis -> UnitTestPatch -> RegressionPlan -> TestRun -> Report
AITask -> LLMCallLog
AITask -> Artifact
ToolDefinition -> ToolInvocation -> Artifact
Report -> Artifact
PromptVersion + SkillVersion -> AITask
KnowledgeProviderConfig -> KnowledgeEvidence
McpServerConfig -> ToolDefinition mapping
```
