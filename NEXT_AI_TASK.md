# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the whole planning set.

## Current Slice

Slice 04: AI Runtime Core.

## Current Task

Slice 04 Completion Gate.

## Product Value Answer

After this task, Chtest has a verified AI Runtime Core slice: AI tasks, context
artifacts, artifact storage, mock provider, worker status progression, task APIs,
and the AI Workbench status shell are all traceable and ready for Prompt/Skill
Registry work.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-04-ai-runtime-core.md`
3. `docs/implementation/02-v1-slice-plan.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/contracts/08-mock-provider-contract.md`
8. `docs/product/06-frontend-ui-guidelines.md`
9. `docs/product/08-frontend-design-spec.md`
10. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Requirement review or case generation product pages.
- Prompt/Skill implementation details unless setting the next task pointer requires them.
- CI/CD Quality Center implementation docs beyond artifact owner references.
- RAG runtime, vector index, embedding, chunking, or reranking docs.
- MCP runtime integration docs.

## Expected Files

Create or update only these files for the current task:

```text
docs/implementation/slices/slice-04-ai-runtime-core.md
NEXT_AI_TASK.md
memory/07-dev-log.md
memory/08-session-handoff.md
```

Read implementation files only if a completion-gate verification failure requires debugging.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/db/test_ai_runtime_models.py backend/app/tests/artifacts/test_artifact_store.py backend/app/tests/api/test_context_artifacts.py backend/app/tests/api/test_ai_tasks.py backend/app/tests/ai_runtime/test_mock_provider.py backend/app/tests/ai_runtime/test_ai_task_worker.py -q
npm --prefix frontend run test -- --run
npm --prefix frontend run build
git diff --check
```

Expected result: Slice 04 backend and frontend verification passes.

## Acceptance

- Slice 04 task table marks every task done with commit ids or current pending commit.
- AI Runtime backend regression passes.
- Frontend AI Workbench tests and build pass.
- `memory/07-dev-log.md` and `memory/08-session-handoff.md` summarize Slice 04 completion and remaining risks.
- `NEXT_AI_TASK.md` is set to Slice 05 Task 1: Add PromptVersion and SkillVersion models.
- No new business endpoints, real provider, vector index, RAG storage, MCP runtime, or unrelated frontend pages are added.

## Commit Message

```text
docs(memory): complete ai runtime slice handoff
```

## Next Task

Slice 05 Task 1: Add PromptVersion and SkillVersion models.
