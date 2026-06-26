# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the whole planning set.

## Current Slice

Slice 03: Project Core.

## Current Task

Task 1: Add Project Core models and migration.

## Product Value Answer

After this task, Chtest has persistent project context records for project,
module, repository, environment, and test command, which unlocks every later
AI, execution, and report workflow.

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
- CI/CD Management implementation docs.
- Playwright, Newman, JMeter, Appium, traffic-capture roadmap docs.

## Expected Files

Create or update only these files for the current task:

```text
backend/app/modules/projects/models.py
backend/app/modules/projects/schemas.py
backend/app/modules/projects/service.py
backend/alembic/versions/<revision>_project_core.py
backend/app/tests/db/test_project_core_models.py
```

## Verification Command

```bash
pytest backend/app/tests/db/test_project_core_models.py -q
```

Expected result: the new project core model test passes.

## Acceptance

- SQLAlchemy models exist for Project, Module, Repository, Environment, and TestCommand.
- The migration creates the project core tables with the contract fields needed by later slices.
- Workspace/User ownership assumptions remain single-user V1 only.
- No AI task models, ToolInvocation, or multi-user permissions are added in this task.
- `git status --short` shows only the expected backend model, migration, and test files before commit.

## Commit Message

```text
feat(projects): add project core models
```

## Next Task

Slice 03 Task 2: add project settings api.
