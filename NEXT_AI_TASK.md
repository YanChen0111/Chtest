# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 24: Local Artifact Access Links.

## Current Task

Slice 24 Task 3: Add backend artifact download API.

## Product Value Answer

After this task, persisted local Artifact rows can be read through a controlled
read-only backend endpoint, without accepting arbitrary paths or external
artifact URLs.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`
8. `docs/implementation/slices/slice-24-local-artifact-access-links.md`
9. existing local artifact store and Artifact model/service patterns

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
backend artifact API/router/service files needed for local read access
backend/app/tests/api/test_artifact_access.py
```

Backend API task. Do not add frontend links, artifact upload/mutation/delete,
cloud storage, external artifact fetch, RBAC, tenants, permissions, package
upgrades, or redesign work.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_artifact_access.py -q
git diff --check
```

Expected result: artifact access API tests and diff check pass.

## Acceptance

- Reads only persisted Artifact rows with local `file_path` values under the
  artifact root.
- Returns content with recorded MIME type and safe download filename behavior.
- Rejects missing artifacts and unsafe paths.
- Does not mutate artifact rows or files.

## Commit Message

```text
feat(artifact): add local artifact access api
```

## Next Task

Slice 24 Task 4: Add frontend artifact links.
