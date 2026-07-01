# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 20: CI Run Metadata Import.

## Current Task

Slice 20 Task 5: Add CI import frontend evidence display.

## Product Value Answer

After this task, CI/CD 管理 can show imported CI run evidence, imported
changed files, and inert artifact references without exposing remote provider
controls.

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
frontend/src/api/extension.ts
frontend/src/stores/extensionStore.ts
frontend/src/views/CICDQualityCenterView.vue
frontend/src/**/*.test.*
```

Frontend display task. User approved development after the V2 document-design
review. Do not add remote CI provider calls, webhooks, pipeline triggers,
reruns, PR comments, deploy/release controls, credentials, RBAC, tenants,
permissions, marketplace, RAG runtime, or MCP runtime.

## Verification Command

```bash
npm --prefix frontend run test -- --run
git diff --check
```

Expected result: CI import frontend evidence display tests and diff check pass.

## Acceptance

- Shows imported CI evidence on CI/CD 管理 without remote provider controls.
- Displays imported provider label, import status, CI conclusion, refs, changed
  file count, and inert artifact references when available.
- Keeps QualityGateDecision and local review workflow visually separate from
  imported CI conclusion.
- Does not expose trigger, rerun, cancel, schedule, PR comment, deploy, release,
  credential, webhook, or remote-fetch controls.

## Commit Message

```text
feat(frontend): show ci import evidence
```

## Next Task

Slice 20 Task 6: Add CI import golden smoke.
