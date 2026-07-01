# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Select the next V2 small slice after Slice 25 completion.

## Current Task

Choose and plan the next narrow V2 slice.

## Product Value Answer

After this task, the next V2 slice is selected with a small task plan before
any product code changes.

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
11. `docs/implementation/10-v2-scope-options.md`
12. recent session handoff and dev log

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

Planning task. Do not add frontend code, backend feature code, migrations,
package upgrades, artifact upload/mutation/delete, cloud storage, external
provider integration, RBAC, tenants, permissions, broad redesign work, report
generation behavior, or runner behavior changes.

## Verification Command

```bash
test -f docs/implementation/slices/<next-slice-file>.md
rg -n "<next slice name>|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/<next-slice-file>.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md
git diff --check
```

Expected result: next slice plan exists, scope is narrow and local-first, and
diff check passes.

## Acceptance

- Slice 25 completion is recorded as done in handoff and dev log.
- `docs/implementation/10-v2-scope-options.md` records Slice 25 completion and
  recommends one next V2 slice.
- A new slice plan defines product value, non-goals, task table, expected files,
  verification commands, and commit messages.
- `NEXT_AI_TASK.md` points to the first implementation task for the selected
  slice.

## Commit Message

```text
docs(v2): add next v2 slice plan
```

## Next Task

First implementation task from the selected next V2 slice.
