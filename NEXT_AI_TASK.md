# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 09: Case Metrics.

## Current Task

Task 5: Add Case Metrics golden smoke.

## Product Value Answer

After this task, Chtest can prove the golden requirement-to-case fixture
produces stable batch-level case generation metrics after review actions.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-09-case-metrics.md`
3. `docs/product/04-ai-quality-metrics.md`
4. `docs/fixtures/01-golden-requirement-to-case.md`
5. `backend/app/tests/golden/test_requirement_to_case.py`
6. `backend/app/modules/cases/service.py`
7. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Frontend, AutomationDraft, execution, Playwright, CI/CD, report center, RAG
  runtime, MCP runtime, and migration reference docs unless a concrete blocker
  requires them.

## Expected Files

Create or update only these files for the current task:

```text
backend/app/tests/golden/test_requirement_to_case_metrics.py
```

Read the existing golden requirement-to-case smoke only as needed to reuse its
fixture setup and review pattern.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_requirement_to_case_metrics.py -q
```

Expected result: golden metrics smoke passes.

## Acceptance

- Add a fixture-aligned golden smoke for case metrics.
- Assert generated_count is at least 5.
- Assert approved_count is 3, edited_count is 1, and optimization_count is 1 for
  the golden review plan.
- Assert review_progress is at least 1.0 after the reviewed golden batch.
- Assert acceptance_rate includes approved and approved_after_edit candidates.
- Do not add browser automation, frontend, execution, AutomationDraft, reports,
  CI/CD quality, RAG runtime, MCP runtime, RBAC, tenants, or permissions.
- `git status --short` shows only the expected golden test file and required
  task docs before commit.

## Commit Message

```text
test(golden): add case metrics smoke
```

## Next Task

Slice 09 completion gate.
