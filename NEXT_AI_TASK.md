# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 22: JMeter Local Execution Evidence.

## Current Task

Slice 22 Task 3: Add JMeter parser and backend API tests.

## Product Value Answer

After this task, Chtest can parse deterministic JMeter JTL evidence into a
backend execution summary shape before the live runner path is added.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`
8. `docs/implementation/slices/slice-22-jmeter-local-execution.md`
9. `docs/implementation/slices/slice-18-newman-api-execution.md`

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
backend/app/modules/execution/jmeter_runner.py
backend/app/tests/api/test_jmeter_execution.py
```

Parser/API-test task. Do not add live JMeter execution, frontend code, golden
tests, JMX editing, performance dashboards, distributed runners, arbitrary shell
execution, secrets management, CI provider controls, RAG runtime, MCP runtime,
RBAC, tenants, or permissions.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_jmeter_execution.py -q
git diff --check
```

Expected result: JMeter parser/API tests and diff check pass.

## Acceptance

- Parses JTL CSV or XML fixture rows deterministically.
- Produces total, passed, failed, error, duration, and sampler summary fields.
- Preserves failure/error details needed by frontend display.
- Does not require a local JMeter binary.
- Does not execute commands in this task unless needed by existing test shape.

## Commit Message

```text
feat(execution): parse jmeter evidence
```

## Next Task

Slice 22 Task 4: Add JMeter runner backend.
