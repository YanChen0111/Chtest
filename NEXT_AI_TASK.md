# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the whole planning set.

## Current Slice

Slice 02.5: Frontend Foundation.

## Current Task

Task 2: Add Arco, router, store, and API shell.

## Product Value Answer

After this task, Chtest has a reusable Chinese-first workbench shell with
navigation, routing, state, and an API client base so later pages can be added
without inventing frontend structure again.

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
frontend/package-lock.json
frontend/package.json
frontend/src/main.ts
frontend/src/App.vue
frontend/src/api/client.ts
frontend/src/layouts/WorkbenchLayout.vue
frontend/src/layouts/WorkbenchLayout.spec.ts
frontend/src/router/index.ts
frontend/src/stores/index.ts
frontend/src/styles/global.css
frontend/src/views/ai-workbench/AiWorkbenchView.vue
```

## Verification Command

```bash
npm --prefix frontend run test -- --run
```

Expected result: Vitest runs the frontend shell tests successfully.

## Acceptance

- Arco Design Vue, Vue Router, Pinia, and the API client shell are wired.
- The main layout shows Chinese-first navigation labels.
- The initial AI 工作台 page uses Chinese visible copy and no marketing landing page.
- No Project Settings forms, business APIs, or execution flows are added in this task.
- `git status --short` shows only the expected frontend shell files before commit.

## Commit Message

```text
feat(frontend): add workbench shell
```

## Next Task

Slice 02.5 Task 3: Add frontend Docker dev command.
