# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 25: Execution Evidence Summary.

## Current Task

Slice 25 Completion Gate.

## Product Value Answer

After this task, Slice 25 is closed with the contract, frontend evidence
summary, and golden smoke verified together.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`
8. `docs/implementation/slices/slice-24-local-artifact-access-links.md`
9. `docs/implementation/10-v2-scope-options.md`
10. `docs/implementation/slices/slice-25-execution-evidence-summary.md`
11. recent session handoff and dev log

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
docs/implementation/slices/slice-25-execution-evidence-summary.md
docs/contracts/02-api-contract.md
docs/contracts/04-artifact-contract.md
backend/app/tests/golden/test_artifact_access_golden.py
docs/fixtures/12-local-artifact-access-golden.md
backend/app/tests/golden/test_execution_evidence_summary_golden.py
docs/fixtures/13-execution-evidence-summary-golden.md
```

Completion gate task. Do not add frontend feature code, backend feature code,
migrations, package upgrades, report generation behavior, artifact
upload/mutation/delete, cloud storage, external provider integration, RBAC,
tenants, permissions, broad redesign work, or runner behavior changes.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_execution_evidence_summary_golden.py backend/app/tests/golden/test_artifact_access_golden.py -q
npm --prefix frontend run build
npm --prefix frontend run test -- --run
git diff --check
```

Expected result: Slice 25 golden smoke, artifact access golden, frontend build,
frontend suite, and diff check pass.

## Acceptance

- Slice 25 task table records completed task commits through Task 4.
- Golden smoke and artifact access golden pass together.
- Frontend report evidence summary still builds and passes full frontend tests.
- Handoff names the next V2 small slice selection task.

## Commit Message

```text
docs(v2): complete execution evidence summary slice
```

## Next Task

Select the next V2 small slice after Slice 25 completion.
