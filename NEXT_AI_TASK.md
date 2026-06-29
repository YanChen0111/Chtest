# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the whole planning set.

## Current Slice

Slice 04: AI Runtime Core.

## Current Task

Task 3: Add ContextArtifact API.

## Product Value Answer

After this task, Chtest can create and list lightweight project-level context
artifacts so later AI tasks can explicitly reference user-provided notes,
OpenAPI fragments, logs, fixtures, and bug summaries without adding RAG storage.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-04-ai-runtime-core.md`
3. `docs/contracts/04-artifact-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/01-data-model-contract.md`
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
backend/app/modules/ai_runtime/artifact_store.py
backend/app/modules/ai_runtime/router.py
backend/app/modules/ai_runtime/service.py
backend/app/modules/ai_runtime/schemas.py
backend/app/main.py
backend/app/tests/api/test_context_artifacts.py
```

Read nearby Project API tests/router/service only to follow existing FastAPI patterns.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_context_artifacts.py -q
```

Expected result: the ContextArtifact API focused test passes.

## Acceptance

- Create API stores project-level ContextArtifact content through the local artifact store.
- Artifact rows use `owner_entity_type=Project`, `owner_entity_id=project_id`, and context artifact types from the artifact contract.
- `metadata_json` records `title`, `source_ref`, `safe_to_show`, `redaction_applied`, and `allowed_for_prompt`.
- List API returns project context artifacts without reading unrelated artifact types.
- No file upload streaming, RAG indexing/chunking/embedding/reranking, AI task execution, mock provider, worker handler, frontend, or MCP runtime is added in this task.
- `git status --short` shows only expected ContextArtifact API files before commit.

## Commit Message

```text
feat(ai-runtime): add context artifact api
```

## Next Task

Slice 04 Task 4: Add Mock LLM Provider.
