# Slice 23: Frontend Build Baseline Task Plan

## Goal

Restore the frontend build gate after V2 frontend growth.

This slice is an engineering-quality slice, not a product-feature slice. It
turns the currently failing `npm --prefix frontend run build` command back into
a reliable verification gate while preserving existing runtime behavior and
frontend tests.

## Source Documents

- `docs/product/01-positioning-and-scope.md`
- `docs/contracts/02-api-contract.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/10-v2-scope-options.md`
- `memory/08-session-handoff.md`

## Product Value Answer

After this slice, frontend changes can be verified with both Vitest and the
production build. This gives future AI coding sessions a stronger regression
gate before they add or modify frontend workbench surfaces.

## Observed Build Failures

The current command:

```bash
npm --prefix frontend run build
```

fails during `vue-tsc --noEmit` with three narrow groups:

- API request interfaces do not satisfy `Record<string, unknown>` constraints in
  `postJson` calls:
  - `src/api/automation.ts`
  - `src/api/cases.ts`
  - `src/api/cicd.ts`
  - `src/api/execution.ts`
  - `src/api/reporting.ts`
  - `src/api/requirements.ts`
- `String.prototype.replaceAll` is used while the frontend TypeScript target
  does not include ES2021:
  - `src/views/ai-workbench/AiWorkbenchView.vue`
  - `src/views/requirements/RequirementReviewView.vue`
- `CicdQualityCenterView.vue` passes a `string | undefined` where a `string` is
  required.

## Non-goals

- No product behavior changes.
- No new pages, navigation entries, backend APIs, database migrations, runners,
  RAG runtime, MCP runtime, CI provider controls, RBAC, tenants, permissions, or
  marketplace work.
- No frontend redesign, layout overhaul, design-system rewrite, theme work, or
  copy changes unless required by type safety.
- No dependency/package upgrade unless the build failure cannot be fixed with
  narrow source changes.
- No broad lint/style cleanup, formatting churn, or unrelated refactors.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Frontend Build Baseline task plan | done | `test -f docs/implementation/slices/slice-23-frontend-build-baseline.md && rg -n "Frontend Build Baseline|npm --prefix frontend run build|TypeScript|Non-goals|Task Table" docs/implementation/slices/slice-23-frontend-build-baseline.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md` | pending | planning-only scope |
| Fix frontend build TypeScript baseline | planned | `npm --prefix frontend run build && npm --prefix frontend run test -- --run && git diff --check` | pending | narrow type fixes |
| Slice 23 completion gate | planned | `npm --prefix frontend run build && npm --prefix frontend run test -- --run && git diff --check` | pending | docs and handoff |

## Task 1: Add Frontend Build Baseline Task Plan

Goal: Define the exact build-baseline slice before editing frontend code.

Expected files:

- `docs/implementation/slices/slice-23-frontend-build-baseline.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-23-frontend-build-baseline.md
rg -n "Frontend Build Baseline|npm --prefix frontend run build|TypeScript|Non-goals|Task Table" docs/implementation/slices/slice-23-frontend-build-baseline.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Creates the Slice 23 plan.
- Documents the observed build failure groups.
- Defines product value, non-goals, task table, expected files, verification
  commands, and commit messages.
- Does not add product code, frontend code, backend code, package upgrades, or
  tests.

Commit message:

```text
docs(v2): add frontend build baseline plan
```

## Task 2: Fix Frontend Build TypeScript Baseline

Goal: Make the current frontend build command pass with minimal type fixes.

Expected files:

- `frontend/src/api/client.ts`
- `frontend/src/api/automation.ts`
- `frontend/src/api/cases.ts`
- `frontend/src/api/cicd.ts`
- `frontend/src/api/execution.ts`
- `frontend/src/api/reporting.ts`
- `frontend/src/api/requirements.ts`
- `frontend/src/views/ai-workbench/AiWorkbenchView.vue`
- `frontend/src/views/cicd/CicdQualityCenterView.vue`
- `frontend/src/views/requirements/RequirementReviewView.vue`
- `frontend/tsconfig*.json` only if replacing `replaceAll` locally is worse
  than aligning TypeScript lib settings
- `docs/implementation/slices/slice-23-frontend-build-baseline.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
npm --prefix frontend run build
npm --prefix frontend run test -- --run
git diff --check
```

Acceptance:

- `npm --prefix frontend run build` passes.
- Full frontend Vitest suite still passes.
- Type fixes are narrow and preserve existing request payloads, visible text,
  routes, and page behavior.
- Does not add product features, package upgrades, backend code, migrations, or
  broad refactors.

Commit message:

```text
fix(frontend): restore build baseline
```

## Slice 23 Completion Gate

Goal: Close the frontend build baseline slice and hand off to the next V2 task.

Expected files:

- `docs/implementation/slices/slice-23-frontend-build-baseline.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
npm --prefix frontend run build
npm --prefix frontend run test -- --run
git diff --check
```

Acceptance:

- Task rows are marked done with commit ids.
- Completion evidence records build, frontend tests, and diff verification.
- Handoff names the next V2 slice or planning task.

Commit message:

```text
docs(v2): complete frontend build baseline slice
```
