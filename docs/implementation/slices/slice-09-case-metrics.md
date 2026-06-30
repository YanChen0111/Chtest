# Slice 09: Case Metrics Task Plan

## Goal

Make AI case generation quality measurable for the requirement-to-case mainline.

This slice must calculate and expose batch-level case generation review metrics
from existing CaseGenerationTask, GeneratedCaseCandidate, and TestCase records.
It must not add Test Case Library workflows, AutomationDraft, execution,
reports, CI/CD quality, RAG runtime, MCP runtime, RBAC, tenants, or permissions.

## Source Documents

- `docs/product/04-ai-quality-metrics.md`
- `docs/fixtures/01-golden-requirement-to-case.md`
- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/implementation/02-v1-slice-plan.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/slices/slice-06-requirement-to-case.md`

## Preconditions

- Slice 06 Requirement To Case Mainline is complete.
- CaseGenerationTask and GeneratedCaseCandidate records exist.
- Case Review API can set approved, approved_after_edit, rejected, and
  needs_optimization candidate states.
- TestCase records are created only after approved or approved_after_edit review
  actions.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Case Metrics backend calculation | done | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_metrics.py -q` | `470fa23` | generated_count, approved_count, rejected_count, acceptance_rate, edit_rate, review_progress |
| Add Case Metrics API | done | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_metrics.py -q` | pending commit | batch endpoint for CaseGenerationTask metrics |
| Add Case Metrics frontend shell | planned | `npm --prefix frontend run test -- --run` | - | metric strip and review progress for generated batch |
| Add Case Metrics golden smoke | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_requirement_to_case_metrics.py -q` | - | fixture-aligned metric assertions |

## Task 1: Add Case Metrics Backend Calculation

Goal: Add a service-level calculation for case generation batch quality metrics
using existing persisted records.

Expected files:

- `backend/app/modules/cases/service.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/tests/api/test_case_metrics.py`

Required metrics:

- `generated_count`
- `approved_count`
- `edited_count`
- `rejected_count`
- `optimization_count`
- `reviewed_count`
- `acceptance_rate`
- `edit_rate`
- `rejection_rate`
- `optimization_rate`
- `review_progress`
- `field_complete_rate`

Verification command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_metrics.py -q
```

Non-goals:

- Do not create a new metric table unless calculation from existing records is
  insufficient.
- Do not add prompt/model/skill aggregation in this task.
- Do not add Test Case Library, AutomationDraft, execution, reports, CI/CD, RAG
  runtime, or MCP runtime.

Commit message:

```text
feat(cases): add case metrics calculation
```

## Task 2: Add Case Metrics API

Goal: Expose batch quality metrics for a CaseGenerationTask.

Expected files:

- `backend/app/modules/cases/router.py`
- `backend/app/modules/cases/service.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/tests/api/test_case_metrics.py`

API shape:

```text
GET /api/case-generation/tasks/{generation_task_id}/metrics
```

Response must include the metrics from Task 1 and enough identifiers for the
frontend to display which batch is being measured.

Verification command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_metrics.py -q
```

Non-goals:

- Do not expose global dashboards or cross-project aggregation.
- Do not include execution_pass_rate until execution slices exist.
- Do not add frontend in this task.

Commit message:

```text
feat(cases): add case metrics api
```

## Task 3: Add Case Metrics Frontend Shell

Goal: Show case generation batch quality metrics in the existing frontend
workbench style.

Expected files:

- `frontend/src/api/cases.ts`
- `frontend/src/stores/cases.ts`
- `frontend/src/views/cases/CaseGenerationReviewView.vue`
- `frontend/src/views/cases/CaseGenerationReviewView.spec.ts`

Verification command:

```bash
npm --prefix frontend run test -- --run
```

Non-goals:

- Do not create a broad dashboard route.
- Do not add charts that require new dependencies.
- Do not add Test Case Library or AutomationDraft entry points.

Commit message:

```text
feat(frontend): show case generation metrics
```

## Task 4: Add Case Metrics Golden Smoke

Goal: Assert the golden requirement-to-case fixture can calculate stable batch
metrics after the expected review actions.

Expected files:

- `backend/app/tests/golden/test_requirement_to_case_metrics.py`

Verification command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_requirement_to_case_metrics.py -q
```

Acceptance:

- `generated_count` is at least 5.
- `approved_count` is 3 for the golden review plan.
- `edited_count` is 1.
- `optimization_count` is 1.
- `review_progress` is at least 1.0 for the reviewed golden batch.
- `acceptance_rate` includes approved and approved_after_edit candidates.

Non-goals:

- Do not add browser automation.
- Do not add execution, AutomationDraft, reports, CI/CD quality, RAG runtime, or
  MCP runtime.

Commit message:

```text
test(golden): add case metrics smoke
```

## Slice Completion Gate

- Case generation batch metrics can be calculated from persisted records.
- Metrics API returns generated_count, approved_count, rejected_count,
  acceptance_rate, edit_rate, and review_progress.
- Frontend can show batch metrics without a broad dashboard.
- Golden fixture metric smoke passes.
- No AutomationDraft, execution, reports, CI/CD quality, RAG runtime, MCP
  runtime, RBAC, tenants, or permissions are added.
