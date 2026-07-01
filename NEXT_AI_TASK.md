# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 22: JMeter Local Execution Evidence.

## Current Task

Slice 22 Task 2: Define JMeter execution contract boundary.

## Product Value Answer

After this task, the contracts define how local JMeter non-GUI execution fits
the existing TestCommand, ToolDefinition, TestRun, TestResult, and Artifact
evidence loop before any implementation code is added.

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
docs/contracts/01-data-model-contract.md
docs/contracts/02-api-contract.md
docs/contracts/03-state-machines.md
docs/contracts/04-artifact-contract.md
docs/implementation/slices/slice-22-jmeter-local-execution.md
```

Contract boundary task. Do not add backend implementation, frontend code,
golden tests, JMX editing, performance dashboards, distributed runners,
arbitrary shell execution, secrets management, CI provider controls, RAG
runtime, MCP runtime, RBAC, tenants, or permissions.

## Verification Command

```bash
rg -n "JMeter|jmeter|jmeter_local|jmeter_jtl|ToolDefinition|command_type" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-22-jmeter-local-execution.md
git diff --check
```

Expected result: JMeter contract keywords are present across contracts and the
Slice 22 plan; diff check passes.

## Acceptance

- Data contract allows `TestCommand.command_type=jmeter`.
- Data contract allows `TestRun.runner_mode=jmeter_local`.
- Artifact contract defines `jmeter_jtl` and parsed JMeter evidence.
- API contract keeps JMeter under existing execution surfaces without JMX
  editing or performance dashboard APIs.
- State-machine contract keeps JMeter under ToolDefinition allowlists and
  existing TestRun status rules.
- Non-goals explicitly exclude arbitrary shell, distributed load testing,
  performance platform features, RAG/MCP runtime, RBAC, tenants, and
  permissions.

## Commit Message

```text
docs(v2): define jmeter execution contract
```

## Next Task

Slice 22 Task 3: Add JMeter parser and backend API tests.
