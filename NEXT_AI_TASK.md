# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 18: Newman API Execution.

## Current Task

Slice 18 Task 5: Add Newman API execution golden smoke.

## Product Value Answer

After this task, the Newman API execution path is proven by a golden smoke that
creates project settings, runs a deterministic Newman collection, and verifies
the evidence chain.

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
13. `backend/app/tests/golden/test_newman_api_execution_golden.py`
14. `docs/fixtures/07-newman-api-execution-golden.md`

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
backend/app/tests/golden/test_newman_api_execution_golden.py
docs/fixtures/07-newman-api-execution-golden.md
```

Golden-only task. Add only deterministic Newman API execution evidence proof.
Do not add new backend features, frontend changes, RAG runtime, MCP runtime,
RBAC, tenants, permissions, marketplace, cloud sync, release automation, remote
CI provider integration, Postman workspace parity, collection editor, or
arbitrary shell execution.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_newman_api_execution_golden.py -q
git diff --check
```

Expected result: Newman golden smoke and diff check pass.

## Acceptance

- Creates a project and approved Newman TestCommand fixture.
- Executes a deterministic Newman API collection fixture.
- Persists TestRun, TestResult, stdout/stderr, Newman JSON, parsed result, and
  environment/runtime evidence artifacts.
- Confirms failed assertions are visible as evidence, not hidden in logs.
- Confirms no arbitrary shell, Postman cloud, remote CI/CD, RAG/MCP runtime,
  RBAC, tenant, or permission dependency is introduced.

## Commit Message

```text
test(v2): add newman execution golden
```

## Next Task

Start Slice 18 completion gate only after the Newman golden smoke is committed.
