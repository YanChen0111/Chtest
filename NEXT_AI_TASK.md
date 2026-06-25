# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the whole planning set.

## Current Slice

Slice 02.5: Frontend Foundation.

## Current Task

Task 1: Scaffold Vue Vite app.

## Product Value Answer

After this task, Chtest has a real frontend application skeleton that future AI
coding sessions can extend without redoing the build tooling, TypeScript
baseline, or app entry structure.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-02-frontend-foundation.md`
3. `docs/product/06-frontend-ui-guidelines.md`
4. `docs/product/03-user-journey-and-page-prd.md`
5. `docs/implementation/04-ai-vibecoding-governance.md`
6. `docs/implementation/05-execution-efficiency-plan.md`

## Do Not Read Unless Needed

- Backend architecture deep dives.
- Open-source migration references.
- Git Quality implementation docs.
- Playwright, Newman, JMeter, Appium, traffic-capture roadmap docs.

## Expected Files

Create or update only these files for the current task:

```text
frontend/package.json
frontend/package-lock.json
frontend/index.html
frontend/vite.config.ts
frontend/tsconfig.json
frontend/src/main.ts
frontend/src/App.vue
frontend/src/env.d.ts
frontend/src/App.spec.ts
```

## Verification Command

```bash
npm --prefix frontend run build
```

Expected result: Vite builds the frontend application successfully.

## Acceptance

- `frontend` contains a working Vue 3 + TypeScript + Vite scaffold.
- The scaffold is ready for Chinese-first UI copy and Arco Design Vue shell work.
- No backend APIs, business pages, or execution flows are added in this task.
- `git status --short` shows only the expected frontend scaffold files before commit.

## Commit Message

```text
feat(frontend): scaffold vue workbench app
```

## Next Task

Slice 02.5 Task 2: Add Arco, router, store, and API shell.
