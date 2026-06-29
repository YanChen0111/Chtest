# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the whole planning set.

## Current Slice

Slice 03: Project Core.

## Current Task

Task 6: Add Project Settings frontend shell.

## Product Value Answer

After this task, Chtest has the first Project Settings frontend route for viewing
and editing the project context that later AI, runner, and report workflows use.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-03-project-core.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/product/08-frontend-design-spec.md`
6. `docs/product/06-frontend-ui-guidelines.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Backend architecture deep dives.
- Open-source migration references.
- Frontend page polish docs beyond this shell task.
- CI/CD Quality Center implementation docs.
- Playwright, Newman, JMeter, Appium, traffic-capture roadmap docs.

## Expected Files

Create or update only these files for the current task:

```text
frontend/src/views/settings/ProjectSettingsView.vue
frontend/src/api/projects.ts
frontend/src/router/index.ts
frontend/src/stores/projectSettings.ts
frontend/src/views/settings/ProjectSettingsView.spec.ts
```

## Verification Command

```bash
npm --prefix frontend run test -- --run
```

Expected result: the Project Settings frontend route smoke test passes.

## Acceptance

- Project Settings route loads in the existing Vue/Arco shell.
- The route fetches `/api/projects/{id}/settings` through a typed API helper.
- The page presents project, modules, repositories, environments, and test commands in Chinese-first shell UI.
- The frontend task does not implement full page polish, drag-and-drop module editing, command execution, AI task models, ToolInvocation, or enterprise admin navigation.
- `git status --short` shows only the expected Project Settings frontend files before commit.

## Commit Message

```text
feat(frontend): add project settings shell
```

## Next Task

Slice 03 completion gate review, then prepare Slice 04 AI Runtime Core.
