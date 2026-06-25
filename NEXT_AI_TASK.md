# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the whole planning set.

## Current Slice

Slice 02.5: Frontend Foundation.

## Current Task

Task 3: Add frontend Docker dev command.

## Product Value Answer

After this task, Chtest frontend can run through Docker Compose with a stable
dev command, so later frontend work does not depend on ad hoc local startup.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-02-frontend-foundation.md`
3. `docs/deployment/01-docker-environment.md`
4. `docs/product/06-frontend-ui-guidelines.md`
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
frontend/Dockerfile
frontend/README.md
deploy/docker-compose.yml
```

## Verification Command

```bash
docker compose -f deploy/docker-compose.yml config
```

Expected result: Docker Compose renders the frontend service without errors.

## Acceptance

- `deploy/docker-compose.yml` includes a frontend service for the Vite dev server.
- The frontend container command aligns with the documented local dev flow.
- No production nginx packaging or CI deployment is added in this task.
- `git status --short` shows only the expected Docker/frontend container files before commit.

## Commit Message

```text
build(frontend): wire vite dev container
```

## Next Task

Slice 02.5 Task 4: Add frontend health and API smoke.
