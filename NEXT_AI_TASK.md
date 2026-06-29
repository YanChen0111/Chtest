# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the whole planning set.

## Current Slice

Slice 04: AI Runtime Core.

## Current Task

Task 5: Add AI Task Enqueue And Worker Handler.

## Product Value Answer

After this task, Chtest can enqueue an AI task into a local fake queue and run a
worker handler that records deterministic mock provider artifacts and status
progression without Redis or real LLM calls.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-04-ai-runtime-core.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/03-state-machines.md`
5. `docs/contracts/04-artifact-contract.md`
6. `docs/contracts/08-mock-provider-contract.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`

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
backend/app/modules/ai_runtime/schemas.py
backend/app/workers/enqueue.py
backend/app/workers/handlers/ai_task_handler.py
backend/app/tests/ai_runtime/test_ai_task_worker.py
```

Read Mock Provider implementation only to call it; do not expand provider behavior in this task.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/ai_runtime/test_ai_task_worker.py -q
```

Expected result: the AI task worker focused test passes.

## Acceptance

- AI task can move through created, pending, running, succeeded, failed, and cancelled states in deterministic tests.
- Worker handler uses the mock provider and local artifact store; no external LLM or network is used.
- Worker records raw, parsed, schema validation, context manifest, and error artifacts as Artifact rows.
- Worker records one LLMCallLog for each mock provider call.
- Fake queue is acceptable for tests; do not add real Redis worker CLI unless already available and required.
- No AI Task API, frontend, real provider, vector index, RAG storage, or MCP runtime is added in this task.
- `git status --short` shows only expected worker/service files before commit.

## Commit Message

```text
feat(ai-runtime): add ai task worker handler
```

## Next Task

Slice 04 Task 6: Add AI Task API.
