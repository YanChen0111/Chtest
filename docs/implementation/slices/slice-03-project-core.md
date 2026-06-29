# Slice 03: Project Core Task Plan

## Goal

Create the single-user project context needed by all later AI, execution, and report workflows.

## Source Documents

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/architecture/03-implementation-technology.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/slices/slice-02-frontend-foundation.md`
- `docs/product/06-frontend-ui-guidelines.md`
- `memory/13-ai-readable-project-brief.md`

## Preconditions

- Slice 01 and Slice 02 are complete.
- Slice 02.5 Frontend Foundation is complete before Task 6.
- If Slice 02.5 is not complete, skip Task 6 and record it as blocked in handoff instead of hand-writing an ad hoc frontend structure.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Project Core models and migration | done | `UV_CACHE_DIR=.tmp/uv-cache uv --project backend run pytest backend/app/tests/db/test_project_core_models.py -q` | pending commit | Added backend model foundation because Slice 2 backend DB baseline was still placeholder-only |
| Add Project CRUD API | done | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_projects.py -q` | pending commit | Includes settings bootstrap response |
| Add Module tree API | done | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_modules.py -q` | pending commit | Enforce five-level limit |
| Add Repository and Environment API | done | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_repository_environment.py -q` | pending commit | Repository path allowlist required |
| Add TestCommand API and validation | planned | `pytest backend/app/tests/api/test_test_commands.py -q` | - | Command safety rules required |
| Add Project Settings frontend shell | planned | `npm --prefix frontend run test -- --run` | - | Basic route and API client smoke |

## Task 1: Add Project Core Models And Migration

Goal: Add SQLAlchemy models and migration for Project, Module, Repository, Environment, and TestCommand.

Expected files:

- `backend/app/modules/projects/models.py`
- `backend/app/modules/projects/schemas.py`
- `backend/app/modules/projects/service.py`
- `backend/alembic/versions/<revision>_project_core.py`
- `backend/app/tests/db/test_project_core_models.py`

Verification command:

```bash
pytest backend/app/tests/db/test_project_core_models.py -q
```

Non-goals:

- Do not implement AI task models.
- Do not implement ToolInvocation.
- Do not add multi-user permissions.

Commit message:

```text
feat(projects): add project core models
```

## Task 2: Add Project CRUD API

Goal: Add Project create/read/update APIs and Project Settings bootstrap response.

Expected files:

- `backend/app/modules/projects/router.py`
- `backend/app/modules/projects/service.py`
- `backend/app/modules/projects/schemas.py`
- `backend/app/main.py`
- `backend/app/tests/api/test_projects.py`

Verification command:

```bash
pytest backend/app/tests/api/test_projects.py -q
```

Non-goals:

- Do not implement frontend in this Task.
- Do not create repository or command validation in this Task.

Commit message:

```text
feat(projects): add project settings api
```

## Task 3: Add Module Tree API

Goal: Add module create/list/update behavior with level, parent, path, and five-level validation.

Expected files:

- `backend/app/modules/projects/router.py`
- `backend/app/modules/projects/service.py`
- `backend/app/modules/projects/schemas.py`
- `backend/app/tests/api/test_modules.py`

Verification command:

```bash
pytest backend/app/tests/api/test_modules.py -q
```

Non-goals:

- Do not add drag-and-drop UI.
- Do not support more than five levels.

Commit message:

```text
feat(projects): add module tree api
```

## Task 4: Add Repository And Environment API

Goal: Add Repository and Environment create/update/list APIs with repository path safety validation.

Expected files:

- `backend/app/modules/projects/router.py`
- `backend/app/modules/projects/service.py`
- `backend/app/modules/projects/schemas.py`
- `backend/app/tests/api/test_repository_environment.py`

Verification command:

```bash
pytest backend/app/tests/api/test_repository_environment.py -q
```

Non-goals:

- Do not run git commands yet.
- Do not store raw secrets in Environment variables.

Commit message:

```text
feat(projects): add repository and environment api
```

## Task 5: Add TestCommand API And Validation

Goal: Add TestCommand create/update/validate APIs with allowlist, working directory, and forbidden shell operator checks.

Expected files:

- `backend/app/modules/projects/router.py`
- `backend/app/modules/projects/service.py`
- `backend/app/modules/projects/schemas.py`
- `backend/app/tests/api/test_test_commands.py`

Verification command:

```bash
pytest backend/app/tests/api/test_test_commands.py -q
```

Non-goals:

- Do not execute commands in this Slice.
- Do not implement ToolInvocation.

Commit message:

```text
feat(projects): add test command validation
```

## Task 6: Add Project Settings Frontend Shell

Goal: Add the first frontend route for viewing and editing Project Settings.

Precondition: Slice 02.5 Frontend Foundation is complete.

Expected files:

- `frontend/src/views/settings/ProjectSettingsView.vue`
- `frontend/src/api/projects.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/projectSettings.ts`
- `frontend/src/views/settings/ProjectSettingsView.spec.ts`

Verification command:

```bash
npm --prefix frontend run test -- --run
```

Non-goals:

- Do not implement all page polish.
- Do not add enterprise admin navigation.

Commit message:

```text
feat(frontend): add project settings shell
```

## Slice Completion Gate

- Project settings API returns project, modules, repositories, environments, test commands, and tool definitions.
- Repository paths are rejected when outside configured allowlisted roots.
- TestCommand validation rejects forbidden shell operators.
- Frontend Project Settings route loads with API client smoke.
- `memory/07-dev-log.md` and `memory/08-session-handoff.md` are updated.
- Next Slice is set to Slice 04 AI Runtime Core.
