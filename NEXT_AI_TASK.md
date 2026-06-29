# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the whole planning set.

## Current Slice

Slice 04: AI Runtime Core.

## Current Task

Task 1: Add AI Runtime models and migration.

## Product Value Answer

After this task, Chtest can persist AI task records, artifact metadata, context
artifact references, and LLM call logs so later mock-provider and worker tasks
can produce evidence-backed AI outputs.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-04-ai-runtime-core.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/04-artifact-contract.md`
5. `docs/contracts/08-mock-provider-contract.md`
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
backend/app/modules/ai_runtime/models.py
backend/app/modules/ai_runtime/schemas.py
backend/alembic/versions/<revision>_ai_runtime_core.py
backend/app/tests/db/test_ai_runtime_models.py
```

Read nearby backend model files only to follow existing SQLAlchemy patterns.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/db/test_ai_runtime_models.py -q
```

Expected result: the AI Runtime model and migration test passes.

## Acceptance

- AITask, Artifact, and LLMCallLog models follow `docs/contracts/01-data-model-contract.md`.
- `AITask.context_artifact_ids` can persist an explicit empty list or provided context artifact ids.
- Artifact metadata can represent V1 ContextArtifact records with `owner_entity_type=Project` and `owner_entity_id=project_id`.
- No real LLM provider, PromptVersion/SkillVersion models, vector index, RAG storage, worker handler, frontend, or MCP runtime is added in this task.
- `git status --short` shows only the expected AI Runtime model/migration/test files before commit.

## Commit Message

```text
feat(ai-runtime): add ai task artifact and llm call models
```

## Next Task

Slice 04 Task 2: Add Artifact store service.
