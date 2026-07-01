# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 29: Execution Run Manifest.

## Current Task

Slice 29 Completion Gate.

## Product Value Answer

After this task, Slice 29 is fully verified and handed off with evidence that
execution run manifests remain readable, local, and evidence-only.

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
```

Completion gate task. Do not add frontend code, backend feature code, tests,
migrations, package upgrades, artifact upload/mutation/delete, cloud storage,
external provider integration, RBAC, tenants, permissions, broad redesign work,
report generation behavior, runner behavior changes, quality gate computation
changes, RAG runtime, or MCP runtime.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py backend/app/tests/golden/test_artifact_access_golden.py -q
npm --prefix frontend run build
npm --prefix frontend run test -- --run
git diff --check
```

Expected result: Slice 29 golden checks, frontend build, frontend tests, and
diff check pass.

## Acceptance

- All Slice 29 task rows are marked done with commit ids.
- Completion evidence records frontend build/test, golden checks, and diff
  verification.
- Non-goals remain excluded.
- Handoff names the next V2 slice or planning task.

## Commit Message

```text
docs(v2): complete execution run manifest slice
```

## Next Task

Select and plan the next narrow V2 task after Slice 29 completion.
