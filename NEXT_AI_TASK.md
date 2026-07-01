# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 22: JMeter Local Execution Evidence.

## Current Task

Slice 22 Task 4: Add JMeter runner backend.

## Product Value Answer

After this task, an approved `TestCommand(command_type=jmeter)` can create a
local `TestRun` with `runner_mode=jmeter_local`, persisted stdout/stderr,
`jmeter_jtl`, parsed_result, and TestResult evidence without requiring a real
JMeter installation in tests.

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
backend/app/modules/execution/service.py
backend/app/tests/api/test_jmeter_execution.py
```

Runner task. Do not add frontend code, golden tests, JMX editing, performance
dashboards, distributed runners, arbitrary shell execution, secrets management,
CI provider controls, RAG runtime, MCP runtime, RBAC, tenants, or permissions.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_jmeter_execution.py -q
git diff --check
```

Expected result: JMeter runner/API tests and diff check pass.

## Acceptance

- Approved `TestCommand(command_type=jmeter)` can create a TestRun using
  `runner_mode=jmeter_local`.
- Runner creates stdout/stderr, `jmeter_jtl`, and parsed_result artifacts.
- Runner rejects shell operators, unsafe paths, and unapproved command shapes.
- Runner handles timeout/error states through existing TestRun state rules.
- Tests do not depend on a real JMeter installation.

## Commit Message

```text
feat(execution): add jmeter local runner
```

## Next Task

Slice 22 Task 5: Add JMeter execution frontend shell.
