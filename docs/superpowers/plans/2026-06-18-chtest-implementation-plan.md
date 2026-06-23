# Chtest V1 Implementation Plan

> Historical planning artifact from 2026-06-18. The canonical active task source
> is now `NEXT_AI_TASK.md`, with detailed task status in
> `docs/implementation/slices/` and `memory/08-session-handoff.md`.

## Batch 1: Repository And Docker Foundation

Tasks:

1. Create directories: `backend`, `frontend`, `worker`, `deploy`, `prompts`, `skills`, `mcp_tools`, `storage`, `artifacts`.
2. Add `.env.example`.
3. Add Docker Compose for PostgreSQL and Redis.
4. Add backend FastAPI health and readiness endpoints.
5. Add worker startup command and Redis ping task.
6. Add frontend Vite + Vue + Arco shell.

Verification:

- `docker compose -f deploy/docker-compose.yml up postgres redis` works.
- `GET /health` returns OK.
- `GET /ready` checks PostgreSQL and Redis.
- Frontend shell opens and calls backend health.

## Batch 2: Backend Core And Project Settings

Tasks:

1. Add config module.
2. Add SQLAlchemy session.
3. Add Alembic migration baseline.
4. Add default workspace and default user context.
5. Add Project, Module, Repository, Environment, TestCommand, ToolDefinition models.
6. Add Project Settings APIs and page.
7. Add test command validation.

Verification:

- Migration creates tables.
- Project Settings page can create project, repository, environment, and test command.
- `GET /api/projects/{id}/settings` returns the bootstrap payload.

## Batch 3: AI Runtime

Tasks:

1. Add AITask, PromptVersion, SkillVersion, Artifact models.
2. Add Prompt/Skill loader from repository files.
3. Add mock LLM provider and OpenAI-compatible provider interface.
4. Add Redis queue producer/consumer.
5. Add AI task detail page.
6. Add schema validation and raw output artifact capture.

Verification:

- A task can go `created -> pending -> running -> succeeded`.
- Prompt and Skill versions are recorded with hash.
- Schema failure saves raw output artifact and does not write business data.

## Batch 4: Requirement Review

Tasks:

1. Add Requirement, RequirementReview, RiskItem models.
2. Add RequirementReviewAgent and RiskAgent.
3. Add requirement review prompt and skill.
4. Add Requirement Review page with six-dimension score and risk matrix.

Verification:

- Requirement text produces review result and risk matrix.
- Review output is traceable to AITask, PromptVersion, SkillVersion, and artifact.

## Batch 5: Case Generation And Review

Tasks:

1. Add CaseGenerationTask and GeneratedCaseCandidate.
2. Add CaseGenerationAgent and CaseReviewAgent.
3. Add candidate table, review drawer, edit flow, reject flow, and optimize flow.
4. Add TestCase creation from approved candidate.
5. Add case quality metrics.

Verification:

- Approved candidate becomes TestCase.
- Edited candidate uses `approve_after_edit` and records edit data.
- Rejected candidate records reason.
- Metrics update after review actions.

## Batch 6: AutomationDraft And Pytest Execution

Tasks:

1. Add AutomationDraft model and APIs.
2. Add AutomationDraftAgent and `automation-draft-skill`.
3. Add Automation Draft Center page.
4. Add edit and approve flow using `edit -> edited -> approve -> approved`.
5. Add pytest TestRunner ToolDefinition and ToolInvocation.
6. Add TestRun and TestResult parser for stdout/stderr/JUnit.

Verification:

- AutomationDraft can be generated from TestCase.
- Unapproved draft cannot execute.
- Approved draft can create TestRun.
- JUnit parser creates TestResult rows.

## Batch 7: Playwright Minimal Loop

Tasks:

1. Add Playwright execution ToolDefinition.
2. Add Playwright artifact capture for trace and screenshots.
3. Add Playwright draft generation prompt constraints.
4. Extend Execution Center to display Playwright artifacts.

Verification:

- A Playwright smoke command can run through ToolInvocation.
- Trace or screenshot artifacts are linked to TestRun.

## Batch 8: Failure Analysis And Reports

Tasks:

1. Add FailureAnalysis model and FailureAnalysisAgent.
2. Add Report model and ReportAgent.
3. Add Markdown/HTML/JSON report generators.
4. Add Report Center page.
5. Add AI effectiveness metrics.

Verification:

- Failed TestRun can trigger FailureAnalysis.
- Report generated from TestRun includes evidence and metrics.
- AI quality metrics are visible.

## Batch 9: Git Quality Support Workflow

Tasks:

1. Add GitChangeSet and GitChangedFile.
2. Add local diff import and base/head analysis.
3. Add GitDiffAgent.
4. Add UnitTestPatch and scope gate.
5. Add UnitTestAgent and patch review page.
6. Add RegressionAgent and regression command selection.
7. Add Git Quality report.

Verification:

- Local diff can be imported.
- UnitTestPatch is generated and scope-validated.
- Patch cannot modify business source files.
- Approved patch can be applied and tested.
- Git quality report explains risk, test generation, regression, and final status.

## Batch 10: Extension Surfaces

Tasks:

1. Add empty KnowledgeAdapter provider.
2. Add ToolDefinition fields needed for MCP mapping.
3. Add Knowledge Integration Settings page.
4. Add Tool Adapter Center page.

Verification:

- KnowledgeAdapter returns empty evidence without breaking AI workflows.
- ToolDefinition can describe local tools and future MCP tools.
