# Slice 02: Backend Core Task Plan

## Goal

Create the minimal FastAPI backend foundation: settings, health, ready checks, database session, Redis client, Alembic skeleton, and default single-user context.

## Source Documents

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/architecture/03-implementation-technology.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/deployment/01-docker-environment.md`

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add FastAPI app and health endpoint | planned | `cd backend && uv run pytest app/tests/test_health.py -q` | - | - |
| Add settings model | planned | `cd backend && uv run pytest app/tests/test_settings.py -q` | - | - |
| Add database session and ready check | planned | `cd backend && uv run pytest app/tests/test_ready.py -q` | - | - |
| Add Redis client and ready check | planned | `cd backend && uv run pytest app/tests/test_ready.py -q` | - | - |
| Add Alembic skeleton and default workspace/user migration | planned | `cd backend && uv run alembic upgrade head` in test database or documented smoke | - | - |
| Add default single-user context dependency | planned | `cd backend && uv run pytest app/tests/test_single_user.py -q` | - | - |

## Task 1: Add FastAPI App And Health Endpoint

Goal: Add a minimal FastAPI application with `/health` endpoint.

Source documents:

- `docs/architecture/03-implementation-technology.md`
- `docs/implementation/04-ai-vibecoding-governance.md`

Expected files:

- `backend/app/main.py`
- `backend/app/tests/test_health.py`
- `backend/pyproject.toml`

Verification command:

```bash
cd backend && uv run pytest app/tests/test_health.py -q
```

Non-goals:

- Do not add database connection.
- Do not add auth.
- Do not add project APIs.

Commit message:

```text
feat(backend): add health check endpoint
```

## Task 2: Add Settings Model

Goal: Add typed backend settings for app, database, Redis, artifact root, and mock provider defaults.

Source documents:

- `docs/architecture/03-implementation-technology.md`
- `docs/deployment/01-docker-environment.md`

Expected files:

- `backend/app/core/config.py`
- `backend/app/tests/test_settings.py`

Verification command:

```bash
cd backend && uv run pytest app/tests/test_settings.py -q
```

Non-goals:

- Do not open database connections.
- Do not read secrets from prompt or docs.

Commit message:

```text
feat(backend): add typed settings model
```

## Task 3: Add Database Session And Ready Check

Goal: Add SQLAlchemy session factory and include database connectivity in `/ready`.

Source documents:

- `docs/contracts/01-data-model-contract.md`
- `docs/architecture/03-implementation-technology.md`

Expected files:

- `backend/app/db/session.py`
- `backend/app/main.py`
- `backend/app/tests/test_ready.py`

Verification command:

```bash
cd backend && uv run pytest app/tests/test_ready.py -q
```

Non-goals:

- Do not create all business tables.
- Do not add project CRUD APIs.

Commit message:

```text
feat(backend): add database ready check
```

## Task 4: Add Redis Client And Ready Check

Goal: Add Redis client factory and include Redis connectivity in `/ready`.

Source documents:

- `docs/architecture/03-implementation-technology.md`
- `docs/deployment/01-docker-environment.md`

Expected files:

- `backend/app/core/redis.py`
- `backend/app/main.py`
- `backend/app/tests/test_ready.py`

Verification command:

```bash
cd backend && uv run pytest app/tests/test_ready.py -q
```

Non-goals:

- Do not implement RQ worker jobs.
- Do not add AI task queue logic.

Commit message:

```text
feat(backend): add redis ready check
```

## Task 5: Add Alembic Skeleton And Default Workspace/User Migration

Goal: Add Alembic migration skeleton and create default workspace/user tables or seed migration according to the data model contract.

Source documents:

- `docs/contracts/01-data-model-contract.md`
- `docs/implementation/04-ai-vibecoding-governance.md`

Expected files:

- `backend/alembic.ini`
- `backend/alembic/env.py`
- `backend/alembic/versions/<revision>_default_workspace_user.py`
- `backend/app/models/base.py`
- `backend/app/models/workspace.py`
- `backend/app/models/user.py`

Verification command:

```bash
cd backend && uv run alembic upgrade head
```

If a test database is not ready yet, document the smoke command in handoff and add the minimal missing setup as the next Task.

Non-goals:

- Do not create all V1 tables in this Task.
- Do not add authentication.

Commit message:

```text
feat(db): add default workspace and user migration
```

## Task 6: Add Default Single-User Context Dependency

Goal: Add backend dependency that returns default workspace/user context for V1 APIs.

Source documents:

- `docs/contracts/01-data-model-contract.md`
- `memory/04-project-constraints.md`

Expected files:

- `backend/app/core/context.py`
- `backend/app/tests/test_single_user.py`

Verification command:

```bash
cd backend && uv run pytest app/tests/test_single_user.py -q
```

Non-goals:

- Do not add login.
- Do not add RBAC.
- Do not add multi-user switching.

Commit message:

```text
feat(backend): add single user context dependency
```

## Slice Completion Gate

- All six Tasks are committed or explicitly documented as blocked.
- `/health` and `/ready` tests pass.
- Settings, DB session, Redis client, Alembic skeleton, and single-user context exist.
- `memory/07-dev-log.md` and `memory/08-session-handoff.md` are updated.
- Next Slice is set to Slice 03 Project Core.
