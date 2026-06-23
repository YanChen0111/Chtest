# Chtest V0.1 Evidence Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the shortest runnable Chtest evidence loop from the current Slice 1 state to `Project -> ContextArtifact -> Mock AITask -> artifacts -> pytest -> report`.

**Architecture:** Keep V1 local-first and single-user. Build a modular FastAPI backend, PostgreSQL metadata store, Redis-backed worker surface, local artifact store, deterministic mock provider, and one minimal pytest sample repository before expanding into full V1 pages.

**Tech Stack:** FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, PostgreSQL 16, Redis 7, RQ-ready worker surface, pytest, Docker Compose, Vue 3/Vite/Arco shell.

---

## Scope

This plan covers implementation through the V0.1 Walking Skeleton only. It intentionally does not implement full Requirement Review UI, Case Review UI, Playwright, Git Quality, real LLM provider, RAG, MCP runtime, or dashboards.

Primary source documents:

- `START_HERE_FOR_AI.md`
- `NEXT_AI_TASK.md`
- `docs/implementation/00-v0.1-walking-skeleton.md`
- `docs/implementation/02-v1-slice-plan.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/05-execution-efficiency-plan.md`
- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/contracts/08-mock-provider-contract.md`

## File Structure

The implementation should keep these responsibilities stable:

- `deploy/docker-compose.yml`: local service graph and health dependencies.
- `.env.example`: container-safe defaults for Postgres, Redis, backend, and artifact root.
- `backend/app/main.py`: FastAPI app creation, router registration, `/health`, `/ready`.
- `backend/app/core/`: typed settings, DB session, Redis client, default single-user context.
- `backend/app/models/`: shared SQLAlchemy base plus Workspace/User foundation.
- `backend/app/modules/projects/`: Project, Module, Repository, Environment, TestCommand.
- `backend/app/modules/ai_runtime/`: AITask, Artifact, ContextArtifact API, LLMCallLog, mock provider.
- `backend/app/modules/prompt_skill/`: PromptVersion, SkillVersion, seed loader, hash logic.
- `backend/app/modules/executions/`: minimal TestRun, ToolInvocation, pytest execution adapter.
- `backend/app/modules/reports/`: minimal JSON report and `evidence_manifest.json`.
- `backend/app/workers/`: queue enqueue facade and handler entrypoints.
- `examples/sample-checkout-app/`: deterministic pytest target for runner smoke.
- `frontend/`: Vite/Arco shell only until the V0.1 API loop passes.
- `memory/08-session-handoff.md`: operational handoff after Slice changes, blockers, or active task changes.
- `NEXT_AI_TASK.md`: one active task, expected files, verification command, acceptance, next task.

## Execution Rules

- Start every task with `git status --short`.
- Work on one task per commit.
- Run `git diff --check` before every commit.
- Run the task-specific verification command before committing.
- Update `NEXT_AI_TASK.md` whenever the active task changes.
- Update `memory/08-session-handoff.md` when a Slice changes state, a blocker appears, or a verification cannot run.
- Do not add Git Quality, RAG, MCP runtime, real LLM provider, or broad dashboard work before V0.1 passes.

## Milestone Order

1. Finish Slice 1 platform placeholders.
2. Finish Slice 2 backend core.
3. Add a minimal frontend shell only after backend skeleton is stable.
4. Finish Slice 3 project core APIs.
5. Finish Slice 4 AI runtime core with ContextArtifact and mock provider.
6. Finish Slice 5 prompt/skill seed loading with minimal seed set.
7. Add sample checkout repository fixture.
8. Add thin TestRun and Report path.
9. Run the V0.1 smoke and update handoff.

---

## Task 1: Add Worker Container Placeholder

**Files:**

- Modify: `deploy/docker-compose.yml`
- Create: `worker/README.md`
- Update after commit: `NEXT_AI_TASK.md`

- [ ] **Step 1: Inspect current state**

Run:

```bash
git status --short
docker compose -f deploy/docker-compose.yml config
```

Expected: clean worktree before edits; Compose config renders successfully.

- [ ] **Step 2: Add worker service placeholder**

Add `worker` to `deploy/docker-compose.yml` using the backend image surface, Redis/PostgreSQL health dependencies, and artifact volume. The command should be an inert placeholder that keeps the container surface stable without implementing RQ behavior.

Required service behavior:

```text
service name: worker
build context: ../backend
depends_on: postgres healthy, redis healthy
volumes: ../artifacts:/opt/chtest/artifacts
non-goal: no RQ worker implementation
```

- [ ] **Step 3: Add worker README**

Create `worker/README.md` with these facts:

```text
# Chtest Worker

This directory is reserved for worker-specific documentation and future entrypoints.

Slice 1 only adds the Docker Compose worker placeholder. Slice 4 adds the AI task
handler surface and queue wiring. Do not implement RQ, AI runtime, or tool
execution behavior in this Slice 1 task.
```

- [ ] **Step 4: Verify**

Run:

```bash
git diff --check
docker compose -f deploy/docker-compose.yml config
```

Expected: no whitespace errors; Compose config renders successfully and includes `chtest-worker`.

- [ ] **Step 5: Commit**

Run:

```bash
git add deploy/docker-compose.yml worker/README.md
git commit -m "build(worker): add worker container placeholder"
```

- [ ] **Step 6: Update next task handoff**

Update `NEXT_AI_TASK.md` to Slice 1 Task 5: add frontend container placeholder. If only the active task changes, keep the update focused and commit it separately as:

```bash
git add NEXT_AI_TASK.md
git commit -m "docs(memory): hand off slice one frontend task"
```

---

## Task 2: Add Frontend Container Placeholder

**Files:**

- Modify: `deploy/docker-compose.yml`
- Create: `frontend/Dockerfile`
- Create: `frontend/README.md`
- Update after commit: `NEXT_AI_TASK.md`, `memory/08-session-handoff.md`, `memory/07-dev-log.md`

- [ ] **Step 1: Inspect current state**

Run:

```bash
git status --short
docker compose -f deploy/docker-compose.yml config
```

Expected: clean worktree; worker placeholder exists.

- [ ] **Step 2: Add frontend placeholder**

Add `frontend` service to Compose with stable port `5173`, build context `../frontend`, and `VITE_API_BASE_URL=http://localhost:8000`.

Create `frontend/Dockerfile` with an inert placeholder command that does not scaffold Vue yet. It should prove the image surface exists without adding app dependencies.

- [ ] **Step 3: Add frontend README**

Create `frontend/README.md` with:

```text
# Chtest Frontend

This directory is reserved for the Vue 3 + Vite + Arco frontend.

Slice 1 only defines the container placeholder and Docker Compose service.
Slice 2.5 adds the frontend app shell, router, store, API client, and smoke test.
```

- [ ] **Step 4: Verify and commit**

Run:

```bash
git diff --check
docker compose -f deploy/docker-compose.yml config
git add deploy/docker-compose.yml frontend/Dockerfile frontend/README.md
git commit -m "build(frontend): add frontend container placeholder"
```

- [ ] **Step 5: Close Slice 1**

Update:

- `docs/implementation/slices/slice-01-platform-foundation.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Next task should become Slice 2 Task 1: add FastAPI app and health endpoint.

Verification:

```bash
git diff --check
docker compose -f deploy/docker-compose.yml config
```

Commit:

```bash
git add docs/implementation/slices/slice-01-platform-foundation.md NEXT_AI_TASK.md memory/07-dev-log.md memory/08-session-handoff.md
git commit -m "docs(memory): close slice one handoff"
```

---

## Task 3: Add FastAPI Health Endpoint

**Files:**

- Create: `backend/pyproject.toml`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/tests/test_health.py`
- Modify: `backend/Dockerfile` only if needed to run the app/tests

- [ ] **Step 1: Write health test**

Create a pytest using FastAPI TestClient that asserts:

```text
GET /health returns status 200
response body includes {"status": "ok", "service": "chtest-backend"}
```

- [ ] **Step 2: Run failing test**

Run:

```bash
cd backend && uv run pytest app/tests/test_health.py -q
```

Expected: fail because the FastAPI app is not implemented yet.

- [ ] **Step 3: Add minimal app**

Implement `backend/app/main.py` with a typed app factory and `/health`. Do not add DB, Redis, auth, project APIs, or AI runtime in this task.

- [ ] **Step 4: Verify and commit**

Run:

```bash
cd backend && uv run pytest app/tests/test_health.py -q
git diff --check
git add backend/pyproject.toml backend/app/__init__.py backend/app/main.py backend/app/tests/test_health.py backend/Dockerfile
git commit -m "feat(backend): add health check endpoint"
```

---

## Task 4: Add Typed Settings

**Files:**

- Create: `backend/app/core/__init__.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/tests/test_settings.py`

- [ ] **Step 1: Write settings tests**

Cover these fields:

```text
app_env
database_url
redis_url
artifact_root
default_user_id
llm_provider
llm_model
tool_execution_mode
```

Assert defaults match `.env.example` container-safe values.

- [ ] **Step 2: Implement settings**

Use Pydantic Settings. Keep types narrow: `str`, `Path`, `UUID`, and explicit literals where useful.

- [ ] **Step 3: Verify and commit**

Run:

```bash
cd backend && uv run pytest app/tests/test_settings.py -q
git diff --check
git add backend/app/core/__init__.py backend/app/core/config.py backend/app/tests/test_settings.py
git commit -m "feat(backend): add typed settings model"
```

---

## Task 5: Add Database, Redis, Alembic, And Ready Check

**Files:**

- Create: `backend/app/core/database.py`
- Create: `backend/app/core/redis.py`
- Create: `backend/app/models/base.py`
- Create: `backend/app/models/workspace.py`
- Create: `backend/app/models/user.py`
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/versions/20260623_0001_default_workspace_user.py`
- Modify: `backend/app/main.py`
- Create: `backend/app/tests/test_ready.py`
- Create: `backend/app/tests/test_single_user.py`

- [ ] **Step 1: Add `/ready` tests with dependency overrides**

Test that `/ready` reports:

```text
postgres: ok when DB check succeeds
redis: ok when Redis ping succeeds
artifact_root: ok when path exists or can be created
status: ready only when all checks pass
```

- [ ] **Step 2: Implement DB and Redis clients**

Add SQLAlchemy engine/session factory and Redis client factory. Keep checks small and explicit.

- [ ] **Step 3: Add Workspace/User models and migration**

Create only Workspace and User foundation tables plus deterministic default records. Do not create all V1 business tables yet.

- [ ] **Step 4: Add single-user context**

Add a dependency that returns the default workspace/user ids from settings. Do not implement login, RBAC, or user switching.

- [ ] **Step 5: Verify and commit**

Run:

```bash
cd backend && uv run pytest app/tests/test_ready.py app/tests/test_single_user.py -q
cd backend && uv run alembic upgrade head
git diff --check
git add backend/app/core backend/app/models backend/alembic.ini backend/alembic backend/app/main.py backend/app/tests/test_ready.py backend/app/tests/test_single_user.py
git commit -m "feat(backend): add ready checks and single user foundation"
```

---

## Task 6: Add Minimal Frontend Shell

**Files:**

- Create: `frontend/package.json`
- Create: `frontend/index.html`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/router/index.ts`
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/views/AiWorkbenchView.vue`
- Create: `frontend/src/views/SettingsView.vue`
- Create: `frontend/src/App.spec.ts`
- Modify: `frontend/Dockerfile`

- [ ] **Step 1: Create frontend smoke test**

Test that the app renders navigation labels for:

```text
AI Workbench
Settings
```

- [ ] **Step 2: Scaffold Vue/Vite/Arco shell**

Keep the UI workbench-first: left navigation, compact top area, no landing hero, no enterprise admin pages.

- [ ] **Step 3: Verify and commit**

Run:

```bash
npm --prefix frontend install
npm --prefix frontend run test -- --run
git diff --check
git add frontend/package.json frontend/package-lock.json frontend/index.html frontend/src frontend/Dockerfile
git commit -m "feat(frontend): add workbench shell"
```

---

## Task 7: Add Project Core APIs

**Files:**

- Create: `backend/app/modules/projects/__init__.py`
- Create: `backend/app/modules/projects/models.py`
- Create: `backend/app/modules/projects/schemas.py`
- Create: `backend/app/modules/projects/service.py`
- Create: `backend/app/modules/projects/router.py`
- Create: `backend/alembic/versions/20260623_0002_project_core.py`
- Modify: `backend/app/main.py`
- Create: `backend/app/tests/api/test_projects.py`
- Create: `backend/app/tests/api/test_test_commands.py`

- [ ] **Step 1: Write API tests**

Cover:

```text
POST /api/projects
GET /api/projects/{id}/settings
POST /api/test-commands
POST /api/test-commands/{id}/validate
repository path allowlist rejection
forbidden shell operator rejection
```

- [ ] **Step 2: Implement models and APIs**

Implement Project, Module, Repository, Environment, and TestCommand fields required for V0.1.

- [ ] **Step 3: Verify and commit**

Run:

```bash
cd backend && uv run pytest app/tests/api/test_projects.py app/tests/api/test_test_commands.py -q
cd backend && uv run alembic upgrade head
git diff --check
git add backend/app/modules/projects backend/alembic/versions/20260623_0002_project_core.py backend/app/main.py backend/app/tests/api/test_projects.py backend/app/tests/api/test_test_commands.py
git commit -m "feat(projects): add project settings and test command api"
```

---

## Task 8: Add AI Runtime, ContextArtifact, And Mock Provider

**Files:**

- Create: `backend/app/modules/ai_runtime/__init__.py`
- Create: `backend/app/modules/ai_runtime/models.py`
- Create: `backend/app/modules/ai_runtime/schemas.py`
- Create: `backend/app/modules/ai_runtime/artifact_store.py`
- Create: `backend/app/modules/ai_runtime/providers/base.py`
- Create: `backend/app/modules/ai_runtime/providers/mock_provider.py`
- Create: `backend/app/modules/ai_runtime/service.py`
- Create: `backend/app/modules/ai_runtime/router.py`
- Create: `backend/app/workers/__init__.py`
- Create: `backend/app/workers/enqueue.py`
- Create: `backend/app/workers/handlers/ai_task_handler.py`
- Create: `backend/alembic/versions/20260623_0003_ai_runtime_core.py`
- Modify: `backend/app/main.py`
- Create: `backend/app/tests/api/test_context_artifacts.py`
- Create: `backend/app/tests/api/test_ai_tasks.py`
- Create: `backend/app/tests/ai_runtime/test_mock_provider.py`
- Create: `backend/app/tests/artifacts/test_artifact_store.py`

- [ ] **Step 1: Write focused tests**

Cover:

```text
ContextArtifact uses Artifact table with owner_entity_type=Project
secret scan blocks high-risk token examples
artifact write is atomic and records sha256
mock provider returns deterministic valid output
mock provider supports provider_error and schema_invalid modes
GET /api/ai-tasks/{id} returns prompt, skill, model, status, artifacts, context ids
```

- [ ] **Step 2: Implement artifact store and models**

Use local filesystem under `ARTIFACT_ROOT`. Store metadata in PostgreSQL. Do not add S3, MinIO, vector DB, or RAG indexing.

- [ ] **Step 3: Implement mock provider and worker handler**

Support only deterministic V0.1 AITask behavior:

```text
created -> pending -> running -> succeeded
created -> pending -> running -> failed
```

Always persist `input.json`, `context_manifest.json`, `raw_output.json`, `parsed_output.json`, and `schema_validation.json` when applicable.

- [ ] **Step 4: Verify and commit**

Run:

```bash
cd backend && uv run pytest app/tests/api/test_context_artifacts.py app/tests/api/test_ai_tasks.py app/tests/ai_runtime/test_mock_provider.py app/tests/artifacts/test_artifact_store.py -q
cd backend && uv run alembic upgrade head
git diff --check
git add backend/app/modules/ai_runtime backend/app/workers backend/alembic/versions/20260623_0003_ai_runtime_core.py backend/app/main.py backend/app/tests/api/test_context_artifacts.py backend/app/tests/api/test_ai_tasks.py backend/app/tests/ai_runtime/test_mock_provider.py backend/app/tests/artifacts/test_artifact_store.py
git commit -m "feat(ai-runtime): add context artifacts and mock provider"
```

---

## Task 9: Add Minimal Prompt And Skill Registry

**Files:**

- Create: `backend/app/modules/prompt_skill/__init__.py`
- Create: `backend/app/modules/prompt_skill/models.py`
- Create: `backend/app/modules/prompt_skill/schemas.py`
- Create: `backend/app/modules/prompt_skill/registry_loader.py`
- Create: `backend/app/modules/prompt_skill/router.py`
- Create: `backend/alembic/versions/20260623_0004_prompt_skill_registry.py`
- Copy seed files from `docs/fixtures/prompt-skill-seeds/` into runtime `prompts/` and `skills/`
- Create: `backend/app/tests/prompt_skill/test_registry_loader.py`
- Create: `backend/app/tests/api/test_prompt_skill_registry.py`

- [ ] **Step 1: Write loader tests**

Assert:

```text
all eight seed files load
PromptVersion has name, version, hash, input_schema_json, output_schema_json
SkillVersion has name, version, hash, quality_gates_json, forbidden_actions_json
loader is idempotent
content hash changes when content changes
```

- [ ] **Step 2: Implement loader and API**

Expose list/detail APIs only. Do not add prompt editing UI, model leaderboard, or A/B testing.

- [ ] **Step 3: Verify and commit**

Run:

```bash
cd backend && uv run pytest app/tests/prompt_skill/test_registry_loader.py app/tests/api/test_prompt_skill_registry.py -q
cd backend && uv run alembic upgrade head
git diff --check
git add backend/app/modules/prompt_skill backend/alembic/versions/20260623_0004_prompt_skill_registry.py prompts skills backend/app/tests/prompt_skill/test_registry_loader.py backend/app/tests/api/test_prompt_skill_registry.py
git commit -m "feat(prompt-skill): add minimal seed registry"
```

---

## Task 10: Add Sample Checkout App Fixture

**Files:**

- Create: `examples/sample-checkout-app/pyproject.toml`
- Create: `examples/sample-checkout-app/src/sample_checkout/__init__.py`
- Create: `examples/sample-checkout-app/src/sample_checkout/coupons.py`
- Create: `examples/sample-checkout-app/tests/test_coupons.py`
- Create: `examples/sample-checkout-app/README.md`

- [ ] **Step 1: Add deterministic coupon behavior**

Implement one pure Python function that validates coupon state:

```text
available coupon returns usable
expired coupon returns unusable with reason expired
disabled coupon returns unusable with reason disabled
used coupon returns unusable with reason already_used
coupon cannot combine with points
```

- [ ] **Step 2: Add pytest tests**

Tests must pass locally and produce useful JUnit output when called by Chtest.

- [ ] **Step 3: Verify and commit**

Run:

```bash
cd examples/sample-checkout-app && uv run pytest tests -q --junitxml=artifacts/junit.xml
git diff --check
git add examples/sample-checkout-app
git commit -m "test(fixtures): add sample checkout pytest app"
```

---

## Task 11: Add Minimal TestRun And Report Path

**Files:**

- Create: `backend/app/modules/executions/__init__.py`
- Create: `backend/app/modules/executions/models.py`
- Create: `backend/app/modules/executions/schemas.py`
- Create: `backend/app/modules/executions/pytest_runner.py`
- Create: `backend/app/modules/executions/router.py`
- Create: `backend/app/modules/reports/__init__.py`
- Create: `backend/app/modules/reports/models.py`
- Create: `backend/app/modules/reports/service.py`
- Create: `backend/app/modules/reports/router.py`
- Create: `backend/alembic/versions/20260623_0005_execution_report.py`
- Modify: `backend/app/main.py`
- Create: `backend/app/tests/executions/test_pytest_runner.py`
- Create: `backend/app/tests/api/test_test_runs.py`
- Create: `backend/app/tests/api/test_reports.py`

- [ ] **Step 1: Write runner/report tests**

Cover:

```text
approved or configured TestCommand creates TestRun
pytest command must match allowlist
runner captures stdout and stderr artifacts
runner writes parsed_result.json when JUnit parser is unavailable
report conclusion cannot be passed when evidence_manifest has missing_evidence
report JSON cites TestRun artifacts
```

- [ ] **Step 2: Implement pytest runner**

Use controlled subprocess execution only for allowlisted pytest commands. Do not accept arbitrary shell strings. Record `runner_mode`, `run_workspace`, `repository_readonly`, `network_enabled`, runtime manifest, dependency snapshot, environment snapshot, stdout, stderr, and parsed result artifacts.

- [ ] **Step 3: Implement minimal report**

Generate `report.json` and `evidence_manifest.json`. Keep Markdown/HTML rendering for full V1 after V0.1 passes.

- [ ] **Step 4: Verify and commit**

Run:

```bash
cd backend && uv run pytest app/tests/executions/test_pytest_runner.py app/tests/api/test_test_runs.py app/tests/api/test_reports.py -q
cd backend && uv run alembic upgrade head
git diff --check
git add backend/app/modules/executions backend/app/modules/reports backend/alembic/versions/20260623_0005_execution_report.py backend/app/main.py backend/app/tests/executions/test_pytest_runner.py backend/app/tests/api/test_test_runs.py backend/app/tests/api/test_reports.py
git commit -m "feat(execution): add minimal pytest run and report path"
```

---

## Task 12: Add V0.1 Walking Skeleton Smoke

**Files:**

- Create: `backend/app/tests/e2e/test_v0_1_walking_skeleton.py`
- Modify: `docs/implementation/00-v0.1-walking-skeleton.md` only if actual verified command changes
- Modify: `NEXT_AI_TASK.md`
- Modify: `memory/07-dev-log.md`
- Modify: `memory/08-session-handoff.md`

- [ ] **Step 1: Write E2E smoke**

The smoke must create or seed:

```text
default workspace/user
Checkout System project
Checkout module
Repository pointing to examples/sample-checkout-app
local Environment
pytest TestCommand
coupon-api-notes.md ContextArtifact
mock AITask using context_artifact_ids
AI task artifacts including context_manifest.json
minimal pytest TestRun
minimal automation_execution Report
evidence_manifest.json
```

- [ ] **Step 2: Verify V0.1**

Run:

```bash
cd backend && uv run pytest app/tests/e2e/test_v0_1_walking_skeleton.py -q
```

Expected:

```text
1 passed
```

- [ ] **Step 3: Run supporting checks**

Run:

```bash
docker compose -f deploy/docker-compose.yml config
git diff --check
```

Expected: Compose renders successfully; no whitespace errors.

- [ ] **Step 4: Commit smoke and handoff**

Run:

```bash
git add backend/app/tests/e2e/test_v0_1_walking_skeleton.py docs/implementation/00-v0.1-walking-skeleton.md NEXT_AI_TASK.md memory/07-dev-log.md memory/08-session-handoff.md
git commit -m "test(e2e): add v0.1 walking skeleton smoke"
```

## V0.1 Completion Gate

V0.1 is complete only when all are true:

- `/health` passes.
- `/ready` passes or documented service dependency is available through Compose.
- ContextArtifact is stored as Artifact with owner `Project`.
- Mock AITask records `context_artifact_ids`.
- AI task artifacts include `context_manifest.json`.
- pytest runner executes `examples/sample-checkout-app`.
- TestRun status comes from execution result, not AI text.
- Report has `report_type=automation_execution`.
- `evidence_manifest.json` supports the report conclusion.
- `git status --short` is clean after final commit.

## Next Plan After V0.1

After V0.1 passes, start a separate implementation plan for full V1 product workflows:

1. Requirement Review.
2. Case Generation Candidate.
3. Case Review Window.
4. AutomationDraft review and execution.
5. FailureAnalysis and richer reports.
6. Playwright minimal loop.
7. Git Quality support workflow.

Do not start these before the V0.1 smoke has a passing command and handoff evidence.
