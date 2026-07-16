# Chtest Agent Workflow Design

## 1. Purpose

This document defines how Chtest V1 uses Agent, Prompt, Skill, Tool Adapter, and Knowledge Adapter to deliver the testing workflow. The goal is reviewable AI output, controlled execution, traceable evidence, and measurable quality improvement.

## 2. Runtime Model

```text
User Action
  -> Backend creates AITask
  -> Orchestrator loads Project Context
  -> Agent selects Prompt + Skill + optional Knowledge evidence
  -> LLM produces structured output
  -> Schema Validator validates output
  -> Service writes business result
  -> Tool Adapter executes approved tools when needed
  -> Artifact Store saves raw and parsed evidence
  -> Metrics Service records AI quality events
  -> UI shows review / execution / report result
```

Every AI task records:

- project_id.
- module_id when available.
- agent_name.
- prompt_name, prompt_version, prompt_hash.
- skill_name, skill_version, skill_hash.
- model_provider and model_name.
- input artifact.
- output artifact.
- schema validation result.
- tool invocations.
- knowledge evidence.
- token usage, runtime, and status.

## 3. Shared Agent Context

Backend services should pass a unified context object to agents:

```text
AgentContext
  task_id
  project_id
  user_id
  module_id
  environment_id
  repository_id
  requirement_id
  test_case_id
  automation_draft_id
  cicd_run_id
  prompt_version
  skill_version
  model_config
  knowledge_evidence[]
  artifact_root
  trace_id
```

Agents do not directly modify database tables. They return structured results; services validate and persist those results.

## 4. AITask State Machine

```text
created
  -> pending
  -> running
  -> waiting_review
  -> waiting_approval
  -> succeeded
  -> failed
  -> cancelled
```

State definitions follow `docs/contracts/03-state-machines.md`.

## 5. Agent Responsibilities

### 5.1 OrchestratorAgent

Responsibilities:

- Create workflow steps from user actions.
- Chain multiple agents.
- Advance state machines.
- Persist workflow artifacts.
- Pause at human review or approval checkpoints.

Inputs: workflow_type, project_id, entity ids.

Outputs: workflow_run, step results, next_action.

Forbidden actions: bypassing human review, applying high-risk patches, or executing unapproved high-risk tools.

### 5.2 RequirementReviewAgent

Responsibilities:

- Score requirement quality on six dimensions.
- Identify ambiguity, contradiction, missing boundary, untestable statement, and risk.
- Generate clarification questions and testability suggestions.

Inputs: requirement text, module, target test type, optional evidence.

Outputs: RequirementReview JSON.

Quality gate: completeness, clarity, consistency, testability, feasibility, and logic must all be present.

### 5.3 RiskAgent

Responsibilities:

- Convert requirement review results into a risk matrix.
- Mark business, technical, data, environment, and regression risks.

Outputs: RiskItem[].

Quality gate: each risk needs impact, severity, and suggested test strategy.

### 5.4 CaseGenerationAgent

Responsibilities:

- Generate structured candidate cases from requirement, review, and risks.
- Include requirement references and AI generation reason.

Outputs: GeneratedCaseCandidate[].

Quality gates:

- Output must pass JSON schema.
- Each case must include steps and expected results.
- Each case must reference requirement text or risk item.

Forbidden action: directly creating official TestCase records.

### 5.5 CaseReviewAgent

Responsibilities:

- Assist the user in reviewing candidate cases.
- Explain low-quality cases.
- Generate optimized versions when the user requests optimization.

Outputs: case_review_result or optimized_case_candidate.

Quality gate: optimization must explain what changed and why.

### 5.6 AutomationDraftAgent

Responsibilities:

- Generate pytest or Playwright AutomationDraft from Requirement or TestCase.
- Produce `draft_code`, `target_framework`, `suggested_file_path`, `execution_notes`, and `risk_notes`.
- Explain dependencies, fixtures, mocks, data setup, and execution assumptions.

Inputs:

- Requirement or TestCase.
- Project language and repository context.
- Existing test command and environment context when available.
- Optional knowledge evidence.

Outputs: AutomationDraft JSON.

Quality gates:

- Output must pass AutomationDraft schema.
- Draft must be executable in principle with declared dependencies.
- Draft must not write to business source files.
- Draft must enter human review before execution.

Forbidden actions:

- Directly editing the target repository.
- Directly applying generated code.
- Creating hidden network or credential dependencies.

### 5.7 CICDChangeAnalysisAgent

Responsibilities:

- Read CICDRun.
- Analyze change intent, affected modules, and risk level.
- Provide context for UnitTestAgent and RegressionAgent.

Outputs: `risk_analysis.json` artifact.

Quality gate: every high-risk file must include risk reason and suggested tests.

### 5.8 UnitTestAgent

Responsibilities:

- Generate UnitTestPatch from a local diff.
- Match existing test style and fixtures.
- Output patch, test intent, coverage target, and risk notes.

Outputs: UnitTestPatch.

Quality gates:

- Patch must pass scope gate.
- Patch must modify test directories only.
- Patch must not add skip/xfail to hide failures.

### 5.9 RegressionAgent

Responsibilities:

- Select regression commands based on changed files, case library, and TestCommand configuration.
- Explain why each command is selected.

Outputs: RegressionPlan.

Quality gate: high-risk changes must recommend at least one regression command; if scope is unclear, recommend full configured regression or manual selection.

### 5.10 ToolExecutionAgent

Responsibilities:

- Call Tool Adapter using ToolDefinition.
- Enforce approval, timeout, cancellation, and artifact capture.
- Parse execution artifacts into TestRun and TestResult.

Outputs: ToolInvocation, TestRun, TestResult.

Forbidden action: executing arbitrary shell outside ToolDefinition allowlist.

### 5.11 FailureAnalysisAgent

Responsibilities:

- Analyze stdout, stderr, JUnit, coverage, screenshots, traces, and related artifacts.
- Classify failure cause.
- Produce evidence-backed next actions.

Outputs: FailureAnalysis.

Quality gate: when evidence is insufficient, classification must be `insufficient_evidence`.

### 5.12 ReportAgent

Responsibilities:

- Summarize requirements, cases, execution, failures, and AI quality metrics.
- Generate Markdown, HTML, and JSON reports.

Outputs: Report.

Quality gate: every key conclusion must reference data or artifact.

## 6. Main Workflow A: Requirement To Reviewed Cases

```text
Requirement
  -> RequirementReviewAgent
  -> RiskAgent
  -> user confirms requirement review
  -> CaseGenerationAgent
  -> schema_validate_candidates
  -> duplicate_check
  -> CaseReviewSession created
  -> user_case_review
  -> approved candidates become TestCase
  -> case quality metrics updated
  -> ReportAgent optional case quality report
```

Human checkpoints:

- Requirement review confirmation.
- Candidate case review.
- Case optimization decision.

Acceptance output:

- RequirementReview.
- RiskItem[].
- GeneratedCaseCandidate[].
- TestCase records for approved candidates.
- Case quality metrics.

## 7. Main Workflow B: Case To Automation Execution

```text
TestCase / Requirement
  -> AutomationDraftAgent
  -> schema_validate
  -> AutomationDraft created
  -> user_review
  -> edit if needed
  -> approve
  -> ToolExecutionAgent
  -> TestRun
  -> TestResult
  -> FailureAnalysisAgent if failed
  -> ReportAgent
```

Human checkpoints:

- AutomationDraft review.
- Tool execution approval when command risk requires it.
- Failure analysis confirmation when needed.

Acceptance output:

- AutomationDraft.
- ToolInvocation.
- TestRun.
- TestResult[].
- FailureAnalysis when failed.
- Report.

## 8. Support Workflow: CI/CD Quality Center

```text
Local Git Diff / CI/CD Change
  -> ChangeSetTool.get_diff
  -> CICDChangeAnalysisAgent
  -> UnitTestAgent
  -> validate_patch_scope
  -> user_patch_review
  -> apply_patch if approved
  -> TestRunner.run_new_tests
  -> RegressionAgent
  -> user_confirm_regression_plan
  -> TestRunner.run_regression
  -> FailureAnalysisAgent if failed
  -> ReportAgent.generate_cicd_quality_report
```

Human checkpoints:

- Applying UnitTestPatch.
- Executing high-risk commands.
- Final report conclusion when needed.

Acceptance output:

- CICDRun.
- CICDChangedFile[].
- UnitTestPatch.
- TestRun records.
- CI/CD quality report.

## 9. Tool Execution Workflow

```text
create_tool_invocation
  -> load ToolDefinition
  -> approval_check
  -> ToolExecutionAgent
  -> capture stdout/stderr/artifacts
  -> parse_artifacts
  -> TestRun saved
  -> TestResult saved
  -> FailureAnalysisAgent if failed
  -> ReportAgent
```

## 10. Prompt And Skill Version Management

Prompt version fields:

```text
name
version
hash
agent_name
input_schema
output_schema
status: draft | active | deprecated
created_at
```

Skill version fields:

```text
name
version
hash
applicable_agents[]
methodology
quality_gates[]
forbidden_actions[]
tool_permissions[]
status
```

Rules:

- New AI tasks must use active Prompt and Skill versions.
- Prompt file changes create a new version and hash.
- Published version content is immutable.
- Deprecated versions remain readable for completed tasks but cannot be default choices for new tasks.

## 11. Output Schema Principles

AI primary output must be structured JSON. Free text is allowed only in fields such as `summary`, `reasoning_summary`, `human_readable_note`, `execution_notes`, and `risk_notes`.

Schema validation failure rules:

- Save raw output artifact.
- Mark AITask failed or partial_failed.
- Do not write business entities.
- UI provides retry.

## 12. Tool Adapter Safety

| Risk | Operation | Policy |
|---|---|---|
| low | read diff, read artifact | auto allowed |
| medium | run tests, generate report | confirm by default, configurable |
| high | apply patch, write files, real environment API | approval required |
| forbidden | delete repository, arbitrary shell, push main branch | forbidden |

All ToolInvocation records must include:

- tool_name.
- input summary.
- approval status.
- started_at and finished_at.
- exit_code.
- stdout/stderr artifacts.
- parsed result.

## 13. Knowledge Adapter

V1 does not build RAG. The interface is stable:

```text
KnowledgeAdapter.search_context(query, project_id, filters) -> evidence[]
KnowledgeAdapter.get_document(document_id) -> document
KnowledgeAdapter.list_sources(project_id) -> source[]
```

`rank_evidence` or other reranking behavior is a later external provider capability, not a V1 internal RAG implementation requirement.

When no provider is configured:

```json
{
  "used_knowledge": false,
  "knowledge_provider": "none",
  "evidence": []
}
```

Agents must work without RAG.

## 14. Implementation Notes For Future AI Sessions

- Add a new Agent only when current Agents cannot cover the behavior.
- Every Prompt declares input and output schema.
- Every Tool has ToolDefinition, risk level, timeout, allowlist, and artifact policy.
- Every workflow declares human checkpoints.
- Every AI output contributes to quality metrics.
- AI output cannot bypass review to mutate official assets.
