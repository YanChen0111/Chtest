# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 26: CI Imported Artifact Reference Clarity.

## Current Task

Slice 26 Completion Gate.

## Product Value Answer

After this task, Slice 26 is fully verified and handed off with imported
external artifact references clearly marked as inert, not locally openable, and
free of remote-provider side effects.

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
13. recent session handoff and dev log

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
docs/contracts/02-api-contract.md
docs/contracts/04-artifact-contract.md
backend/app/tests/golden/test_artifact_access_golden.py
docs/fixtures/12-local-artifact-access-golden.md
backend/app/tests/golden/test_execution_evidence_summary_golden.py
docs/fixtures/13-execution-evidence-summary-golden.md
backend/app/tests/golden/test_ci_imported_artifact_reference_clarity_golden.py
docs/fixtures/14-ci-imported-artifact-reference-clarity-golden.md
```

Completion gate task. Do not add frontend or backend feature code, migrations,
package upgrades, artifact upload/mutation/delete, cloud storage, external
provider integration, RBAC, tenants, permissions, broad redesign work, report
generation behavior, or runner behavior changes.

## Verification Command

```bash
npm --prefix frontend run build
npm --prefix frontend run test -- --run
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_ci_imported_artifact_reference_clarity_golden.py backend/app/tests/golden/test_artifact_access_golden.py -q
git diff --check
```

Expected result: Slice 26 frontend checks, artifact golden checks, and diff
check pass.

## Acceptance

- Slice 26 task table records Task 1-4 completion and commit ids.
- Completion evidence records frontend build/test, golden checks, and diff
  verification.
- Imported external artifact references remain inert, not locally openable,
  and not remotely fetched.
- No TestRun, Report, FailureAnalysis, QualityGateDecision, or remote-provider
  side effect is created by import-only metadata.

## Commit Message

```text
docs(v2): complete ci imported reference clarity slice
```

## Next Task

Select next V2 small slice after Slice 26 completion.
