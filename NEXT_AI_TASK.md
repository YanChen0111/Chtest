# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Select the next V2 small slice.

## Current Task

Select the next V2 small slice after Slice 23 completion.

## Product Value Answer

After this task, the next small V2 task is selected with a narrow product value,
non-goals, expected files, verification command, and commit scope.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`
8. `docs/implementation/10-v2-scope-options.md`
9. recent session handoff and dev log

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud CI/provider integration, RBAC, tenants,
  permissions, and frontend redesign docs unless a concrete blocker requires
  them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
docs/implementation/slices/slice-22-jmeter-local-execution.md
docs/implementation/10-v2-scope-options.md
docs/implementation/slices/slice-23-frontend-build-baseline.md
frontend/src/api/client.ts
frontend/src/api/automation.ts
frontend/src/api/cases.ts
frontend/src/api/cicd.ts
frontend/src/api/execution.ts
frontend/src/api/reporting.ts
frontend/src/api/requirements.ts
frontend/src/views/ai-workbench/AiWorkbenchView.vue
frontend/src/views/cicd/CicdQualityCenterView.vue
frontend/src/views/requirements/RequirementReviewView.vue
```

Planning task. Do not add product code, backend code, frontend code, migrations,
package upgrades, redesign work, or tests. Do not start a broad V2 platform
expansion.

## Verification Command

```bash
rg -n "V2|Next|small slice|Candidate|Frontend Build Baseline|Slice 23" docs/implementation/10-v2-scope-options.md docs/implementation/slices/slice-23-frontend-build-baseline.md NEXT_AI_TASK.md
git diff --check
```

Expected result: next V2 planning keywords are present and diff check passes.

## Acceptance

- Slice 23 remains closed.
- Next task is selected as a small, verifiable V2 slice or planning item.
- Product value, non-goals, expected files, verification command, and commit
  message are explicit.
- No product code is changed.

## Commit Message

```text
docs(v2): select next small slice
```

## Next Task

Start the selected V2 task.
