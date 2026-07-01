# Slice 22: JMeter Local Execution Evidence Task Plan

## Goal

Add a narrow V2 runner expansion for local JMeter non-GUI execution evidence.

This slice lets Chtest run an approved JMeter test plan through the same
evidence loop used by pytest, Playwright, and Newman: command allowlist, TestRun
state, stdout/stderr artifacts, JTL result artifacts, parsed sampler/assertion
summary, and frontend-readable execution evidence. It must not become a
performance testing platform, a JMX editor, distributed load infrastructure, or
arbitrary shell execution.

## Source Documents

- `docs/product/01-positioning-and-scope.md`
- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/10-v2-scope-options.md`
- `docs/implementation/slices/slice-12-testrunner-pytest-execution.md`
- `docs/implementation/slices/slice-13-playwright-minimal-loop.md`
- `docs/implementation/slices/slice-18-newman-api-execution.md`

## Preconditions

- pytest, Playwright, and Newman already prove the controlled local runner
  evidence loop.
- TestCommand, ToolDefinition, ToolInvocation, TestRun, TestResult, Artifact,
  and frontend execution-center patterns already exist.
- Slice 19, Slice 20, and Slice 21 strengthened knowledge, CI import, and review
  attribution evidence, so runner expansion can return as the next practical
  V2 value.
- JMeter must run only through approved local TestCommand/ToolDefinition
  allowlists.

## Product Value Answer

After this slice, a test engineer can run an approved local JMeter test plan in
non-GUI mode, inspect execution status, review stdout/stderr and JTL artifacts,
and see parsed sampler/assertion counts and durations as evidence. This expands
Chtest from API functional runner evidence into lightweight performance/API
execution evidence while preserving local-first safety and auditability.

## Non-goals

- No JMX editor, recorder, parameterization UI, scenario designer, or test-plan
  authoring workflow.
- No performance trend dashboard, capacity analysis, SLA management, load
  modeling, or benchmark platform.
- No distributed JMeter, remote agents, cloud load testing, or Kubernetes
  runner.
- No arbitrary shell execution, unapproved working directory, shell operators,
  or command string concatenation.
- No secret manager, credentials vault, account system, RBAC, tenants,
  permissions, SSO, or enterprise audit.
- No remote CI provider control, PR comments, deployment automation, release
  automation, or external pipeline trigger.
- No automatic Report, FailureAnalysis, QualityGateDecision, RAG runtime, MCP
  runtime, marketplace, or cloud sync.

## Slice Boundary

- Extend `TestCommand.command_type` to include `jmeter`.
- Extend `TestRun.runner_mode` to include `jmeter_local`.
- Add a JMeter-specific allowlisted tool intent such as
  `jmeter_non_gui_run`.
- Execute only local non-GUI JMeter commands equivalent to:
  `jmeter -n -t <plan.jmx> -l <result.jtl>`.
- Capture stdout/stderr using existing text artifact patterns.
- Store machine-readable JMeter output as a typed artifact, planned as
  `jmeter_jtl`.
- Store parsed sampler/assertion summary as existing `parsed_result` evidence.
- Map sampler rows to TestResult rows when deterministic names can be derived;
  otherwise preserve sampler aggregate data in parsed_result.
- Use a fake JMeter executable or deterministic JTL fixture for backend and
  golden tests so verification does not depend on a local JMeter installation.
- Add a compact frontend execution shell that shows status, summary counts,
  durations, failures/errors, and artifact links.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add JMeter Local Execution Evidence task plan | done | `test -f docs/implementation/slices/slice-22-jmeter-local-execution.md && rg -n "JMeter|jmeter|jmeter_local|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-22-jmeter-local-execution.md docs/implementation/10-v2-scope-options.md` | `59d3918` | planning-only scope |
| Define JMeter execution contract boundary | done | `rg -n "JMeter|jmeter|jmeter_local|jmeter_jtl|ToolDefinition|command_type" docs/contracts docs/implementation/slices/slice-22-jmeter-local-execution.md` | `10fa27d` | contract-only before code |
| Add JMeter parser and backend API tests | done | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_jmeter_execution.py -q` | `0d1a666` | deterministic JTL parsing first |
| Add JMeter runner backend | done | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_jmeter_execution.py -q` | pending | allowlisted fake executable tests |
| Add JMeter execution frontend shell | planned | `npm --prefix frontend run test -- --run` | pending | compact Chinese UI |
| Add JMeter local execution golden smoke | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_jmeter_local_execution_golden.py -q` | pending | TestRun evidence proof |
| Slice 22 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_jmeter_execution.py backend/app/tests/golden/test_jmeter_local_execution_golden.py -q && npm --prefix frontend run test -- --run && git diff --check` | pending | docs and handoff |

## Task 1: Add JMeter Local Execution Evidence Task Plan

Goal: Define the smallest useful JMeter runner slice before implementation.

Expected files:

- `docs/implementation/slices/slice-22-jmeter-local-execution.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-22-jmeter-local-execution.md
rg -n "JMeter|jmeter|jmeter_local|Product Value Answer|Non-goals|Task Table|Task 2" docs/implementation/slices/slice-22-jmeter-local-execution.md docs/implementation/10-v2-scope-options.md
git diff --check
```

Acceptance:

- Creates the Slice 22 plan.
- Defines product value, non-goals, slice boundary, task table, expected files,
  and verification commands.
- Selects JMeter local execution evidence as the next V2 slice.
- Keeps the scope to local runner evidence, not a performance testing platform.
- Does not add product code, backend code, frontend code, or contract changes.

Commit message:

```text
docs(v2): add jmeter execution slice plan
```

## Task 2: Define JMeter Execution Contract Boundary

Goal: Update contracts so implementation has a precise local JMeter execution
boundary.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-22-jmeter-local-execution.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "JMeter|jmeter|jmeter_local|jmeter_jtl|ToolDefinition|command_type" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-22-jmeter-local-execution.md
git diff --check
```

Acceptance:

- Data contract allows `TestCommand.command_type=jmeter`.
- Data contract allows `TestRun.runner_mode=jmeter_local`.
- Artifact contract defines `jmeter_jtl` and parsed JMeter evidence.
- API contract keeps JMeter under `POST /api/test-runs` or existing execution
  surfaces without adding JMX editing or performance dashboard APIs.
- State-machine contract keeps JMeter under ToolDefinition allowlists and
  existing TestRun status rules.
- Non-goals explicitly exclude arbitrary shell, distributed load testing,
  performance platform features, RAG/MCP runtime, RBAC, tenants, and
  permissions.

Commit message:

```text
docs(v2): define jmeter execution contract
```

## Task 3: Add JMeter Parser And Backend API Tests

Goal: Parse deterministic JMeter JTL evidence into Chtest execution summaries.

Expected files:

- `backend/app/modules/execution/jmeter_runner.py` or focused parser module
- `backend/app/tests/api/test_jmeter_execution.py`
- deterministic JTL fixture data needed by the test

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_jmeter_execution.py -q
```

Acceptance:

- Parses JTL CSV or XML fixture rows deterministically.
- Produces total, passed, failed, error, duration, and sampler summary fields.
- Preserves failure/error details needed by frontend display.
- Does not require a local JMeter binary.
- Does not execute commands in this task unless needed by existing test shape.

Commit message:

```text
feat(execution): parse jmeter evidence
```

## Task 4: Add JMeter Runner Backend

Goal: Add the controlled local JMeter execution path.

Expected files:

- `backend/app/modules/execution/jmeter_runner.py`
- execution service/router/schema files needed to register `jmeter_local`
- `backend/app/tests/api/test_jmeter_execution.py`
- fake JMeter executable or deterministic runner fixture

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_jmeter_execution.py -q
```

Acceptance:

- Approved `TestCommand(command_type=jmeter)` can create a TestRun using
  `runner_mode=jmeter_local`.
- Runner creates stdout/stderr, `jmeter_jtl`, and parsed_result artifacts.
- Runner rejects shell operators, unsafe paths, and unapproved command shapes.
- Runner handles timeout/error states through existing TestRun state rules.
- Tests do not depend on a real JMeter installation.

Commit message:

```text
feat(execution): add jmeter local runner
```

## Task 5: Add JMeter Execution Frontend Shell

Goal: Show compact JMeter execution evidence in the frontend.

Expected files:

- frontend execution API/store/view files needed for JMeter display
- focused frontend tests

Verification Command:

```bash
npm --prefix frontend run test -- --run
```

Acceptance:

- UI exposes JMeter as an execution mode only when using approved local
  commands.
- UI shows TestRun status, total/passed/failed/error sampler counts, duration,
  and artifact links.
- UI uses Chinese-facing labels while keeping product terms such as TestRun,
  TestResult, JMeter, and JTL unchanged.
- Does not add a JMX editor, performance dashboard, distributed runner controls,
  secrets UI, CI provider controls, RBAC, tenants, or permissions.

Commit message:

```text
feat(frontend): show jmeter execution evidence
```

## Task 6: Add JMeter Local Execution Golden Smoke

Goal: Prove local JMeter execution evidence fits the Chtest evidence loop.

Expected files:

- `backend/app/tests/golden/test_jmeter_local_execution_golden.py`
- `docs/fixtures/11-jmeter-local-execution-golden.md`
- `docs/implementation/slices/slice-22-jmeter-local-execution.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_jmeter_local_execution_golden.py -q
```

Acceptance:

- Golden proves approved local JMeter command creates TestRun evidence.
- Golden proves stdout/stderr, JTL, parsed_result, and optional TestResult rows
  are persisted.
- Golden proves unsafe shell/provider/platform features are absent.
- Golden does not require a real local JMeter installation.

Commit message:

```text
test(golden): add jmeter local execution smoke
```

## Slice 22 Completion Gate

Goal: Validate all JMeter local execution work and prepare the next V2 task.

Expected files:

- `docs/implementation/slices/slice-22-jmeter-local-execution.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_jmeter_execution.py backend/app/tests/golden/test_jmeter_local_execution_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

Acceptance:

- All Slice 22 task rows are marked done with commit ids.
- Completion evidence records backend, golden, frontend, and diff
  verification.
- Handoff names the next V2 slice or planning task.
- Non-goals remain excluded.

Commit message:

```text
docs(v2): complete jmeter execution slice
```
