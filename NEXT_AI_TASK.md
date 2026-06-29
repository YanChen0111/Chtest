# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the whole planning set.

## Current Slice

Slice 06: Requirement To Case Mainline.

## Current Task

Task 0: Create Slice 06 task plan.

## Product Value Answer

After this task, Chtest has a focused Slice 06 task plan for requirement review,
risk analysis, case generation, and case review, so future AI coding sessions can
continue without broad roadmap rereads.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/05-prompt-skill-contract.md`
7. `docs/fixtures/01-golden-requirement-to-case.md`
8. `docs/implementation/01-v1-delivery-plan.md`
9. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- AutomationDraft, Playwright, CI/CD Quality Center, report center, RAG runtime,
  vector index, embedding, chunking, reranking, MCP runtime, and frontend polish
  docs unless a concrete Slice 06 task requires them.

## Expected Files

Create or update only these files for the current task:

```text
docs/implementation/slices/slice-06-requirement-to-case.md
NEXT_AI_TASK.md
```

Do not implement Slice 06 code in this planning task.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/db/test_prompt_skill_models.py -q
```

Expected result: existing prompt/skill model smoke remains green after docs-only
handoff changes.

## Acceptance

- Slice 06 task file exists and breaks M3 into small, verified backend/frontend
  tasks.
- The first executable Slice 06 task has expected files, non-goals,
  verification command, and commit message.
- Task plan follows V1 boundaries: no RBAC, no RAG runtime, no MCP runtime,
  no AutomationDraft or CI/CD scope.
- `NEXT_AI_TASK.md` points to the first executable Slice 06 task after the plan
  is created.

## Commit Message

```text
docs(slice-06): add requirement to case task plan
```

## Next Task

Slice 06 Task 1: Add Requirement Review models and migration.
