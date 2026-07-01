# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 22: JMeter Local Execution Evidence.

## Current Task

Slice 22 Task 6: Add JMeter local execution golden smoke.

## Product Value Answer

After this task, the JMeter local execution evidence loop is proven by a golden
smoke: approved command -> TestRun -> stdout/stderr -> `jmeter_jtl` ->
parsed_result -> optional TestResult rows.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`
8. `docs/implementation/slices/slice-22-jmeter-local-execution.md`
9. existing JMeter API tests and golden smoke fixtures

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
backend/app/tests/golden/test_jmeter_local_execution_golden.py
docs/fixtures/11-jmeter-local-execution-golden.md
```

Golden smoke task. Do not add frontend code, JMX editing, performance
dashboards, distributed runners, arbitrary shell execution, secrets management,
CI provider controls, RAG runtime, MCP runtime, RBAC, tenants, or permissions.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_jmeter_local_execution_golden.py -q
git diff --check
```

Expected result: JMeter golden smoke and diff check pass.

## Acceptance

- Golden proves approved local JMeter command creates TestRun evidence.
- Golden proves stdout/stderr, JTL, parsed_result, and optional TestResult rows
  are persisted.
- Golden proves unsafe shell/provider/platform features are absent.
- Golden does not require a real local JMeter installation.

## Commit Message

```text
test(golden): add jmeter local execution smoke
```

## Next Task

Slice 22 Completion Gate.
