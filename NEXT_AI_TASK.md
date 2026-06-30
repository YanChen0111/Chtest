# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 09: Case Metrics.

## Current Task

Slice 09 completion gate.

## Product Value Answer

After this task, Chtest can prove the Case Metrics slice is complete across
backend calculation, API, frontend shell, and golden fixture coverage.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-09-case-metrics.md`
3. `docs/product/04-ai-quality-metrics.md`
4. `docs/fixtures/01-golden-requirement-to-case.md`
5. `docs/implementation/02-v1-slice-plan.md`
6. `memory/08-session-handoff.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Frontend, AutomationDraft, execution, Playwright, CI/CD, report center, RAG
  runtime, MCP runtime, and migration reference docs unless a concrete blocker
  requires them.

## Expected Files

Create or update only these files for the current task:

```text
docs/implementation/slices/slice-09-case-metrics.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
```

Do not modify product code unless the completion verification exposes a concrete
bug.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_metrics.py backend/app/tests/golden/test_requirement_to_case.py backend/app/tests/golden/test_requirement_to_case_metrics.py -q
npm --prefix frontend run test -- --run
```

Expected result: Case Metrics backend/golden tests and frontend test suite pass.

## Acceptance

- Confirm the Slice 09 task table has commit IDs for every completed task.
- Confirm case metrics can be calculated from persisted records.
- Confirm metrics API returns generated_count, approved_count, rejected_count,
  acceptance_rate, edit_rate, and review_progress.
- Confirm frontend can show batch metrics without a broad dashboard.
- Confirm golden fixture metric smoke passes.
- Do not add AutomationDraft, execution, reports, CI/CD quality, RAG runtime,
  MCP runtime, RBAC, tenants, or permissions.
- Update handoff with completion evidence and next recommended slice/task.

## Commit Message

```text
docs(metrics): complete case metrics slice
```

## Next Task

Select the next smallest V1 task from `docs/implementation/02-v1-slice-plan.md`.
