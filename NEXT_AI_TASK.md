# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 18: Newman API Execution.

## Current Task

Slice 18 Task 2: Define Newman execution contract boundary.

## Product Value Answer

After this task, the contracts explicitly define Newman API execution as an
allowlisted local evidence path before implementation starts.

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

## Do Not Read Unless Needed

- RAG runtime, MCP runtime, RBAC, tenants, permissions, release management, and
  remote CI provider integration docs unless a concrete blocker requires them.

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
docs/implementation/slices/slice-18-newman-api-execution.md
```

Contract-only task. Do not add product code, RAG runtime, MCP runtime, RBAC,
tenants, permissions, marketplace, cloud sync, release automation, remote CI
provider integration, Postman workspace parity, collection editor, or arbitrary
shell execution.

## Verification Command

```bash
rg -n "Newman|newman|newman_json|command_type|ToolDefinition" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-18-newman-api-execution.md
git diff --check
```

Expected result: Newman contract boundaries are visible and diff check passes.

## Acceptance

- Data contract allows `TestCommand.command_type=newman`.
- Artifact contract defines Newman output artifacts and parsed result
  expectations.
- State-machine contract keeps Newman under ToolDefinition allowlists and
  TestRun status rules.
- API contract names the API execution evidence surface without adding a
  collection editor or remote CI/CD provider integration.
- Non-goals still exclude arbitrary shell, Postman parity, RAG/MCP runtime,
  RBAC, tenants, and permissions.

## Commit Message

```text
docs(v2): define newman execution contract
```

## Next Task

Start Slice 18 Task 3 only after the Newman contract boundary is committed.
