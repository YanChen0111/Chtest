# Slice 04: AI Runtime Core Task Plan

## Goal

Create the AI task runtime foundation: AITask, Artifact, ContextArtifact metadata, LLMCallLog, deterministic mock provider, queue worker, and task status APIs.

## Source Documents

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/08-mock-provider-contract.md`
- `docs/architecture/04-agent-workflow-design.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/slices/slice-02-frontend-foundation.md`
- `docs/product/06-frontend-ui-guidelines.md`

## Preconditions

- Slice 01, Slice 02, and Slice 03 backend tasks are complete.
- Slice 02.5 Frontend Foundation is complete before Task 7.
- If Slice 02.5 is not complete, skip Task 7 and record it as blocked in handoff instead of hand-writing an ad hoc frontend structure.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add AI runtime models and migration | done | `pytest backend/app/tests/db/test_ai_runtime_models.py -q` | pending commit | AITask, Artifact, context_artifact_ids, LLMCallLog |
| Add Artifact store service | done | `pytest backend/app/tests/artifacts/test_artifact_store.py -q` | pending commit | Atomic write and sha256 |
| Add ContextArtifact API | done | `pytest backend/app/tests/api/test_context_artifacts.py -q` | pending commit | Lightweight context input, no RAG |
| Add Mock LLM Provider | planned | `pytest backend/app/tests/ai_runtime/test_mock_provider.py -q` | - | success, provider_error, schema_invalid, timeout |
| Add AI task enqueue and worker handler | planned | `pytest backend/app/tests/ai_runtime/test_ai_task_worker.py -q` | - | fake queue acceptable |
| Add AI Task API | planned | `pytest backend/app/tests/api/test_ai_tasks.py -q` | - | GET status and artifacts |
| Add AI task frontend status shell | planned | `npm --prefix frontend run test -- --run` | - | Recent task list/detail smoke |

## Task 1: Add AI Runtime Models And Migration

Goal: Add AITask, Artifact, and LLMCallLog models matching the data contract, including `AITask.context_artifact_ids`.

Expected files:

- `backend/app/modules/ai_runtime/models.py`
- `backend/app/modules/ai_runtime/schemas.py`
- `backend/alembic/versions/<revision>_ai_runtime_core.py`
- `backend/app/tests/db/test_ai_runtime_models.py`

Verification command:

```bash
pytest backend/app/tests/db/test_ai_runtime_models.py -q
```

Non-goals:

- Do not add real LLM provider.
- Do not add PromptVersion or SkillVersion models in this Task.
- Do not add vector index or RAG storage.

Commit message:

```text
feat(ai-runtime): add ai task artifact and llm call models
```

## Task 2: Add Artifact Store Service

Goal: Add local artifact write/read service with path safety, atomic write, sha256, size, and metadata handling.

Expected files:

- `backend/app/modules/ai_runtime/artifact_store.py`
- `backend/app/modules/ai_runtime/schemas.py`
- `backend/app/tests/artifacts/test_artifact_store.py`

Verification command:

```bash
pytest backend/app/tests/artifacts/test_artifact_store.py -q
```

Non-goals:

- Do not add S3/MinIO.
- Do not expose artifact download API yet unless needed for tests.

Commit message:

```text
feat(artifact): add local artifact store
```

## Task 3: Add ContextArtifact API

Goal: Add lightweight context artifact creation and listing so AI tasks can explicitly reference user-provided documents, OpenAPI files, logs, fixtures, and bug summaries.

Expected files:

- `backend/app/modules/ai_runtime/router.py`
- `backend/app/modules/ai_runtime/service.py`
- `backend/app/modules/ai_runtime/schemas.py`
- `backend/app/tests/api/test_context_artifacts.py`

Verification command:

```bash
pytest backend/app/tests/api/test_context_artifacts.py -q
```

Non-goals:

- Do not implement file upload streaming.
- Do not implement RAG indexing, chunking, embedding, or reranking.
- Do not allow context artifacts to be used implicitly; AI task requests must pass ids explicitly.

Commit message:

```text
feat(ai-runtime): add context artifact api
```

## Task 4: Add Mock LLM Provider

Goal: Add deterministic mock provider behavior required by Golden Paths and parser tests.

Expected files:

- `backend/app/modules/ai_runtime/providers/mock_provider.py`
- `backend/app/modules/ai_runtime/providers/base.py`
- `backend/app/tests/ai_runtime/test_mock_provider.py`

Verification command:

```bash
pytest backend/app/tests/ai_runtime/test_mock_provider.py -q
```

Non-goals:

- Do not call external network.
- Do not add OpenAI-compatible provider yet.

Commit message:

```text
feat(ai-runtime): add deterministic mock provider
```

## Task 5: Add AI Task Enqueue And Worker Handler

Goal: Add AITask status progression through created, pending, running, succeeded, failed, and cancelled using a fake queue in tests.

Expected files:

- `backend/app/modules/ai_runtime/service.py`
- `backend/app/workers/handlers/ai_task_handler.py`
- `backend/app/workers/enqueue.py`
- `backend/app/tests/ai_runtime/test_ai_task_worker.py`

Verification command:

```bash
pytest backend/app/tests/ai_runtime/test_ai_task_worker.py -q
```

Non-goals:

- Do not implement real Redis worker CLI if Slice 2 did not finish Redis setup.
- Do not add business agents yet.

Commit message:

```text
feat(ai-runtime): add ai task worker handler
```

## Task 6: Add AI Task API

Goal: Add `GET /api/ai-tasks/{id}` and minimal task list API for workbench views.

Expected files:

- `backend/app/modules/ai_runtime/router.py`
- `backend/app/modules/ai_runtime/service.py`
- `backend/app/modules/ai_runtime/schemas.py`
- `backend/app/main.py`
- `backend/app/tests/api/test_ai_tasks.py`

Verification command:

```bash
pytest backend/app/tests/api/test_ai_tasks.py -q
```

Non-goals:

- Do not add requirement review or case generation endpoints.
- Do not expose unsafe raw LLM output without redaction.
- Do not hide context usage; return `context_artifact_ids` for every AI task.

Commit message:

```text
feat(ai-runtime): add ai task api
```

## Task 7: Add AI Task Frontend Status Shell

Goal: Add recent AI task list and detail shell for AI Workbench.

Precondition: Slice 02.5 Frontend Foundation is complete.

Expected files:

- `frontend/src/views/ai-workbench/AiWorkbenchView.vue`
- `frontend/src/api/aiTasks.ts`
- `frontend/src/stores/aiTasks.ts`
- `frontend/src/router/index.ts`
- `frontend/src/views/ai-workbench/AiWorkbenchView.spec.ts`

Verification command:

```bash
npm --prefix frontend run test -- --run
```

Non-goals:

- Do not implement full requirement review UI.
- Do not add charts beyond simple status counts.

Commit message:

```text
feat(frontend): add ai task status shell
```

## Slice Completion Gate

- AITask, Artifact, and LLMCallLog are persisted.
- AI task can record `context_artifact_ids` or an explicit empty list.
- Context artifacts are stored as Artifact records and do not create a RAG index.
- Mock provider supports success and failure modes.
- AI worker handler records raw, parsed, validation, and error artifacts.
- AI task API returns prompt, skill, model, status, token usage, and artifacts.
- `memory/07-dev-log.md` and `memory/08-session-handoff.md` are updated.
- Next Slice is set to Slice 05 Prompt And Skill Registry.
