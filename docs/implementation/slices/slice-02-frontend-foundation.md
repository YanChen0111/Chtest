# Slice 02.5: Frontend Foundation Task Plan

## Goal

Create the Vue 3 + TypeScript + Vite + Arco Design Vue frontend foundation required before Slice 3 frontend pages.

The visible frontend copy in this slice must be Chinese-first. Navigation labels, page titles, buttons, table headers, empty states, and status text should use Chinese terms such as `AI 工作台`, `需求评审`, `上下文工件`, `AI 任务`, `大模型调用日志`, and `工件`.

## Source Documents

- `docs/product/06-frontend-ui-guidelines.md`
- `docs/architecture/03-implementation-technology.md`
- `docs/deployment/01-docker-environment.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/02-v1-slice-plan.md`

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Scaffold Vue Vite app | planned | `npm --prefix frontend run build` | - | Vue 3 + TypeScript |
| Add Arco, router, store, and API shell | planned | `npm --prefix frontend run test -- --run` | - | Minimal workbench shell, Chinese UI copy |
| Add frontend Docker dev command | planned | `docker compose -f deploy/docker-compose.yml config` | - | Align with deploy docs |
| Add frontend health/API smoke | planned | `npm --prefix frontend run test -- --run` | - | API base URL and health probe |

## Task 1: Scaffold Vue Vite App

Goal: Create the frontend app foundation with Vue 3, TypeScript, Vite, and Vitest.

Expected files:

- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/index.html`
- `frontend/vite.config.ts`
- `frontend/tsconfig.json`
- `frontend/src/main.ts`
- `frontend/src/App.vue`
- `frontend/src/env.d.ts`
- `frontend/src/App.spec.ts`

Verification command:

```bash
npm --prefix frontend run build
```

Non-goals:

- Do not implement business pages.
- Do not add marketing or landing pages.

Commit message:

```text
feat(frontend): scaffold vue workbench app
```

## Task 2: Add Arco Router Store And API Shell

Goal: Add the shared frontend shell used by Slice 3-5 pages, with Chinese-first visible labels.

Expected files:

- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`
- `frontend/src/api/client.ts`
- `frontend/src/layouts/WorkbenchLayout.vue`
- `frontend/src/views/ai-workbench/AiWorkbenchView.vue`
- `frontend/src/styles/global.css`
- `frontend/src/layouts/WorkbenchLayout.spec.ts`

Verification command:

```bash
npm --prefix frontend run test -- --run
```

Non-goals:

- Do not implement Project Settings forms.
- Do not add enterprise navigation.
- Do not implement charts beyond simple placeholder status counts.

Commit message:

```text
feat(frontend): add workbench shell
```

## Task 3: Add Frontend Docker Dev Command

Goal: Make the frontend container run the Vite dev server consistently through Docker Compose.

Expected files:

- `frontend/Dockerfile`
- `frontend/README.md`
- `deploy/docker-compose.yml`

Verification command:

```bash
docker compose -f deploy/docker-compose.yml config
```

Non-goals:

- Do not add production nginx packaging.
- Do not add CI deployment.

Commit message:

```text
build(frontend): wire vite dev container
```

## Task 4: Add Frontend Health And API Smoke

Goal: Add a minimal health probe from frontend API client to backend `/health`.

Expected files:

- `frontend/src/api/health.ts`
- `frontend/src/views/ai-workbench/AiWorkbenchView.vue`
- `frontend/src/views/ai-workbench/AiWorkbenchView.spec.ts`

Verification command:

```bash
npm --prefix frontend run test -- --run
```

Non-goals:

- Do not require backend to be running in unit tests.
- Do not add full E2E Playwright frontend tests yet.

Commit message:

```text
feat(frontend): add health probe smoke
```

## Slice Completion Gate

- `npm --prefix frontend run build` passes.
- `npm --prefix frontend run test -- --run` passes.
- `docker compose -f deploy/docker-compose.yml config` passes.
- Frontend uses Vue 3, TypeScript, Vite, Arco Design Vue, router, store, and API client shell.
- Navigation follows `docs/product/06-frontend-ui-guidelines.md`.
- Next Slice is set to Slice 03 Project Core.
