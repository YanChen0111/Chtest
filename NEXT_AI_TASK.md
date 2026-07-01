# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 24: Local Artifact Access Links.

## Current Task

Slice 24 Task 5: Add artifact access golden smoke.

## Product Value Answer

After this task, local artifact access is proven by a golden smoke that reads a
persisted execution artifact and confirms external imported references remain
inert.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`
8. `docs/implementation/slices/slice-24-local-artifact-access-links.md`
9. existing artifact access API tests and execution golden fixtures

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

Golden smoke task. Do not add frontend code, artifact upload/mutation/delete,
cloud storage, external artifact fetch, RBAC, tenants, permissions, package
upgrades, broad redesign work, or runner behavior changes.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_artifact_access_golden.py -q
git diff --check
```

Expected result: artifact access golden smoke and diff check pass.

## Acceptance

- Golden proves a TestRun artifact can be read through the local artifact
  endpoint.
- Golden proves artifact content matches persisted sha256/size metadata.
- Golden proves external imported artifact references remain inert.

## Commit Message

```text
test(golden): add local artifact access smoke
```

## Next Task

Slice 24 Completion Gate.
