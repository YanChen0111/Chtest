# Start Here For AI

This file is the shortest safe entry point for an AI coding session in Chtest.
Use it when the session needs to start implementation quickly without re-reading every planning document.

## Current Objective

Build Chtest V1 as a local-first AI testing evidence workbench for individual test engineers and automation test engineers.

The first engineering target is not broad feature coverage. It is a runnable, review-gated, evidence-backed loop that proves Chtest can connect project context, AI task records, artifacts, controlled execution, and reports.

## Required Reading

Read these files before any development work:

1. `memory/13-ai-readable-project-brief.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/00-v0.1-walking-skeleton.md`
4. `docs/implementation/02-v1-slice-plan.md`
5. `docs/implementation/04-ai-vibecoding-governance.md`

Then read task-specific contracts:

- Data/API/state work: `docs/contracts/01-data-model-contract.md`, `docs/contracts/02-api-contract.md`, `docs/contracts/03-state-machines.md`
- Artifact or evidence work: `docs/contracts/04-artifact-contract.md`
- Prompt/Skill or mock provider work: `docs/contracts/05-prompt-skill-contract.md`, `docs/contracts/08-mock-provider-contract.md`
- Golden Path work: `docs/fixtures/00-v1-demo-path.md`

## First Command

```bash
git status --short
```

If the workspace is dirty, inspect the diff before editing. Do not overwrite user changes.

## Current Recommended Development Path

1. Finish Slice 1: repository/deploy skeleton.
2. Finish Slice 2: backend core with health/ready, settings, DB, Redis, Alembic, single-user context.
3. Finish Slice 2.5 only to the frontend shell level.
4. Finish Slice 3-5 enough to support the V0.1 Walking Skeleton.
5. Run the V0.1 evidence loop before expanding into all V1 pages and metrics.

## V0.1 Evidence Loop

The first early loop is:

```text
Project
  -> ContextArtifact
  -> Mock AITask
  -> Artifact records
  -> minimal pytest execution
  -> minimal report JSON
```

This loop is defined in `docs/implementation/00-v0.1-walking-skeleton.md`.

## Forbidden Shortcuts

- Do not build RBAC, tenants, enterprise approval flows, or team management.
- Do not build RAG indexing, vector storage, or reranking in V1.
- Do not make MCP a runtime dependency before Internal Tool Adapter works.
- Do not let generated cases enter the case library without review.
- Do not execute AutomationDraft before approval.
- Do not let UnitTestPatch modify business source files.
- Do not execute arbitrary shell strings; use ToolDefinition allowlists.
- Do not mark reports as passed without evidence artifacts.
- Do not add broad dashboard or marketplace work before the V0.1 loop runs.

## Completion Rule

Every completed task must have:

- one focused verification command;
- a passing result or documented blocker;
- a small commit;
- updated handoff when the session changes slice state or discovers a significant risk.
