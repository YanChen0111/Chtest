# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the whole planning set.

## Current Slice

Slice 04: AI Runtime Core.

## Current Task

Task 7: Add AI task frontend status shell.

## Product Value Answer

After this task, Chtest can show a lightweight AI Workbench status surface with
recent AI tasks, selected task details, model metadata, context usage, LLM call
logs, and generated artifact summaries.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-04-ai-runtime-core.md`
3. `docs/implementation/slices/slice-02-frontend-foundation.md`
4. `docs/product/06-frontend-ui-guidelines.md`
5. `docs/product/08-frontend-design-spec.md`
6. `docs/contracts/02-api-contract.md`
7. `docs/contracts/04-artifact-contract.md`
8. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Requirement review or case generation product pages.
- CI/CD Quality Center implementation docs beyond artifact owner references.
- RAG runtime, vector index, embedding, chunking, or reranking docs.
- MCP runtime integration docs.

## Expected Files

Create or update only these files for the current task:

```text
frontend/src/views/ai-workbench/AiWorkbenchView.vue
frontend/src/api/aiTasks.ts
frontend/src/stores/aiTasks.ts
frontend/src/router/index.ts
frontend/src/views/ai-workbench/AiWorkbenchView.spec.ts
```

Read nearby frontend API/store/router tests only to follow existing Vue 3 + Arco Design Vue patterns.

## Verification Command

```bash
npm --prefix frontend run test -- --run
```

Expected result: the frontend focused and existing Vitest tests pass.

## Acceptance

- AI 工作台 displays recent AI tasks from `GET /api/projects/{project_id}/ai-tasks`.
- Selecting a task displays status, prompt/skill ids, provider/model, token usage, context artifact ids, LLM call logs, and artifact summaries from `GET /api/ai-tasks/{id}`.
- Visible labels remain Chinese-first and use the approved light Arco workbench style.
- Raw LLM output content is not fetched or displayed; only artifact metadata, safe flags, and paths are shown.
- No full requirement review UI, case generation UI, charts beyond simple status counts, real provider, vector index, RAG storage, or MCP runtime is added in this task.
- `git status --short` shows only expected frontend files and required task docs before commit.

## Commit Message

```text
feat(frontend): add ai task status shell
```

## Next Task

Slice 04 completion gate, then Slice 05 Prompt And Skill Registry.
