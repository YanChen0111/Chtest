# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 27: AI Task Evidence Artifact Links.

## Current Task

Slice 27 Task 3: Add AI Workbench artifact links.

## Product Value Answer

After this task, the AI Workbench shows local open links for safe AI task
evidence artifacts and keeps unsafe raw LLM artifacts metadata-only.

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
12. `docs/implementation/slices/slice-26-ci-imported-artifact-reference-clarity.md`
13. `docs/implementation/slices/slice-27-ai-task-evidence-artifact-links.md`
14. `memory/08-session-handoff.md`
15. `memory/07-dev-log.md`

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
docs/implementation/slices/slice-26-ci-imported-artifact-reference-clarity.md
docs/implementation/slices/slice-27-ai-task-evidence-artifact-links.md
docs/contracts/02-api-contract.md
docs/contracts/04-artifact-contract.md
backend/app/tests/golden/test_artifact_access_golden.py
docs/fixtures/12-local-artifact-access-golden.md
backend/app/tests/golden/test_execution_evidence_summary_golden.py
docs/fixtures/13-execution-evidence-summary-golden.md
backend/app/tests/golden/test_ci_imported_artifact_reference_clarity_golden.py
docs/fixtures/14-ci-imported-artifact-reference-clarity-golden.md
```

Frontend task. Do not add backend feature code, migrations, package upgrades,
artifact upload/mutation/delete, cloud storage, external provider integration,
RBAC, tenants, permissions, broad redesign work, report generation behavior,
runner behavior changes, AI task rerun, prompt editing, raw LLM inline display,
RAG runtime, or MCP runtime.

## Verification Command

```bash
npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts
npm --prefix frontend run build
git diff --check
```

Expected result: AI Workbench focused test, frontend build, and diff check pass.

## Acceptance

- Safe local AI task artifacts show an "打开" link.
- Unsafe artifacts such as raw LLM output remain visible as metadata and show a
  not-openable status.
- LLM call logs still cite request/response/parsed artifact ids without
  inlining artifact contents.
- Page still excludes rerun, provider control, prompt editing, raw content, and
  remote runtime controls.

## Commit Message

```text
feat(frontend): link safe ai task artifacts
```

## Next Task

Slice 27 Task 4: Add AI task artifact link golden smoke.
