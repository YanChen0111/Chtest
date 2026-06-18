# Chtest Positioning And Scope

## 1. Final Positioning

Chtest V1 is an AI Testing Workbench for individual test engineers and automation test engineers.

It focuses on one practical outcome: use AI to raise testing efficiency and quality across requirement review, test case design, case review, automation draft generation, controlled execution, failure analysis, and report generation.

The first version is single-user, local-first, review-driven, and measurable. It must feel like a serious daily testing tool, not a demo and not a team management platform.

## 2. Product Boundary

### In Scope For V1

- Project, module, repository, environment, and test command configuration.
- Requirement creation and AI-assisted requirement review.
- AI test case generation from requirements.
- Human review workflow for generated cases.
- Test case library and case quality metrics.
- AutomationDraft generation for pytest and Playwright.
- Approval-gated automation execution.
- TestRun, TestResult, artifacts, failure analysis, and reports.
- Local Git diff analysis, scoped unit test patch generation, approval, and regression execution.
- Prompt, Skill, ToolDefinition, ToolInvocation, and AI quality measurement.
- KnowledgeAdapter interface for future RAG connection.

### Out Of Scope For V1

- Multi-user collaboration, roles, permissions, departments, and enterprise audit.
- Defect lifecycle management as a Jira replacement.
- Full API testing platform parity with Postman or MeterSphere.
- Full performance testing platform parity with JMeter.
- Full mobile automation platform.
- Fiddler-level traffic capture and replay.
- Built-in RAG indexing, vector database, and reranking service.
- Unapproved AI code changes to business source files.

## 3. Mainline And Support Workflow

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

### Support Workflow: Git Quality

```text
Local Git Diff
  -> GitDiffAgent
  -> UnitTestAgent
  -> UnitTestPatch Review
  -> TestRunner
  -> RegressionAgent
  -> ReportAgent
```

Git Quality supports code-change validation. It does not replace the main product loop.

## 4. Tool Priority

| Priority | Capability | V1 Decision |
|---|---|---|
| P0 | pytest TestRunner | Must implement |
| P0 | Git diff reader and patch scope validator | Must implement |
| P0 | Artifact parser and report generator | Must implement |
| P1 | Playwright smoke execution | Implement after pytest loop is stable |
| P1 | Newman API execution | Add after V1 core loop |
| P2 | JMeter execution | Add after execution/report contracts are stable |
| P3 | Appium and traffic capture | Roadmap |

## 5. AI Safety Boundary

AI output must be structured, schema-validated, reviewable, and traceable.

AI can generate candidates, drafts, patches, plans, and analysis. AI cannot directly promote cases, apply patches, write business source files, or execute high-risk commands without approval.

## 6. Documentation Priority

When documents appear to disagree, follow this order:

1. `docs/product/01-positioning-and-scope.md`.
2. `docs/contracts/*`.
3. `docs/implementation/01-v1-delivery-plan.md`.
4. `memory/13-ai-readable-project-brief.md`.
5. `docs/fixtures/*`.
6. `docs/architecture/*`.
7. `docs/reference/*` and `docs/superpowers/*`.
