# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 20: CI Run Metadata Import.

## Current Task

Slice 20 Task 3: Add deterministic CI metadata parser.

## Product Value Answer

After this task, Chtest can parse static CI metadata JSON into a deterministic
internal model while rejecting control fields, credentials, and remote-provider
behavior before any import API is exposed.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`
8. `docs/implementation/slices/slice-15-cicd-quality-center.md`
9. `docs/implementation/slices/slice-20-ci-run-metadata-import.md`

## Do Not Read Unless Needed

- Remote CI provider integration docs, webhooks, PR bots, release management,
  RAG runtime, MCP runtime, RBAC, tenants, permissions, and marketplace docs
  unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
docs/implementation/slices/slice-20-ci-run-metadata-import.md
backend/app/modules/cicd/service.py
backend/app/modules/cicd/schemas.py
backend/app/tests/api/test_ci_run_metadata_import.py
```

Parser-only task. User approved development after the V2 document-design review.
Do not add the import API endpoint, frontend code, migrations, remote CI
provider calls, webhooks, pipeline triggers, reruns, PR comments,
deploy/release controls, credentials, RBAC, tenants, permissions, marketplace,
RAG runtime, or MCP runtime.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_ci_run_metadata_import.py -q
git diff --check
```

Expected result: deterministic CI metadata parser tests and diff check pass.

## Acceptance

- Parses provider label, pipeline name, job name, conclusion, started/finished
  timestamps, duration, base/head refs, changed files, and artifact references.
- Treats provider as an inert label only.
- Rejects secret-like fields, credentials, webhook payload actions, trigger
  commands, rerun/cancel/schedule/deploy/release controls, and malformed changed
  files.
- Normalizes changed file roles and risks using existing CICDChangedFile
  classification rules where possible.
- Does not fetch external artifact URLs or call remote providers.

## Commit Message

```text
feat(cicd): add ci metadata import parser
```

## Next Task

Slice 20 Task 4: Add CI run import API.
