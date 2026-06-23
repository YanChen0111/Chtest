# Execution Efficiency Plan

## 1. Purpose

This plan reduces Chtest vibecoding overhead. The project already has strong
product and contract documents; the next risk is spending too much AI time
rereading planning material instead of shipping the runnable evidence loop.

The goal is a faster loop:

```text
NEXT_AI_TASK
  -> task-specific docs only
  -> one focused edit set
  -> one verification command
  -> one small commit
  -> handoff update when needed
```

## 2. Current Efficiency Problems

- The full recommended reading order is useful for onboarding but too heavy for
  every implementation session.
- Fixtures explain product paths, but real tester scenarios were not explicit.
- Prompt and Skill behavior existed as a contract, but not as seed files that an
  AI worker can load or test.
- Some future AI sessions may expand into dashboards, Git Quality, RAG, or MCP
  before the V0.1 evidence loop runs.

## 3. Optimization Decisions

### 3.1 Add Real User Scenario Samples

Use `docs/fixtures/04-real-user-scenarios.md` to keep implementation decisions
anchored in three real user jobs:

- API test engineer: requirement to API cases and pytest evidence.
- Web automation engineer: reviewed case to Playwright evidence.
- Backend engineer: Git diff to scoped unit test patch and regression evidence.

These scenarios are fixtures, not new scope. They clarify why the existing loops
matter.

### 3.2 Add Prompt/Skill Seed Fixtures

Use `docs/fixtures/05-minimal-prompt-skill-seeds.md` and
`docs/fixtures/prompt-skill-seeds/` as the concrete starting point for Slice 5.

Slice 5 should load these seed files before adding prompt editing screens,
marketplace concepts, or advanced model comparison.

### 3.3 Add `NEXT_AI_TASK.md`

`NEXT_AI_TASK.md` is the active short handoff. It must name:

- current Slice;
- current Task;
- product value answer;
- must-read docs;
- docs not to read unless needed;
- expected files;
- verification command;
- acceptance;
- commit message;
- next task.

If `NEXT_AI_TASK.md` conflicts with contracts or product scope, contracts and
product scope win. Update `NEXT_AI_TASK.md` after the current task changes.

### 3.4 Add A Minimal Sample Repository Before Runner Smoke

The V0.1 and V1 evidence loops require a real pytest target. Before starting
the TestRunner smoke, ensure there is a minimal sample repository fixture such
as `examples/sample-checkout-app`, or an equivalent allowlisted local repository,
with a deterministic coupon validation function and `tests/` directory.

This fixture is not a new product feature. It exists so AI sessions can verify
runner, artifact, report, and evidence behavior without depending on an
uncontrolled external project.

## 4. AI Session Rules

- Start from `START_HERE_FOR_AI.md`, then read `NEXT_AI_TASK.md`.
- Work on only one task unless the user explicitly expands scope.
- Do not read broad architecture, reference, or roadmap docs unless the task
  names them.
- Every task must have one primary verification command before editing starts.
- If no verification command exists, the first task is to create a smoke check.
- Stop after two or three failed repair attempts and write a failure handoff.
- Do not start V0.1 runner smoke until the sample repository path and pytest
  TestCommand are defined and allowlisted.
- Do not add UI, dashboard, RAG, MCP, or Git Quality breadth unless the active
  task moves the V0.1 or V1 evidence loop forward.

## 5. Documentation Routing

| Work Type | Read |
|---|---|
| Any session | `START_HERE_FOR_AI.md`, `NEXT_AI_TASK.md` |
| Current task | named Slice task file |
| Backend model/API/state work | `docs/contracts/01-data-model-contract.md`, `docs/contracts/02-api-contract.md`, `docs/contracts/03-state-machines.md` |
| Artifact/evidence work | `docs/contracts/04-artifact-contract.md` |
| Prompt/Skill/mock provider work | `docs/contracts/05-prompt-skill-contract.md`, `docs/contracts/08-mock-provider-contract.md`, `docs/fixtures/05-minimal-prompt-skill-seeds.md` |
| User scenario or demo fixture work | `docs/fixtures/00-v1-demo-path.md`, `docs/fixtures/04-real-user-scenarios.md` |
| Frontend page work | `docs/product/06-frontend-ui-guidelines.md` plus the relevant API contract |

## 6. Completion Gate

A task is complete only when:

- the focused verification command has been run;
- the result is passing or a blocker is documented;
- the diff is reviewed with `git diff --check` and `git diff --name-only`;
- the task has a small commit, unless the user explicitly asks not to commit;
- `NEXT_AI_TASK.md` is updated when the active task changes;
- `memory/08-session-handoff.md` is updated when slice state, risk, or blocker
  changes.
