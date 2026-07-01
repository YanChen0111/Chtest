# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 28: CI/CD Quality Gate Evidence Summary.

## Current Task

Slice 28 Task 2: Define quality gate evidence summary contract.

## Product Value Answer

After this task, contracts define how the CI/CD quality gate evidence summary
is derived from existing QualityGateDecision and Artifact evidence without
changing gate computation.

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
14. `docs/implementation/slices/slice-28-cicd-quality-gate-evidence-summary.md`
15. `memory/08-session-handoff.md`
16. `memory/07-dev-log.md`

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
docs/implementation/slices/slice-28-cicd-quality-gate-evidence-summary.md
docs/contracts/02-api-contract.md
docs/contracts/04-artifact-contract.md
backend/app/tests/golden/test_artifact_access_golden.py
docs/fixtures/12-local-artifact-access-golden.md
backend/app/tests/golden/test_execution_evidence_summary_golden.py
docs/fixtures/13-execution-evidence-summary-golden.md
backend/app/tests/golden/test_ci_imported_artifact_reference_clarity_golden.py
docs/fixtures/14-ci-imported-artifact-reference-clarity-golden.md
```

Contract task. Do not add frontend or backend feature code, migrations, package
upgrades, artifact upload/mutation/delete, cloud storage, external provider
integration, RBAC, tenants, permissions, broad redesign work, report generation
behavior, runner behavior changes, quality gate computation changes, RAG
runtime, or MCP runtime.

## Verification Command

```bash
rg -n "quality gate evidence summary|required evidence|blocking reasons|local artifact" docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-28-cicd-quality-gate-evidence-summary.md
git diff --check
```

Expected result: quality gate evidence summary contract language is
discoverable and diff check passes.

## Acceptance

- API contract defines quality gate evidence summary as a read-only
  presentation derived from existing QualityGateDecision fields.
- Artifact contract states local links are only for persisted local Artifact
  ids and missing evidence remains visible but not downloadable.
- Contract preserves no quality gate computation, report generation, runner,
  remote provider, RBAC, tenant, RAG runtime, or MCP runtime changes.

## Commit Message

```text
docs(v2): define quality gate evidence summary contract
```

## Next Task

Slice 28 Task 3: Add CI/CD quality gate frontend summary.
