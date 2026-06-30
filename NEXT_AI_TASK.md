# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 18: Newman API Execution.

## Current Task

Slice 18 Task 3: Add Newman runner/parser backend.

## Product Value Answer

After this task, the backend can execute an allowlisted local Newman API
collection, persist execution artifacts, and parse request/assertion evidence
into TestRun/TestResult records.

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
13. backend execution module and tests needed for Newman only

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
backend/app/modules/execution/newman_runner.py
backend/app/modules/execution/*
backend/app/tests/api/test_newman_execution.py
backend/app/tests/fixtures/*
```

Backend-only task. Add only the Newman runner/parser and focused tests needed
for Slice 18. Do not add frontend, RAG runtime, MCP runtime, RBAC, tenants,
permissions, marketplace, cloud sync, release automation, remote CI provider
integration, Postman workspace parity, collection editor, or arbitrary shell
execution.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_newman_execution.py -q
git diff --check
```

Expected result: Newman backend tests and diff check pass.

## Acceptance

- Runs only approved Newman TestCommand/ToolDefinition entries.
- Captures stdout, stderr, runtime manifest, dependency snapshot, environment
  snapshot, Newman JSON, and parsed result artifacts.
- Maps Newman collection/request/assertion results into TestRun/TestResult
  evidence.
- Uses deterministic local fixtures in tests.
- Rejects arbitrary command text and unapproved command types.
- Does not call remote CI/CD providers or require Postman cloud accounts.

## Commit Message

```text
feat(execution): add newman runner
```

## Next Task

Start Slice 18 Task 4 only after the Newman backend runner/parser is committed.
