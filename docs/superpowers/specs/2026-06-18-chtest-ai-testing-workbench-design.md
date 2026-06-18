# Chtest AI Testing Workbench Design

## 1. Design Summary

Chtest V1 is an AI Testing Workbench for individual test engineers and automation test engineers. It turns requirements and local code changes into reviewed test assets, automation drafts, controlled executions, failure analysis, and quality reports.

The product uses real infrastructure from the first release: Docker Compose, PostgreSQL, Redis, FastAPI, worker process, Vue 3, Arco Design Vue, artifact storage, Prompt/Skill registry, and controlled Tool Adapter execution.

## 2. V1 Product Lines

### Mainline A: Requirement To Reviewed Cases

```text
Requirement
  -> RequirementReviewAgent
  -> RiskAgent
  -> CaseGenerationAgent
  -> CaseReviewSession
  -> TestCase Library
  -> Case Quality Metrics
```

### Mainline B: Reviewed Case To Automation Execution

```text
TestCase / Requirement
  -> AutomationDraftAgent
  -> AutomationDraft Review
  -> Approved AutomationDraft
  -> ToolExecutionAgent
  -> TestRun / TestResult
  -> FailureAnalysisAgent when failed
  -> ReportAgent
```

### Support Line: Git Quality

```text
Local Git Diff
  -> GitDiffAgent
  -> UnitTestAgent
  -> UnitTestPatch Review
  -> TestRunner
  -> RegressionAgent
  -> Git Quality Report
```

## 3. V1 Scope

In scope:

- Docker-controlled local environment.
- Single-user workspace.
- Project, module, repository, environment, and test command configuration.
- AI task state machine.
- Prompt and Skill registry.
- Requirement review and risk matrix.
- AI case generation candidates.
- Case review window and quality metrics.
- Test case library.
- AutomationDraft generation for pytest and Playwright.
- Approval-gated tool execution.
- TestRun, TestResult, FailureAnalysis, and Report.
- Local Git Quality support workflow.
- Empty Knowledge Adapter.
- MCP-ready ToolDefinition schema.

Out of scope:

- Built-in RAG/vector DB.
- GitHub webhook or GitHub MCP as a V1 dependency.
- Enterprise test management.
- Full low-code UI automation editor.
- Appium device management.
- Fiddler-level traffic capture and replay.
- Full Postman or JMeter replacement.

## 4. Key Pages

- Workbench Dashboard.
- Project Settings.
- Requirement Review.
- Case Generation Review.
- Test Case Library.
- Automation Draft Center.
- Execution Center.
- Git Quality Center.
- Tool Adapter Center.
- Prompt & Skill Center.
- Report Center.
- Knowledge Integration Settings.

## 5. Data Model Groups

- Project config: Project, Module, Repository, Environment, TestCommand.
- Requirement: Requirement, RequirementReview, RiskItem.
- Case review: CaseGenerationTask, GeneratedCaseCandidate, TestCase.
- Automation: AutomationDraft.
- Git quality: GitChangeSet, GitChangedFile, UnitTestPatch.
- AI runtime: AITask, PromptVersion, SkillVersion.
- Tools: ToolDefinition, ToolInvocation.
- Execution: TestRun, TestResult, FailureAnalysis, Report.
- Evidence: Artifact.

## 6. Reference Migration

WHartTest references:

- MCP tool pattern.
- Skill packaging and `SKILL.md` convention.
- Generated cases modal interaction model.
- `review_status` model.
- Optimization suggestion flow.
- Actuator execution design.

MeterSphere references:

- Case review page structure.
- Pass-rate and review progress line.
- Test asset management layout.
- Test plan and report status components.
- API case AI template structure.

## 7. Quality Gates

- AI-generated cases require review before library insertion.
- AutomationDraft requires review before execution.
- UnitTestPatch requires path scope validation and approval.
- High-risk tool invocations require manual approval.
- Reports require evidence references.
- RAG absence must not fail any workflow.
