# Slice 01: Platform Foundation Task Plan

## Goal

Create the repository and deploy skeleton required for Chtest local development.

## Source Documents

- `docs/product/01-positioning-and-scope.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/deployment/01-docker-environment.md`
- `docs/implementation/02-v1-slice-plan.md`

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Initialize repository directories | done | `find backend frontend worker deploy prompts skills mcp_tools artifacts -maxdepth 1 -type f -name .gitkeep` | `a7cd981` | Matches Task 1 acceptance |
| Add Docker Compose for PostgreSQL and Redis | done | `docker compose -f deploy/docker-compose.yml config` | `360ab7a` | - |
| Add backend container placeholder | done | `docker compose -f deploy/docker-compose.yml config` | `4160695` | - |
| Add worker container placeholder | planned | `docker compose -f deploy/docker-compose.yml config` | - | - |
| Add frontend container placeholder | planned | `docker compose -f deploy/docker-compose.yml config` | - | - |

## Task 1: Initialize Repository Directories

Goal: Create the top-level directories used by V1 implementation.

Source documents:

- `docs/implementation/02-v1-slice-plan.md`
- `docs/implementation/04-ai-vibecoding-governance.md`

Expected files/directories:

- `backend/.gitkeep`
- `frontend/.gitkeep`
- `worker/.gitkeep`
- `deploy/.gitkeep`
- `prompts/.gitkeep`
- `skills/.gitkeep`
- `mcp_tools/.gitkeep`
- `artifacts/.gitkeep`

Rule: Empty directories must include `.gitkeep` so the directory skeleton is committed.

Verification command:

```bash
find backend frontend worker deploy prompts skills mcp_tools artifacts -maxdepth 1 -type f -name .gitkeep
```

Non-goals:

- Do not implement FastAPI app.
- Do not add package dependencies.
- Do not add Docker services yet.

Commit message:

```text
chore(repo): initialize platform directories
```

## Task 2: Add Docker Compose For PostgreSQL And Redis

Goal: Add deploy Docker Compose services for PostgreSQL and Redis.

Source documents:

- `docs/deployment/01-docker-environment.md`
- `docs/implementation/04-ai-vibecoding-governance.md`

Expected files:

- `deploy/docker-compose.yml`
- `.env.example`

Verification command:

```bash
docker compose -f deploy/docker-compose.yml config
```

Non-goals:

- Do not start backend, worker, or frontend app containers yet.
- Do not add application code.

Commit message:

```text
build(deploy): add postgres and redis compose services
```

## Task 3: Add Backend Container Placeholder

Goal: Add a backend service placeholder to Docker Compose so later backend code has a stable container name and environment surface.

Source documents:

- `docs/deployment/01-docker-environment.md`
- `docs/implementation/04-ai-vibecoding-governance.md`

Expected files:

- `deploy/docker-compose.yml`
- `backend/Dockerfile`
- `backend/README.md`

Verification command:

```bash
docker compose -f deploy/docker-compose.yml config
```

Non-goals:

- Do not implement FastAPI health endpoint in this Task.
- Do not install backend dependencies beyond placeholder requirements.

Commit message:

```text
build(backend): add backend container placeholder
```

## Task 4: Add Worker Container Placeholder

Goal: Add a worker service placeholder to Docker Compose.

Source documents:

- `docs/deployment/01-docker-environment.md`
- `docs/implementation/04-ai-vibecoding-governance.md`

Expected files:

- `deploy/docker-compose.yml`
- `worker/README.md`

Verification command:

```bash
docker compose -f deploy/docker-compose.yml config
```

Non-goals:

- Do not implement Redis queue worker logic in this Task.
- Do not add AI runtime code.

Commit message:

```text
build(worker): add worker container placeholder
```

## Task 5: Add Frontend Container Placeholder

Goal: Add a frontend service placeholder to Docker Compose.

Source documents:

- `docs/deployment/01-docker-environment.md`
- `docs/implementation/04-ai-vibecoding-governance.md`

Expected files:

- `deploy/docker-compose.yml`
- `frontend/Dockerfile`
- `frontend/README.md`

Verification command:

```bash
docker compose -f deploy/docker-compose.yml config
```

Non-goals:

- Do not scaffold Vue app in this Task unless explicitly included in Slice 2 or a dedicated frontend Slice.
- Do not implement UI pages.

Commit message:

```text
build(frontend): add frontend container placeholder
```

## Slice Completion Gate

- All five Tasks are committed or explicitly documented as blocked.
- `docker compose -f deploy/docker-compose.yml config` passes.
- `memory/07-dev-log.md` and `memory/08-session-handoff.md` are updated.
- Next Slice is set to Slice 02 Backend Core.
