# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 11: AutomationDraft Foundation.

## Current Task

Task 5: Add AutomationDraft frontend review shell.

## Product Value Answer

After this task, Chtest can review, edit, and approve AutomationDraft records
from the frontend workbench without execution actions.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/02-v1-slice-plan.md`
3. `docs/product/01-positioning-and-scope.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/implementation/slices/slice-11-automation-draft-foundation.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Execution, Playwright, CI/CD, report center, RAG runtime, MCP runtime, and
  migration reference docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
frontend/src/api/automation.ts
frontend/src/stores/automation.ts
frontend/src/views/automation/AutomationDraftReviewView.vue
frontend/src/views/automation/AutomationDraftReviewView.spec.ts
frontend/src/router/index.ts
frontend/src/layouts/WorkbenchLayout.vue
frontend/src/stores/index.ts
docs/implementation/slices/slice-11-automation-draft-foundation.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
```

Read existing frontend shell patterns as needed, but do not add execution/run
buttons or backend behavior in this task.

## Verification Command

```bash
npm --prefix frontend run test -- --run
```

Expected result: frontend test suite passes.

## Acceptance

- Add frontend API/store wiring for AutomationDraft create, get, edit, and
  approve.
- Add workbench navigation for AutomationDraft review.
- Show draft code, suggested path, execution notes, risk notes, status, and
  approval_required.
- Support edit and approve actions through the API.
- Do not add execution/run buttons, report links, CI/CD quality actions, RAG
  runtime, MCP runtime, RBAC, tenants, or permissions.
- Update handoff and set the next task to golden smoke.

## Commit Message

```text
feat(frontend): add automation draft review shell
```

## Next Task

Slice 11 Task 6: Add AutomationDraft golden smoke.
