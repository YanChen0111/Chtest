# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 24: Local Artifact Access Links.

## Current Task

Slice 24 Task 2: Define local artifact access contract.

## Product Value Answer

After this task, artifact access has a precise read-only local API and artifact
safety contract before backend/frontend implementation starts.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`
8. `docs/implementation/slices/slice-24-local-artifact-access-links.md`
9. existing artifact contract and execution artifact tables

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
docs/implementation/slices/slice-22-jmeter-local-execution.md
docs/implementation/10-v2-scope-options.md
docs/implementation/slices/slice-23-frontend-build-baseline.md
docs/implementation/slices/slice-24-local-artifact-access-links.md
docs/contracts/02-api-contract.md
docs/contracts/04-artifact-contract.md
```

Contract task. Do not add product code, backend code, frontend code, migrations,
package upgrades, redesign work, or tests. Do not start a broad artifact
platform expansion.

## Verification Command

```bash
rg -n "artifact access|download|GET /api/artifacts|Artifact" docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-24-local-artifact-access-links.md
git diff --check
```

Expected result: artifact access contract keywords are present and diff check passes.

## Acceptance

- API contract defines a read-only artifact content/download endpoint.
- Artifact contract defines local-root path safety, MIME/filename handling, and
  content access boundaries.
- External imported artifact references remain inert and unavailable through the
  local download endpoint.
- Non-goals remain explicit.

## Commit Message

```text
docs(v2): define artifact access contract
```

## Next Task

Slice 24 Task 3: Add backend artifact download API.
