# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 26: CI Imported Artifact Reference Clarity.

## Current Task

Slice 26 Task 2: Define imported artifact reference display contract.

## Product Value Answer

After this task, imported external artifact references have an explicit display
contract before frontend clarity or golden smoke work begins.

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
```

Contract task. Do not add frontend code, backend feature code, migrations,
package upgrades, artifact upload/mutation/delete, cloud storage, external
provider integration, RBAC, tenants, permissions, broad redesign work, report
generation behavior, or runner behavior changes.

## Verification Command

```bash
rg -n "imported artifact reference|inert reference|remote_fetch_performed|not locally openable" docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-26-ci-imported-artifact-reference-clarity.md
git diff --check
```

Expected result: imported artifact reference display contract text is present
and diff check passes.

## Acceptance

- API contract states imported artifact references are display-only external
  references, not local Artifact files.
- Artifact contract states external references must show inert/not-local status
  and must not receive local download links.
- Contract preserves `remote_fetch_performed=false` and external-provider
  non-goals.

## Commit Message

```text
docs(v2): define imported reference clarity contract
```

## Next Task

Slice 26 Task 3: Add CI imported reference frontend clarity.
