# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 29: Execution Run Manifest.

## Current Task

Slice 29 Task 2: Define execution run manifest contract.

## Product Value Answer

After this task, the execution run manifest is defined as read-only presentation
from existing TestRun fields and Artifact metadata before frontend changes.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`
8. `docs/implementation/10-v2-scope-options.md`
9. `docs/implementation/slices/slice-29-execution-run-manifest.md`
10. `memory/08-session-handoff.md`
11. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, and frontend redesign docs unless a concrete blocker
  requires them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
docs/implementation/slices/slice-29-execution-run-manifest.md
docs/contracts/01-data-model-contract.md
docs/contracts/02-api-contract.md
docs/contracts/04-artifact-contract.md
```

Contract task. Do not add frontend code, backend feature code, tests,
migrations, package upgrades, artifact upload/mutation/delete, cloud storage,
external provider integration, RBAC, tenants, permissions, broad redesign work,
report generation behavior, runner behavior changes, quality gate computation
changes, RAG runtime, or MCP runtime.

## Verification Command

```bash
rg -n "execution run manifest|runtime artifact|dependency snapshot|environment snapshot|network policy" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-29-execution-run-manifest.md
git diff --check
```

Expected result: execution run manifest contract language is present and diff
check passes.

## Acceptance

- Data/API/artifact contracts define execution run manifest as presentation
  derived from existing TestRun fields and Artifact metadata.
- Contract states missing runtime/dependency/environment snapshots remain
  visible but unavailable.
- Contract states local open links are allowed only for persisted local Artifact
  ids through the existing artifact access endpoint.
- Contract preserves the no runner, report, failure analysis, quality gate,
  remote provider, RAG runtime, or MCP runtime behavior change boundary.

## Commit Message

```text
docs(v2): define execution run manifest contract
```

## Next Task

Slice 29 Task 3: Add frontend run manifest panel.
