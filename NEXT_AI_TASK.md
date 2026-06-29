# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 09: Case Metrics.

## Current Task

Task 3: Add Case Metrics API.

## Product Value Answer

After this task, Chtest can expose batch-level case generation quality metrics
through a backend API for frontend display.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-09-case-metrics.md`
3. `docs/product/04-ai-quality-metrics.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- AutomationDraft, execution, Playwright, CI/CD, report center, RAG runtime,
  MCP runtime, and migration reference docs unless a concrete blocker requires
  them.

## Expected Files

Create or update only these files for the current task:

```text
docs/implementation/slices/slice-06-requirement-to-case.md
backend/app/modules/cases/service.py
backend/app/modules/cases/router.py
backend/app/modules/cases/schemas.py
backend/app/tests/api/test_case_metrics.py
```

Read existing Case Generation and Case Review tests only as needed to reuse
fixtures and request patterns.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_metrics.py -q
```

Expected result: Case Metrics focused test passes.

## Acceptance

- Add `GET /api/case-generation/tasks/{generation_task_id}/metrics`.
- Return generated_count, approved_count, edited_count, rejected_count,
  optimization_count, reviewed_count, acceptance_rate, edit_rate,
  rejection_rate, optimization_rate, review_progress, and field_complete_rate.
- Reuse the service calculation from Task 2.
- Do not add frontend, Test Case Library, AutomationDraft, execution, reports,
  CI/CD, RAG runtime, MCP runtime, RBAC, tenants, or permissions.
- `git status --short` shows only expected cases router/service/schema/test files
  and required task docs before commit.

## Commit Message

```text
feat(cases): add case metrics api
```

## Next Task

Slice 09 Task 4: Add Case Metrics frontend shell.
