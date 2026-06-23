# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the whole planning set.

## Current Slice

Slice 1: Repository and Deploy Skeleton.

## Current Task

Task 3: Add backend container placeholder.

## Product Value Answer

After this task, Chtest has a stable backend service surface in Docker Compose
so Slice 2 can add the FastAPI app without changing container names or basic
environment wiring.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-01-platform-foundation.md`
3. `docs/implementation/04-ai-vibecoding-governance.md`
4. `docs/implementation/05-execution-efficiency-plan.md`
5. `docs/deployment/01-docker-environment.md`

## Do Not Read Unless Needed

- Full PRD and page PRD files.
- Architecture deep dives.
- Open-source migration references.
- Git Quality docs.
- Playwright, Newman, JMeter, Appium, traffic-capture roadmap docs.

## Expected Files

Create or update only these files for the current task:

```text
deploy/docker-compose.yml
backend/Dockerfile
backend/README.md
```

## Verification Command

```bash
docker compose -f deploy/docker-compose.yml config
```

Expected result: Docker Compose renders a valid configuration without errors.

## Acceptance

- `deploy/docker-compose.yml` includes a backend service placeholder.
- The backend service has a stable service name and port surface for later `/health`.
- `backend/Dockerfile` and `backend/README.md` exist.
- No FastAPI app, backend dependencies, worker logic, database schema, AI runtime, or UI behavior is added in this task.
- `git status --short` shows only the expected backend placeholder files and compose update before commit.

## Commit Message

```text
build(backend): add backend container placeholder
```

## Next Task

Slice 1 Task 4: Add worker container placeholder.
