# Chtest Positioning And Scope

## 1. Final Positioning

Chtest V1 is an AI testing evidence workbench for individual test engineers and automation test engineers.

It focuses on one practical outcome: turn requirements and local code changes into human-reviewed, sandbox-executed, evidence-backed, and quality-measured testing assets.

The first version is single-user, local-first, review-driven, and measurable. It must feel like a serious daily testing tool, not a demo and not a team management platform.

V1 should not be positioned as only an AI test-case generator or a broad test management platform. Generation is useful only when the result can be reviewed, executed, traced to artifacts, and measured.

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

`docs/fixtures/00-v1-demo-path.md` is the minimum product proof. V1 is not accepted until a user can follow that path and understand what AI analyzed, which context artifacts were used, what was approved, what executed, what evidence supports the conclusion, and what happens next after failure.

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
- V1 minimum evidence demo: requirement -> ContextArtifact -> reviewed case -> approved AutomationDraft -> sandboxed execution -> evidence report.
- Runner sandbox metadata, runtime manifest, dependency snapshot, and environment snapshot for AutomationDraft execution.
- CI/CD Quality Center support: local Git diff analysis, scoped unit test patch generation, approval, and regression execution.
- CI/CD Quality Center quality gate: local diff risk, patch scope, test evidence, regression evidence, and a passed/failed/needs_review decision.
- Prompt, Skill, ToolDefinition, ToolInvocation, and AI quality measurement.
- KnowledgeAdapter interface for future RAG connection.
- RAG 知识库 page surface for ContextArtifact management, KnowledgeAdapter configuration state, safety metadata, and evidence usage display.
- Final Test Knowledge RAG System: evidence-backed knowledge ingestion,
  structured TestKnowledgeCard review, hybrid retrieval, case-generation
  evidence, coverage-gap analysis, relationship-graph queries, and reviewed
  knowledge feedback.

### Out Of Scope For V1

- Multi-user collaboration, roles, permissions, departments, and enterprise audit.
- Defect lifecycle management as a Jira replacement.
- Full API testing platform parity with Postman or MeterSphere.
- Full performance testing platform parity with JMeter.
- Full mobile automation platform.
- Fiddler-level traffic capture and replay.
- Broad model leaderboard or benchmark platform before the V1 evidence loop works.
- Unapproved AI code changes to business source files.

### Final RAG Scope Promotion

The Final Test Knowledge RAG System is an approved final-product direction. It
extends the existing local-first evidence loop; it does not turn Chtest into a
generic chat knowledge base.

The final knowledge flow is:

```text
Project sources and reviewed evidence
  -> KnowledgeIngestionRun
  -> reviewable TestKnowledgeCard rows
  -> metadata + full-text + vector retrieval
  -> normalized KnowledgeEvidence
  -> evidence-backed CaseGeneration and CoverageGap review
  -> human approval
  -> execution and failure evidence
  -> reviewed KnowledgeFeedback
```

Design decisions and product reasons:

| Capability | Product decision | Why |
|---|---|---|
| Knowledge ingestion | Every import is a persisted run with parser results, counts, failures, and Artifact evidence | Test engineers need resumable imports and exact failure diagnosis instead of an opaque upload button |
| Structured cards | Documents are normalized into testing-specific, human-reviewable TestKnowledgeCard rows | Raw chunks are difficult to audit and do not express boundaries, risks, exceptions, or test strategy |
| Safety review | Only approved, safe, prompt-eligible cards can affect final generation | Dirty, stale, duplicate, or secret-bearing knowledge must never silently lower case quality |
| Hybrid retrieval | PostgreSQL metadata/full-text plus pgvector is the default local-first provider; Qdrant is optional behind KnowledgeAdapter | PostgreSQL keeps operational cost low and preserves joins/evidence locality; Qdrant remains available when corpus scale or vector operations justify a separate engine |
| Provider isolation | Haystack, LlamaIndex, Qdrant, or later providers map into Chtest KnowledgeEvidence | Provider replacement must not change Chtest cases, reports, review history, or evidence contracts |
| Evidence-backed cases | Every generated case cites knowledge, requirements, risks, generation reason, gaps, and automation readiness | A reviewer must understand why a case exists and whether its expected result is verifiable |
| Review and coverage agents | Focused agents check domain alignment, duplication, executability, verifiability, and coverage gaps before human review | Human time should be spent on product judgment, not mechanical completeness checks |
| Relationship graph | Chtest persists typed relationships between requirements, modules, APIs, risks, cases, runs, failures, and knowledge | Impact analysis and regression recommendation require relationships that flat vector similarity cannot prove |
| Feedback loop | Accepted/rejected reviews and failure evidence create proposed knowledge that requires review | Chtest should learn from project use without allowing automatic feedback to poison trusted knowledge |

The final implementation remains local-first, single-user, review-gated, and
evidence-backed. Provider runtimes are optional capabilities, not availability
requirements for core project, case, execution, or report workflows.

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

### Support Workflow: CI/CD Quality Center

```text
Local Git Diff / CI/CD Change
  -> CICDChangeAnalysisAgent
  -> UnitTestAgent
  -> UnitTestPatch Review
  -> TestRunner
  -> RegressionAgent
  -> QualityGateDecision
  -> ReportAgent
```

CI/CD Quality Center supports local code-change validation. In V1 it is a local-first support workflow, not a cloud CI/CD platform, and it does not replace the main product loop.

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
