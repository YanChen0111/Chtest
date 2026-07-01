# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 22: JMeter Local Execution Evidence.

## Current Task

Slice 22 Completion Gate.

## Product Value Answer

After this task, Slice 22 is closed with backend, frontend, golden, docs, and
handoff evidence verified together.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`
8. `docs/implementation/slices/slice-22-jmeter-local-execution.md`
9. existing JMeter API tests, frontend tests, and golden smoke fixtures

## Do Not Read Unless Needed

- JMeter distributed execution, cloud load testing, remote CI provider
  integration, webhooks, PR bots, release management, RAG runtime, MCP runtime,
  RBAC, tenants, permissions, and marketplace docs unless a concrete blocker
  requires them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
docs/implementation/slices/slice-22-jmeter-local-execution.md
```

Completion gate task. Do not add product code, frontend features, JMX editing,
performance dashboards, distributed runners, arbitrary shell execution, secrets
management, CI provider controls, RAG runtime, MCP runtime, RBAC, tenants, or
permissions.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_jmeter_execution.py backend/app/tests/golden/test_jmeter_local_execution_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

Expected result: JMeter backend/API golden smoke, frontend tests, and diff check pass.

## Acceptance

- All Slice 22 task rows are marked done with commit ids.
- Completion evidence records backend, golden, frontend, and diff verification.
- Handoff names the next V2 slice or planning task.
- Non-goals remain excluded.

## Commit Message

```text
docs(v2): complete jmeter execution slice
```

## Next Task

Select the next V2 small slice.
