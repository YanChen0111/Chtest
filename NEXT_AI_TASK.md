# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the whole planning set.

## Current Slice

Slice 03: Project Core.

## Current Task

Task 3: Add Module tree API.

## Product Value Answer

After this task, Chtest can organize a project's testing scope into a bounded
module tree that later requirement, case, automation, and report workflows can
reference consistently.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-03-project-core.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Backend architecture deep dives.
- Open-source migration references.
- Frontend page polish docs beyond shell level.
- CI/CD Quality Center implementation docs.
- Playwright, Newman, JMeter, Appium, traffic-capture roadmap docs.

## Expected Files

Create or update only these files for the current task:

```text
backend/app/modules/projects/service.py
backend/app/modules/projects/schemas.py
backend/app/modules/projects/router.py
backend/app/main.py
backend/app/tests/api/test_modules.py
```

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_modules.py -q
```

Expected result: the new Module tree API test passes.

## Acceptance

- Module create/list/update APIs follow `docs/contracts/02-api-contract.md` and Slice 03 Task 3.
- Root modules have `level=1`, child modules derive `level`, `parent_id`, and `path` from their parent.
- The five-level module tree limit is enforced.
- Module names remain unique under the same parent.
- No repository path validation, environment mutation API, TestCommand validation, AI task models, ToolInvocation, frontend, or multi-user permissions are added in this task.
- `git status --short` shows only the expected Module API files before commit.

## Commit Message

```text
feat(projects): add module tree api
```

## Next Task

Slice 03 Task 4: add repository and environment api.
