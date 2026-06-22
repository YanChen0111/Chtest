# Chtest Positioning And Scope

## 1. Final Positioning

Chtest V1 is an AI testing evidence workbench for individual test engineers and automation test engineers.

It focuses on one practical outcome: turn requirements and code changes into human-reviewed, sandbox-executed, evidence-backed, and quality-measured testing assets.

The first version is single-user, local-first, review-driven, and measurable. It must feel like a serious daily testing tool, not a demo and not a team management platform.

V1 should not be positioned as only an AI test-case generator. Generation is useful only when the result can be reviewed, executed, traced to artifacts, and measured.

## 2. V1 North Star

The release spine is the evidence closed loop:

```text
Requirement or local code change
  -> AI risk and test analysis
  -> reviewed test cases or test patches
  -> approved AutomationDraft or UnitTestPatch
  -> controlled runner execution
  -> runtime artifacts and evidence
  -> failure analysis or repair candidate
  -> report
  -> AI quality metrics
```

`docs/fixtures/00-v1-demo-path.md` is the minimum product proof. V1 is not accepted until a user can follow that path and understand what AI analyzed, what was approved, what executed, what evidence supports the conclusion, and what happens next after failure.

## 3. Product Boundary

### In Scope For V1

- Project, module, repository, environment, and test command configuration.
- Requirement creation and AI-assisted requirement review.
- AI test case generation from requirements.
- Human review workflow for generated cases.
- Test case library and case quality metrics.
- AutomationDraft generation for pytest and Playwright.
- Approval-gated automation execution.
- TestRun, TestResult, artifacts, failure analysis, and reports.
- V1 minimum evidence demo: requirement -> reviewed case -> approved AutomationDraft -> sandboxed execution -> evidence report.
- Lightweight context artifacts for requirement documents, API samples, logs, fixtures, and bug summaries.
- Small model/prompt evaluation bench for schema validity, usefulness, execution success, repair success, and evidence completeness.
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
- Broad model leaderboard or benchmark platform before the V1 evidence loop works.
- Unapproved AI code changes to business source files.

## 4. Mainline And Support Workflow

### Mainline A: Requirement To Evidence-Ready Cases

```text
Requirement
  -> RequirementReviewAgent
  -> RiskAgent
  -> CaseGenerationAgent
  -> CaseReviewSession
  -> TestCase Library
  -> Case Quality Metrics
```

### Mainline B: Reviewed Case To Automation Evidence

```text
TestCase / Requirement
  -> AutomationDraftAgent
  -> AutomationDraft Review
  -> Approved AutomationDraft
  -> ToolExecutionAgent
  -> TestRun / TestResult
  -> FailureAnalysisAgent when failed
  -> AutomationRepairTask when repair is needed
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

## 5. Tool Priority

| Priority | Capability | V1 Decision |
|---|---|---|
| P0 | pytest TestRunner | Must implement |
| P0 | Docker runner mode | Preferred product acceptance runner when available |
| P0 | Git diff reader and patch scope validator | Must implement |
| P0 | Artifact parser and report generator | Must implement |
| P1 | Playwright smoke execution | Implement after pytest loop is stable |
| P1 | Newman API execution | Add after V1 core loop |
| P2 | JMeter execution | Add after execution/report contracts are stable |
| P3 | Appium and traffic capture | Roadmap |

## 6. AI Safety Boundary

AI output must be structured, schema-validated, reviewable, and traceable.

AI can generate candidates, drafts, patches, plans, and analysis. AI cannot directly promote cases, apply patches, write business source files, or execute high-risk commands without approval.

Every AI task must record the prompt, skill, model, input artifacts, output artifacts, context artifacts used, schema validation result, and review or execution outcome when available.

## 7. Documentation Priority

When documents appear to disagree, follow this order:

1. `docs/product/01-positioning-and-scope.md`.
2. `docs/contracts/*`.
3. `docs/implementation/04-ai-vibecoding-governance.md`.
4. `docs/implementation/01-v1-delivery-plan.md`.
5. `memory/13-ai-readable-project-brief.md`.
6. `docs/fixtures/*`.
7. `docs/architecture/*`.
8. `docs/reference/*` and `docs/superpowers/*`.
