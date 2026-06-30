# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 13: Playwright Minimal Loop.

## Current Task

Task 2: Add Playwright execution API contract and task boundary.

## Product Value Answer

After this task, Chtest has a contract-first API boundary for minimal
Playwright execution before backend implementation starts.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/02-v1-slice-plan.md`
3. `docs/product/01-positioning-and-scope.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/slices/slice-13-playwright-minimal-loop.md`
8. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- CI/CD, report center, RAG runtime, MCP runtime, and migration reference docs
  unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
docs/implementation/slices/slice-13-playwright-minimal-loop.md
docs/contracts/02-api-contract.md
docs/contracts/04-artifact-contract.md
```

This is a contract/documentation task only. Do not modify product code.

## Verification Command

```bash
rg -n "Playwright|POST /api/playwright-runs|playwright_trace|screenshot" docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-13-playwright-minimal-loop.md
```

Expected result: API/artifact contracts and Slice 13 plan name the minimal
Playwright execution endpoint and evidence artifacts.

## Acceptance

- Contract defines minimal Playwright execution endpoint shape.
- Request supports approved Playwright AutomationDraft or configured
  Playwright TestCommand.
- Response reuses TestRun/TestResult evidence shape and includes trace and
  screenshot artifact metadata.
- Keep V1 Playwright execution allowlisted and local-first.
- Do not add reports, failure analysis, CI/CD quality, RAG runtime, MCP runtime,
  RBAC, tenants, permissions, low-code UI automation, or browser matrix work.
- Update handoff and set the next task to Playwright runner adapter.

## Commit Message

```text
docs(playwright): define minimal execution api
```

## Next Task

Slice 13 Task 3: Add Playwright runner adapter.
