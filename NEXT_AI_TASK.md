# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 24: Local Artifact Access Links.

## Current Task

Slice 24 Completion Gate.

## Product Value Answer

After this task, Slice 24 is closed with backend API, frontend links, and golden
artifact access evidence verified together.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`
8. `docs/implementation/slices/slice-24-local-artifact-access-links.md`
9. existing artifact access API, golden, and execution frontend tests

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
backend/app/tests/golden/test_artifact_access_golden.py
docs/fixtures/12-local-artifact-access-golden.md
```

Completion gate task. Do not add frontend code, backend feature code, artifact
upload/mutation/delete, cloud storage, external artifact fetch, RBAC, tenants,
permissions, package upgrades, broad redesign work, or runner behavior changes.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_artifact_access.py backend/app/tests/golden/test_artifact_access_golden.py -q
npm --prefix frontend run build
npm --prefix frontend run test -- --run
git diff --check
```

Expected result: Slice 24 backend API, golden, frontend build, frontend suite,
and diff check pass.

## Acceptance

- Slice 24 task table records completed task commits through Task 5.
- Backend artifact access API and golden smoke pass together.
- Frontend execution artifact links still build and test successfully.
- Handoff names the next V2 small slice selection task.

## Commit Message

```text
docs(v2): complete local artifact access slice
```

## Next Task

Select the next V2 small slice after Slice 24 completion.
