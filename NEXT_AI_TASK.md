# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 29: Execution Run Manifest.

## Current Task

Slice 29 Task 4: Add execution run manifest golden smoke.

## Product Value Answer

After this task, a golden smoke proves execution run manifest inputs stay tied
to existing TestRun and Artifact evidence.

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
backend/app/tests/golden/test_execution_run_manifest_golden.py
docs/fixtures/17-execution-run-manifest-golden.md
```

Golden smoke task. Do not add frontend code, backend feature code beyond the
focused test, migrations, package upgrades, artifact upload/mutation/delete,
cloud storage,
external provider integration, RBAC, tenants, permissions, broad redesign work,
report generation behavior, runner behavior changes, quality gate computation
changes, RAG runtime, or MCP runtime.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q
git diff --check
```

Expected result: execution run manifest golden smoke and diff check pass.

## Acceptance

- Golden proves TestRun read data keeps command, working directory,
  runner_mode, run workspace, repository/network policy, parsed result, and
  artifact metadata available for manifest display.
- Golden proves local artifact ids remain openable through existing artifact
  access when they are persisted local artifacts.
- Golden proves missing snapshot ids remain visible as missing/unavailable
  evidence.
- Golden proves run manifest display inputs do not create Report,
  FailureAnalysis, QualityGateDecision, AutomationRepair, new TestRun, artifact
  mutation, remote provider behavior, RAG runtime, or MCP runtime.

## Commit Message

```text
test(golden): add execution run manifest smoke
```

## Next Task

Slice 29 Completion Gate.
