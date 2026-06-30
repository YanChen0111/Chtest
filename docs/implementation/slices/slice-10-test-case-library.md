# Slice 10: Test Case Library Task Plan

## Goal

Make reviewed TestCase records visible and reusable as the next handoff point
from requirement-to-case into automation drafting.

This slice must stay limited to browsing/searching existing reviewed TestCase
records and the minimum suite grouping needed by contracts or current models.
It must not add AutomationDraft generation, execution, reports, CI/CD quality,
RAG runtime, MCP runtime, RBAC, tenants, or permissions.

## Source Documents

- `docs/product/01-positioning-and-scope.md`
- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/implementation/02-v1-slice-plan.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/slices/slice-06-requirement-to-case.md`
- `docs/implementation/slices/slice-09-case-metrics.md`

## Preconditions

- Slice 06 Requirement To Case Mainline is complete.
- Slice 09 Case Metrics is complete.
- Reviewed TestCase records are created only after approved or
  approved_after_edit Case Review actions.
- TestCase is already defined in the data model contract.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Test Case Library API contract and task boundary | planned | `rg -n "Test Case Library|GET /api/test-cases|TestCaseList" docs/contracts/02-api-contract.md docs/implementation/slices/slice-10-test-case-library.md` | - | contract-first endpoint shape |
| Add Test Case Library backend API | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_test_case_library.py -q` | - | list reviewed TestCase records by project/module/status |
| Add Test Case Library frontend shell | planned | `npm --prefix frontend run test -- --run` | - | compact searchable library view |
| Add Test Case Library golden smoke | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_case_library.py -q` | - | reviewed golden cases appear in library |
| Slice 10 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_test_case_library.py backend/app/tests/golden/test_test_case_library.py -q && npm --prefix frontend run test -- --run` | - | docs and handoff only |

## Task 1: Add Test Case Library API Contract And Task Boundary

Goal: Define the minimal Test Case Library API and freeze Slice 10 scope before
implementation.

Expected files:

- `docs/contracts/02-api-contract.md`
- `docs/implementation/slices/slice-10-test-case-library.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "Test Case Library|GET /api/test-cases|TestCaseList" docs/contracts/02-api-contract.md docs/implementation/slices/slice-10-test-case-library.md
```

Acceptance:

- Contract defines `GET /api/test-cases` for reviewed TestCase browsing.
- Response includes id, project_id, module_id, source_candidate_id, title,
  priority, test_type, precondition, steps, expected_results, input_data, tags,
  source_type, review_status, and status.
- Contract names query filters for project_id, module_id, status, test_type,
  priority, and keyword.
- No AutomationDraft, execution, report, CI/CD quality, RAG runtime, MCP
  runtime, RBAC, tenant, or permission API is added.

Commit message:

```text
docs(cases): define test case library api
```

## Task 2: Add Test Case Library Backend API

Goal: Expose reviewed TestCase records through the minimal library API.

Expected files:

- `backend/app/modules/cases/router.py`
- `backend/app/modules/cases/service.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/tests/api/test_test_case_library.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_test_case_library.py -q
```

Acceptance:

- `GET /api/test-cases` returns only persisted TestCase records, not generated
  candidates.
- Supports project_id filtering and optional module_id, status, test_type,
  priority, and keyword filters.
- Results are deterministic, ordered by created_at then id.
- Response includes `items` and `total`.
- Unknown project_id returns the existing project-not-found style contract
  error when applicable.

Non-goals:

- Do not create TestCase records outside Case Review.
- Do not add mutation APIs for manual case authoring in this task.
- Do not add suite execution, AutomationDraft, reports, or metrics.

Commit message:

```text
feat(cases): add test case library api
```

## Task 3: Add Test Case Library Frontend Shell

Goal: Let users browse reviewed TestCase records from the workbench.

Expected files:

- `frontend/src/api/cases.ts`
- `frontend/src/stores/cases.ts`
- `frontend/src/views/cases/TestCaseLibraryView.vue`
- `frontend/src/views/cases/TestCaseLibraryView.spec.ts`
- `frontend/src/router/index.ts`
- `frontend/src/layouts/WorkbenchLayout.vue`

Verification Command:

```bash
npm --prefix frontend run test -- --run
```

Acceptance:

- Adds a workbench navigation entry for Test Case Library.
- Shows a compact searchable/filterable list of reviewed cases.
- Shows selected case title, priority, type, status, steps, expected results,
  tags, and review/source metadata.
- Does not add AutomationDraft buttons, execution buttons, reports, broad
  dashboard widgets, or chart dependencies.

Commit message:

```text
feat(frontend): add test case library shell
```

## Task 4: Add Test Case Library Golden Smoke

Goal: Prove golden reviewed cases are visible through the library API after the
requirement-to-case review plan.

Expected files:

- `backend/app/tests/golden/test_test_case_library.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_case_library.py -q
```

Acceptance:

- Reuses the golden requirement-to-case fixture setup and review plan.
- Asserts the library returns 4 reviewed TestCase records after review.
- Asserts the edited expired-coupon case keeps the edited step and input data.
- Asserts keyword filtering can find a golden case by title or requirement text.

Non-goals:

- Do not add browser automation.
- Do not add AutomationDraft, execution, reports, CI/CD quality, RAG runtime, or
  MCP runtime.

Commit message:

```text
test(golden): add test case library smoke
```

## Slice Completion Gate

- TestCase Library API contract exists.
- Backend library API returns reviewed TestCase records with filters.
- Frontend shell can browse reviewed cases without automation/execution actions.
- Golden fixture smoke proves reviewed cases enter the library.
- No AutomationDraft, execution, reports, CI/CD quality, RAG runtime, MCP
  runtime, RBAC, tenants, or permissions are added.
