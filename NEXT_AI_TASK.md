# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the whole planning set.

## Current Slice

Slice 04: AI Runtime Core.

## Current Task

Task 6: Add AI Task API.

## Product Value Answer

After this task, Chtest can expose AI task status, model metadata, token usage,
context artifact ids, LLM call logs, and generated artifacts through a minimal
API for backend and frontend status views.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-04-ai-runtime-core.md`
3. `docs/contracts/02-api-contract.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/04-artifact-contract.md`
6. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Requirement review or case generation product pages.
- CI/CD Quality Center implementation docs beyond artifact owner references.
- Frontend page polish docs.
- RAG runtime, vector index, embedding, chunking, or reranking docs.
- MCP runtime integration docs.

## Expected Files

Create or update only these files for the current task:

```text
backend/app/modules/ai_runtime/service.py
backend/app/modules/ai_runtime/router.py
backend/app/modules/ai_runtime/schemas.py
backend/app/main.py
backend/app/tests/api/test_ai_tasks.py
```

Read existing ContextArtifact and Project API tests only to follow FastAPI patterns.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_ai_tasks.py -q
```

Expected result: the AI Task API focused test passes.

## Acceptance

- `GET /api/ai-tasks/{id}` returns task status, prompt/skill ids, provider/model, token usage, context artifact ids, LLM call logs, and artifact summaries.
- Minimal list API returns recent AI tasks for a project.
- API does not expose unsafe raw LLM output content; it returns artifact metadata and paths only.
- API returns `context_artifact_ids` for every task.
- No requirement review or case generation endpoints, frontend, real provider, vector index, RAG storage, or MCP runtime is added in this task.
- `git status --short` shows only expected AI Task API files before commit.

## Commit Message

```text
feat(ai-runtime): add ai task api
```

## Next Task

Slice 04 Task 7: Add AI task frontend status shell.
