# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 20: CI Run Metadata Import.

## Current Task

Slice 20 Completion Gate.

## Product Value Answer

After this task, Slice 20 is closed with backend API, golden smoke, frontend
tests, and documentation proving CI metadata import is evidence-only.

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
backend/app/tests/api/test_ci_run_metadata_import.py
backend/app/tests/golden/test_ci_run_metadata_import_golden.py
docs/fixtures/09-ci-run-metadata-import-golden.md
frontend/src/api/cicd.ts
frontend/src/views/cicd/CicdQualityCenterView.vue
frontend/src/views/cicd/CicdQualityCenterView.spec.ts
```

Completion gate task. User approved development after the V2 document-design
review. Do not add new feature scope, migrations, remote CI provider calls,
webhooks, pipeline triggers, reruns, PR comments, deploy/release controls,
credentials, RBAC, tenants, permissions, marketplace, RAG runtime, or MCP
runtime.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_ci_run_metadata_import.py backend/app/tests/golden/test_ci_run_metadata_import_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

Expected result: Slice 20 backend, golden, frontend, and diff checks pass.

## Acceptance

- Runs Slice 20 API and golden tests.
- Runs the frontend test suite.
- Confirms `git diff --check` is clean.
- Updates Slice 20 task table with Task 6 commit.
- Marks Slice 20 completion gate done pending commit.
- Selects the next V2 task or slice without expanding remote CI/provider scope.

## Commit Message

```text
docs(v2): complete ci metadata import slice
```

## Next Task

Select the next V2 small slice after Slice 20 completion.
