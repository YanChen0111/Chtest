# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 10: Test Case Library.

## Current Task

Task 4: Add Test Case Library frontend shell.

## Product Value Answer

After this task, Chtest can browse reviewed TestCase records from the frontend
workbench without adding automation or execution actions.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/02-v1-slice-plan.md`
3. `docs/product/01-positioning-and-scope.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/implementation/slices/slice-10-test-case-library.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- AutomationDraft, execution, Playwright, CI/CD, report center, RAG runtime,
  MCP runtime, and migration reference docs unless a concrete blocker requires
  them.

## Expected Files

Create or update only these files for the current task:

```text
docs/implementation/slices/slice-10-test-case-library.md
frontend/src/api/cases.ts
frontend/src/stores/cases.ts
frontend/src/views/cases/TestCaseLibraryView.vue
frontend/src/views/cases/TestCaseLibraryView.spec.ts
frontend/src/router/index.ts
frontend/src/layouts/WorkbenchLayout.vue
NEXT_AI_TASK.md
memory/08-session-handoff.md
```

Read existing frontend cases/requirements shells as needed, but keep writes
inside the files above unless a concrete blocker requires an explained
contract/doc update.

## Verification Command

```bash
npm --prefix frontend run test -- --run
```

Expected result: frontend test suite passes.

## Acceptance

- Add frontend API/store wiring for `GET /api/test-cases`.
- Add a workbench navigation entry for Test Case Library.
- Show a compact searchable/filterable list of reviewed cases.
- Show selected case title, priority, type, status, steps, expected results,
  tags, and review/source metadata.
- Do not add AutomationDraft buttons, execution buttons, reports, broad
  dashboard widgets, chart dependencies, RAG runtime, MCP runtime, RBAC,
  tenants, or permissions.
- Update handoff and set the next task to golden smoke.

## Commit Message

```text
feat(frontend): add test case library shell
```

## Next Task

Slice 10 Task 5: Add Test Case Library golden smoke.
