# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 18: Newman API Execution.

## Current Task

Slice 18 Completion Gate.

## Product Value Answer

After this task, Slice 18 is verified end to end and ready for the next V2
planning or implementation task.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/02-v1-slice-plan.md`
3. `docs/product/01-positioning-and-scope.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/03-state-machines.md`
7. `docs/contracts/04-artifact-contract.md`
8. `docs/implementation/04-ai-vibecoding-governance.md`
9. `docs/implementation/00-v0.1-walking-skeleton.md`
10. `docs/fixtures/00-v1-demo-path.md`
11. `docs/implementation/10-v2-scope-options.md`
12. `docs/implementation/slices/slice-18-newman-api-execution.md`
13. `backend/app/tests/api/test_newman_execution.py`
14. `backend/app/tests/golden/test_newman_api_execution_golden.py`
15. frontend Newman execution tests

## Do Not Read Unless Needed

- RAG runtime, MCP runtime, RBAC, tenants, permissions, release management, and
  remote CI provider integration docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
docs/implementation/slices/slice-18-newman-api-execution.md
```

Completion-only task. Do not add new product behavior. Record verification
evidence, mark Slice 18 complete, and name the next V2 task.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_newman_execution.py backend/app/tests/golden/test_newman_api_execution_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

Expected result: Newman backend/API golden tests, frontend tests, and diff check
pass.

## Acceptance

- All Slice 18 task rows are marked done with commit ids.
- Completion evidence records backend, golden, frontend, and diff verification.
- Handoff names the next V2 slice or planning task.
- Non-goals remain excluded.

## Commit Message

```text
docs(v2): complete newman execution slice
```

## Next Task

Choose the next V2 task after Slice 18 completion evidence is committed.
