# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 09: Case Metrics.

## Current Task

Task 4: Add Case Metrics frontend shell.

## Product Value Answer

After this task, Chtest can show batch-level case generation quality metrics in
the existing Case Generation Review frontend shell.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-09-case-metrics.md`
3. `docs/product/04-ai-quality-metrics.md`
4. `frontend/src/views/cases/CaseGenerationReviewView.vue`
5. `frontend/src/api/cases.ts`
6. `frontend/src/stores/cases.ts`
7. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- AutomationDraft, execution, Playwright, CI/CD, report center, RAG runtime,
  MCP runtime, and migration reference docs unless a concrete blocker requires
  them.

## Expected Files

Create or update only these files for the current task:

```text
frontend/src/api/cases.ts
frontend/src/stores/cases.ts
frontend/src/views/cases/CaseGenerationReviewView.vue
frontend/src/views/cases/CaseGenerationReviewView.spec.ts
```

Read existing cases frontend shell only as needed to add a compact metrics strip.

## Verification Command

```bash
npm --prefix frontend run test -- --run
```

Expected result: frontend test suite passes.

## Acceptance

- Add frontend API/store wiring for `GET /api/case-generation/tasks/{id}/metrics`.
- Show generated_count, approved_count, rejected_count, acceptance_rate,
  edit_rate, review_progress, and field_complete_rate in the Case Generation
  Review shell.
- Keep the shell compact; do not create a broad dashboard route or add chart
  dependencies.
- Do not add Test Case Library, AutomationDraft, execution, reports, CI/CD, RAG
  runtime, MCP runtime, RBAC, tenants, or permissions.
- `git status --short` shows only expected frontend files and required task docs
  before commit.

## Commit Message

```text
feat(frontend): show case generation metrics
```

## Next Task

Slice 09 Task 5: Add Case Metrics golden smoke.
